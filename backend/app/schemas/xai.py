from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    time_in_hospital: float = Field(3, ge=1, le=30)
    num_lab_procedures: float = Field(40, ge=0, le=200)
    num_procedures: float = Field(0, ge=0, le=20)
    num_medications: float = Field(12, ge=0, le=100)
    number_outpatient: float = Field(0, ge=0, le=100)
    number_emergency: float = Field(0, ge=0, le=100)
    number_inpatient: float = Field(0, ge=0, le=100)
    number_diagnoses: float = Field(5, ge=1, le=30)


class PredictionOut(BaseModel):
    probability: float
    model_label: str
    increasing_factors: list[dict]
    decreasing_factors: list[dict]
    data_quality: list[str]
    ood_warning: str | None = None
    illustrative_counterfactual: str | None = None
    disclaimer: str
