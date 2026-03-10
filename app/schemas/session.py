from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class DetalleSesionResponse(BaseModel):
    verbo_infinitivo: str
    respuesta_correcta: str
    respuesta_usuario: str
    puntaje: float
    categoria_error: Optional[str] = None
    feedback_ia: Optional[str] = None

    class Config:
        from_attributes = True

class SesionResumenResponse(BaseModel):
    id: int
    fecha: datetime
    modulo: str
    mood: str
    tense: str
    puntaje_total: float

    class Config:
        from_attributes = True

class SesionCompletaResponse(SesionResumenResponse):
    texto_generado_ia: Optional[str] = None
    detalles: List[DetalleSesionResponse]

class WeakestTenseSchema(BaseModel):
    name: str
    score: float

class TenseStatSchema(BaseModel):
    name: str
    score: float
    total: int

class WeaknessItemSchema(BaseModel):
    category: str
    mastery_level: float
    error_count: int

class ReportDataSchema(BaseModel):
    recommendations: List[str]
    weaknesses: List[WeaknessItemSchema]

class DashboardResponse(BaseModel):
    totalExercises: int
    weakestTense: Optional[WeakestTenseSchema]
    stats: List[TenseStatSchema]
    report: ReportDataSchema