import traceback
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_usuario_actual
from app.models import Usuario
from app.models.response_detail import DetalleRespuesta
from app.models.session import Sesion
from app.schemas.writing import ChatGradeResponse, ChatRequest, ChatTurnResponse, ConfiguracionWriting, WritingContextResponse
from app.services.ia_service import evaluar_chat_ia, generar_contexto_escritura_ia, generar_respuesta_chat_ia

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat IA / Escritura"])

@router.post("/generate-context", response_model=WritingContextResponse)
async def generate_context(
    config: ConfiguracionWriting, 
    usuario_actual: Usuario = Depends(get_usuario_actual) 
):
    try:
        resultado_ia = await generar_contexto_escritura_ia(
            nivel=config.nivel,
            contexto=config.contexto,
            grupo_verbos=config.grupo_verbos,
            mood=config.mood,
            tense=config.tense
        )
        
        return WritingContextResponse(
            escenario=resultado_ia["escenario"],
            primer_mensaje=resultado_ia["primer_mensaje"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Error al conectar con OpenAI para generar el contexto: {str(e)}"
        )
    
@router.post("/", response_model=None)
async def chat_principal(
    request: ChatRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):     
    try:
        config_dict = request.config.model_dump()

        historial_seguro = []
        for m in request.messageHistory:
            rol = m.get("role") if isinstance(m, dict) else getattr(m, "role", "user")
            contenido = m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
            
            if contenido is None:
                contenido = ""
                
            historial_seguro.append({"role": rol, "content": contenido})

        if request.gradeExercise:
            resultado_final = await evaluar_chat_ia(
                config=config_dict,
                historial=historial_seguro 
            )
            
            score = float(resultado_final.get("score", 0))
            feedback = resultado_final.get("feedback", "Buen trabajo.")
            
            nueva_sesion = Sesion(
                usuario_id=usuario_actual.id,
                modulo="escritura",
                mood=request.config.mood,
                tense=request.config.tense,
                puntaje_total=score,
                texto_generado_ia=feedback
            )
            db.add(nueva_sesion)
            db.flush()

            textos_del_usuario = " | ".join([m["content"] for m in historial_seguro if m["role"] == "user"])

            detalle = DetalleRespuesta(
                sesion_id=nueva_sesion.id,
                verbo_infinitivo="Conversación",
                respuesta_correcta="Uso correcto de: " + request.config.tense,
                respuesta_usuario=textos_del_usuario,
                puntaje=score,
                categoria_error="Gramática / Producción Escrita",
                feedback_ia=feedback
            )
            db.add(detalle)
            db.commit()
            
            return ChatGradeResponse(
                score=score,
                feedback=feedback,
                exerciseComplete=True
            )

        logger.debug("Generando respuesta IA para mensaje del usuario")
        resultado_turno = await generar_respuesta_chat_ia(
            mensaje=request.message,
            config=config_dict,
            historial=historial_seguro
        )
        
        if "respuesta_chat" not in resultado_turno:
            raise ValueError("La IA no devolvió 'respuesta_chat'. Revisa el servicio.")

        return ChatTurnResponse(
            respuesta_chat=resultado_turno["respuesta_chat"],
            correcciones=resultado_turno.get("correcciones", [])
        )

    except Exception as e:
        logger.error("--- ❌ ERROR DETECTADO ---")
        logger.exception(e)
        raise HTTPException(
            status_code=500, 
            detail=f"Error procesando el chat: {str(e)}"
        )