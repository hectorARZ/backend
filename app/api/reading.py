import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.security import get_usuario_actual
from app.core.database import get_db
from app.schemas.reading import (
    GenerarLecturaRequest, LecturaResponse, ValidarLecturaRequest, ValidarLecturaResponse)
from app.services.ia_service import analizar_error_gramatical, generar_texto_ia
from app.services.reading_service import calificar_ejercicios, crear_detalle, crear_sesion, procesar_lectura_completa
from app.models.user import Usuario
from app.core.skills import actualizar_progreso_habilidad

router = APIRouter(
    prefix="/reading",
    tags=["Reading"],
    dependencies=[Depends(get_usuario_actual)]
)

logger = logging.getLogger(__name__)


@router.post("/generar", response_model=LecturaResponse)
async def generar_ejercicio(datos: GenerarLecturaRequest):
    try:
        data_ia = await generar_texto_ia(datos.nivel, datos.contexto, datos.grupo_verbos, datos.mood, datos.tense)
        resultado = procesar_lectura_completa(data_ia)
        return resultado
    except Exception as e:
        logger.error(f"Error en /reading/generar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="No se pudo generar la lectura. Intenta de nuevo más tarde.")

@router.post("/validar", response_model=ValidarLecturaResponse)
async def validar_ejercicio_lectura(
    datos: ValidarLecturaRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if not datos.ejercicios:
        raise HTTPException(status_code=400, detail="No hay ejercicios para calificar")

    try:
        resultados = calificar_ejercicios(datos.ejercicios)
        puntaje_final = round(sum(r.puntaje for r in resultados) / len(resultados), 2)
        tema_actual = f"{datos.mood} - {datos.tense}"

        balance_puntos = sum(1 if r.es_correcto else -1 for r in resultados)
        actualizar_progreso_habilidad(db, usuario_actual.id, tema_actual, balance_puntos)
        
        sesion = crear_sesion(db, usuario_actual.id, datos, puntaje_final)

        for original, evaluado in zip(datos.ejercicios, resultados):
            if evaluado.puntaje < 100:
                analisis = await analizar_error_gramatical(
                    verbo_correcto=original.respuesta_correcta,
                    respuesta_usuario=original.respuesta_usuario,
                    contexto=datos.texto_base
                )
                evaluado.categoria_error = analisis.get("categoria")
                evaluado.feedback_ia = analisis.get("feedback")

            db.add(crear_detalle(sesion.id, original, evaluado))

        db.commit()
        return ValidarLecturaResponse(puntaje_total=puntaje_final, resultados=resultados)

    except Exception as e:
        db.rollback()
        logger.error(f"Error al calificar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al calificar el ejercicio")
