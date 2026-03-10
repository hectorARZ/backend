from pydantic import BaseModel
from typing import List, Optional

class GenerarLecturaRequest(BaseModel):
    nivel: str
    contexto: str
    grupo_verbos: str
    mood: str
    tense: str

class EjercicioResponse(BaseModel):
    id: str
    infinitivo: str
    persona: str
    respuesta_correcta: str

class LecturaResponse(BaseModel):
    texto: str
    ejercicios: List[EjercicioResponse]

class ItemValidacion(BaseModel):
    id: str                 
    respuesta_usuario: str  
    respuesta_correcta: str 

class ValidarLecturaRequest(BaseModel):
    mood: str
    tense: str
    texto_base: str
    ejercicios: List[ItemValidacion]

class ResultadoEjercicio(BaseModel):
    id: str
    puntaje: float
    es_correcto: bool
    categoria_error: Optional[str] = None
    feedback_ia: Optional[str] = None

class ValidarLecturaResponse(BaseModel):
    puntaje_total: float
    resultados: List[ResultadoEjercicio]