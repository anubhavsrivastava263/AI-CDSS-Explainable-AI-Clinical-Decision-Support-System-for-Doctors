"""Week 7 clinician assistant: controlled evidence plus optional owned record navigation."""
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.patient import Patient
from app.schemas.assistant import AssistantAnswerOut, AssistantQuestion, ClinicalDraftOut, PatientContextOut
from app.services.rag_retrieval import answer as evidence_answer

router = APIRouter(prefix="/assistant", tags=["AI Clinical Assistant"])


def _owned_patient(patient_id: int, db: Session, doctor_id: int) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.doctor_id == doctor_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found")
    return patient


def _record_context(patient: Patient, question: str) -> PatientContextOut:
    terms = {word.lower() for word in re.findall(r"[a-zA-Z]{4,}", question)}
    matches = []
    for report in patient.reports:
        for sentence in re.split(r"(?<=[.!?])\s+", report.extracted_text or ""):
            lowered = sentence.lower()
            if terms and any(term in lowered for term in terms):
                matches.append(f"{report.filename}: {sentence.strip()}")
            if len(matches) == 5:
                break
        if len(matches) == 5:
            break
    return PatientContextOut(
        patient_id=patient.id,
        patient_name=f"{patient.first_name} {patient.last_name}",
        history=[item.condition for item in patient.medical_history[:8]],
        report_matches=matches,
    )


@router.post("/ask", response_model=AssistantAnswerOut)
def ask_assistant(payload: AssistantQuestion, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Answer from curated guideline evidence; record snippets only help the clinician locate source text."""
    try:
        result = evidence_answer(payload.question, payload.limit)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error))
    context = _record_context(_owned_patient(payload.patient_id, db, current_user.id), payload.question) if payload.patient_id else None
    # The shared RAG service names the submitted text `query`; this endpoint
    # exposes it as `question` to match the clinical-assistant API contract.
    return {**result, "question": result["query"], "patient_context": context}


@router.get("/patients/{patient_id}/draft", response_model=ClinicalDraftOut)
def patient_draft(patient_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Produce a transparent deterministic hand-off draft; it never infers findings."""
    patient = _owned_patient(patient_id, db, current_user.id)
    history = "; ".join(item.condition for item in patient.medical_history[:8]) or "No documented conditions."
    reports = [report for report in patient.reports if report.extracted_text]
    snippets = []
    for report in reports[:3]:
        text = re.sub(r"\s+", " ", report.extracted_text).strip()
        if text:
            snippets.append(f"{report.filename}: {text[:280]}{'…' if len(text) > 280 else ''}")
    draft = (
        f"Draft for clinician review — {patient.first_name} {patient.last_name}.\n"
        f"Documented history: {history}\n"
        f"Uploaded reports with extracted text ({len(reports)}): " + (" | ".join(snippets) if snippets else "None available.")
    )
    return {"patient_id": patient.id, "draft": draft, "report_count": len(reports),
            "disclaimer": "Draft compiled from stored records only. Verify the source reports; it is not a diagnosis or prescription."}
