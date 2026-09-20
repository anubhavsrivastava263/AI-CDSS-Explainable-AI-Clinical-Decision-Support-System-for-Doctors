"""Local, retrieval-only guideline search. It does not generate clinical advice."""
import json
import logging
import re
from pathlib import Path

import faiss
import httpx
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

from app.core.config import settings

logger = logging.getLogger("rag_retrieval")
logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = ROOT / "rag" / "documents"
INDEX_DIR = ROOT / settings.VECTOR_DB_PATH.lstrip("./")
INDEX_FILE = INDEX_DIR / "guidelines.faiss"
META_FILE = INDEX_DIR / "guidelines.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _chunks(text: str, size: int = 700, overlap: int = 120):
    text = re.sub(r"\s+", " ", text).strip()
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            end = boundary + 1 if boundary > start + size // 2 else end
        yield text[start:end]
        if end == len(text):
            break
        start = end - overlap


def _document_chunks():
    chunks = []
    for path in sorted(DOCS_DIR.glob("**/*")):
        if path.suffix.lower() not in {".md", ".txt"} or path.name == "README.md":
            continue
        raw = path.read_text(encoding="utf-8")
        title = next((line[2:].strip() for line in raw.splitlines() if line.startswith("# ")), path.stem)
        url_match = re.search(r"Source:\s*(https?://\S+)", raw, re.I)
        section = title
        for part in re.split(r"(?=^## )", raw, flags=re.M):
            section_match = re.search(r"^##\s+(.+)$", part, re.M)
            section = section_match.group(1).strip() if section_match else title
            clean = re.sub(r"^#.*$|^Source:\s*.*$", "", part, flags=re.M).strip()
            for text in _chunks(clean):
                if text:
                    chunks.append({"source": title, "source_url": url_match.group(1) if url_match else None,
                                   "section": section, "text": text})
    return chunks


def _embed(texts: list[str], mode: str | None = None):
    if mode != "hashing":
        try:
            from sentence_transformers import SentenceTransformer
            # Do not make a server request wait on a model download. The model
            # is cached during setup; otherwise the deterministic fallback is used.
            model = SentenceTransformer(MODEL_NAME, local_files_only=True)
            vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(vectors, dtype="float32"), "sentence-transformers/all-MiniLM-L6-v2"
        except (ImportError, OSError, RuntimeError):
            pass
    vectors = HashingVectorizer(n_features=384, alternate_sign=False, norm="l2", stop_words="english").transform(texts)
    return vectors.toarray().astype("float32"), "hashing fallback (install sentence-transformers for semantic embeddings)"


def rebuild_index():
    chunks = _document_chunks()
    if not chunks:
        raise ValueError("No .md or .txt guideline documents are available in rag/documents.")
    vectors, mode = _embed([chunk["text"] for chunk in chunks])
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(INDEX_FILE))
    META_FILE.write_text(json.dumps({"embedding_mode": mode, "chunks": chunks}, indent=2), encoding="utf-8")
    return {"documents": len({c["source"] for c in chunks}), "chunks": len(chunks), "embedding_mode": mode}


def search(query: str, limit: int):
    if not INDEX_FILE.exists() or not META_FILE.exists():
        rebuild_index()
    metadata = json.loads(META_FILE.read_text(encoding="utf-8"))
    mode = metadata["embedding_mode"]
    vectors, _ = _embed([query], "hashing" if mode.startswith("hashing") else None)
    index = faiss.read_index(str(INDEX_FILE))
    scores, ids = index.search(vectors, min(limit, index.ntotal))
    results = []
    for score, item_id in zip(scores[0], ids[0]):
        if item_id >= 0:
            results.append({**metadata["chunks"][int(item_id)], "score": round(float(score), 4)})
    return {"query": query, "embedding_mode": mode, "results": results}


def _extractive_evidence_summary(evidence: list[dict]) -> str:
    """Return cited source text without adding facts or clinical advice."""
    excerpts = []
    for index, item in enumerate(evidence[:2], start=1):
        text = re.sub(r"\s+", " ", item["text"]).strip()
        if text:
            excerpts.append(f"[{index}] {text}")
    return "\n\n".join(excerpts)


