from pydantic import BaseModel
from typing import List, Dict, Optional

class ConfiguracionWriting(BaseModel):
    nivel: str
    contexto: str
    grupo_verbos: str
    mood: str
    tense: str

class ChatRequest(BaseModel):
    message: str
    config: ConfiguracionWriting
    messageHistory: Optional[List[Dict[str, str]]] = []
    gradeExercise: Optional[bool] = False

class WritingContextResponse(BaseModel):
    escenario: str
    primer_mensaje: str

class ChatRequest(BaseModel):
    message: str
    config: ConfiguracionWriting
    messageHistory: Optional[List[Dict[str, str]]] = []
    gradeExercise: Optional[bool] = False

class CorreccionChat(BaseModel):
    error: str
    correccion: str
    explicacion: str

class ChatTurnResponse(BaseModel):
    respuesta_chat: str
    correcciones: List[CorreccionChat]

class ChatGradeResponse(BaseModel):
    score: float
    feedback: str
    exerciseComplete: bool