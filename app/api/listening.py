from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_usuario_actual
from app.models import Usuario
from app.models.response_detail import DetalleRespuesta
from app.models.session import Sesion
from app.schemas.listening import (
    ConfiguracionListening, ListeningGenerateResponse, 
    ListeningGradeRequest, ListeningGradeResponse
)
from app.services.ia_service import (
    generar_texto_listening_ia, generar_audio_tts, evaluar_listening_ia
)

router = APIRouter(prefix="/listening", tags=["Módulo Escuchar"])

@router.post("/generate", response_model=ListeningGenerateResponse)
async def listening_generate(
    config: ConfiguracionListening,
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    try:
        texto = await generar_texto_listening_ia(
            nivel=config.nivel,
            contexto=config.contexto,
            grupo_verbos=config.grupo_verbos,
            mood=config.mood,
            tense=config.tense
        )
        audio_b64 = await generar_audio_tts(texto)
        
        return ListeningGenerateResponse(
            audio_base64=audio_b64,
            texto_original=texto
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el dictado: {str(e)}")


@router.post("/grade", response_model=ListeningGradeResponse)
async def listening_grade(
    request: ListeningGradeRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    try:
        resultado = await evaluar_listening_ia(
            texto_original=request.texto_original,
            respuesta_usuario=request.respuesta_usuario
        )
        score = float(resultado.get("score", 0))
        feedback = resultado.get("feedback", "")
        nueva_sesion = Sesion(
            usuario_id=usuario_actual.id,
            modulo="escuchar",
            mood=request.config.mood,
            tense=request.config.tense,
            puntaje_total=score,
            texto_generado_ia=request.texto_original
        )
        db.add(nueva_sesion)
        db.flush()

        detalle = DetalleRespuesta(
            sesion_id=nueva_sesion.id,
            verbo_infinitivo="Dictado Completo",
            respuesta_correcta=request.texto_original,
            respuesta_usuario=request.respuesta_usuario,
            puntaje=score,
            categoria_error="Comprensión Oral",
            feedback_ia=feedback
        )
        db.add(detalle)
        db.commit()
        
        return ListeningGradeResponse(
            score=score,
            feedback=feedback,
            texto_original=request.texto_original
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calificar el dictado: {str(e)}")