def answer(question: str, limit: int):
    """Generate a constrained explanation from evidence, never from model memory."""
    logger.info("answer(): query=%r limit=%s", question, limit)

    retrieved = search(question, limit)
    evidence = retrieved["results"]
    top_score = evidence[0]["score"] if evidence else None
    logger.info("answer(): retrieved %d chunk(s), top_score=%s", len(evidence), top_score)

    # A zero/near-zero inner-product result means the local corpus cannot support
    # the question. Do not send such a prompt to an LLM.
    if not evidence or evidence[0]["score"] < 0.12:
        logger.info("answer(): BRANCH=insufficient_evidence (no chunks or top_score < 0.12)")
        return {
            "query": question, "status": "insufficient_evidence", "answer": None,
            "message": "No sufficiently relevant evidence was found in the curated local knowledge base.",
            "provider": None, "model": None, "evidence": evidence,
        }

    provider = settings.LLM_PROVIDER.strip().lower()
    has_key = bool(settings.LLM_API_KEY)
    has_model = bool(settings.LLM_MODEL)
    logger.info(
        "answer(): LLM config -> provider=%r has_api_key=%s model=%r",
        provider, has_key, settings.LLM_MODEL or None,
    )
    if provider != "openai" or not has_key or not has_model:
        logger.info(
            "answer(): BRANCH=evidence_summary (provider!=openai=%s, missing_key=%s, missing_model=%s). "
            "Check that backend/.env exists, was loaded, and the server was restarted after editing it.",
            provider != "openai", not has_key, not has_model,
        )
        return {
            "query": question,
            "status": "evidence_summary",
            "answer": _extractive_evidence_summary(evidence),
            "message": "Extractive summary from the curated evidence; no external LLM was used.",
            "provider": "local",
            "model": None,
            "evidence": evidence,
        }

    context = "\n\n".join(
        f"[{index}] {item['source']} — {item.get('section') or 'Excerpt'}\n{item['text']}"
        for index, item in enumerate(evidence, start=1)
    )
    instructions = (
        "You are a clinical decision-support writing assistant. Answer only from the supplied evidence. "
        "Do not diagnose, prescribe, calculate risk, or add facts from your own knowledge. "
        "If the evidence does not answer the question, reply exactly: Insufficient evidence in the curated knowledge base. "
        "Use concise prose and cite every factual statement using [1], [2], etc. "
        "End with: Clinician review is required."
    )
    logger.info("answer(): calling OpenAI model=%r with %d evidence chunk(s)", settings.LLM_MODEL, len(evidence))
    try:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}", "Content-Type": "application/json"},
            json={"model": settings.LLM_MODEL, "instructions": instructions,
                  "input": f"Question: {question}\n\nCurated evidence:\n{context}", "store": False},
            timeout=30,
        )
        response.raise_for_status()
        generated = response.json().get("output_text", "").strip()
        logger.info("answer(): OpenAI call succeeded, response length=%d chars", len(generated))
    except httpx.HTTPError as error:
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        body = getattr(getattr(error, "response", None), "text", None)
        logger.warning(
            "answer(): BRANCH=generation_unavailable — OpenAI call failed: %s (status=%s) body=%s",
            error, status_code, body,
        )
        return {
            "query": question, "status": "generation_unavailable", "answer": None,
            "message": "The configured LLM could not generate an evidence-grounded response. Review the retrieved evidence directly.",
            "provider": "openai", "model": settings.LLM_MODEL, "evidence": evidence,
        }

    citations = {int(number) for number in re.findall(r"\[(\d+)\]", generated)}
    if not generated or "Insufficient evidence" in generated or not citations or max(citations) > len(evidence):
        logger.info(
            "answer(): BRANCH=insufficient_evidence (post-LLM) — empty=%s, refused=%s, citations=%s, evidence_count=%d",
            not generated, "Insufficient evidence" in generated, citations, len(evidence),
        )
        return {
            "query": question, "status": "insufficient_evidence", "answer": None,
            "message": "The generated response could not be verified against the retrieved evidence. Review the excerpts below.",
            "provider": "openai", "model": settings.LLM_MODEL, "evidence": evidence,
        }
    logger.info("answer(): BRANCH=answered — citations=%s", citations)
    return {"query": question, "status": "answered", "answer": generated, "message": None,
            "provider": "openai", "model": settings.LLM_MODEL, "evidence": evidence}
