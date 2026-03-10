from pydantic import BaseModel

class ConfiguracionListening(BaseModel):
    nivel: str
    contexto: str
    grupo_verbos: str
    mood: str
    tense: str

class ListeningGenerateResponse(BaseModel):
    audio_base64: str
    texto_original: str

class ListeningGradeRequest(BaseModel):
    config: ConfiguracionListening
    texto_original: str
    respuesta_usuario: str

class ListeningGradeResponse(BaseModel):
    score: float
    feedback: str
    texto_original: str