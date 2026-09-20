"""Small, review-only clinical text parser used for the Week 3 prototype."""
import re


CONDITIONS = (
    "diabetes mellitus", "type 1 diabetes", "type 2 diabetes", "hypertension",
    "asthma", "copd", "pneumonia", "migraine", "anemia", "hypothyroidism",
    "hyperthyroidism", "heart failure", "coronary artery disease", "stroke",
    "chronic kidney disease", "kidney disease", "depression", "arthritis",
)
MEDICATIONS = (
    "metformin", "insulin", "lisinopril", "amlodipine", "atorvastatin",
    "aspirin", "paracetamol", "acetaminophen", "ibuprofen", "omeprazole",
    "levothyroxine", "salbutamol", "albuterol", "amoxicillin", "azithromycin",
)
LAB_NAMES = "HbA1c|Hemoglobin|WBC|Platelets|Glucose|Creatinine|Urea|Sodium|Potassium|Cholesterol|LDL|HDL|Triglycerides|TSH"
EVENT_WORDS = "admitted|discharged|hospitalized|surgery|follow-up|follow up|referred|diagnosis|complaint"


def _unique(items):
    seen = set()
    return [item for item in items if not (item["text"].lower() in seen or seen.add(item["text"].lower()))]


def extract_clinical_entities(text: str | None) -> dict:
    """Return conservative regex matches for clinician review; never a diagnosis."""
    text = text or ""
    conditions = [{"type": "condition", "text": match.group(0), "confidence": "possible"}
                  for name in CONDITIONS if (match := re.search(rf"\b{re.escape(name)}\b", text, re.I))]
    medications = [{"type": "medication", "text": match.group(0), "confidence": "possible"}
                   for name in MEDICATIONS if (match := re.search(rf"\b{re.escape(name)}\b", text, re.I))]
    labs = []
    for match in re.finditer(rf"\b({LAB_NAMES})\b\s*[:=\-]?\s*(\d+(?:\.\d+)?)\s*(%|mg/dL|mmol/L|g/dL|mEq/L|/uL|cells/uL)?", text, re.I):
        labs.append({"type": "lab_value", "text": match.group(0), "name": match.group(1), "value": match.group(2), "unit": match.group(3) or "", "confidence": "possible"})
    events = [{"type": "clinical_event", "text": match.group(0), "confidence": "possible"}
              for match in re.finditer(rf"\b(?:{EVENT_WORDS})\b[^.\n]*", text, re.I)]
    dates = [{"type": "date", "text": match.group(0), "confidence": "possible"}
             for match in re.finditer(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b", text, re.I)]
    return {"conditions": _unique(conditions), "medications": _unique(medications), "lab_values": _unique(labs), "clinical_events": _unique(events), "dates": _unique(dates)}
