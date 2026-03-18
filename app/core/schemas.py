from typing import Literal
from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    category: Literal["Produtivo", "Improdutivo"]
    confidence: float = Field(ge=0, le=1)
    suggested_reply: str
    summary: str
    reasoning: str
    detected_signals: list[str]
    processed_text: str


class HealthResponse(BaseModel):
    status: str
    provider: str
