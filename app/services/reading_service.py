import logging
from sqlalchemy.orm import Session
from app.core.grammar import get_correct_form
from app.core.scoring import calcular_calificacion
from app.models.response_detail import DetalleRespuesta
from app.models.session import Sesion
from app.schemas.reading import ResultadoEjercicio, ValidarLecturaRequest

logger = logging.getLogger(__name__)

def procesar_lectura_completa(data_ia: dict):

    if not data_ia or 'texto' not in data_ia or 'ejercicios' not in data_ia:
        return {"error": "El formato de la IA es inválido o está incompleto."}

    ejercicios_finales = []

    for i, ej in enumerate(data_ia['ejercicios'], 1):
        respuesta = get_correct_form(
            verb=ej.get('infinitivo', ''),
            mood=ej.get('mood', 'indicative'),
            tense=ej.get('tense', 'present'),
            persona=ej.get('persona', 'je')
        )

        if respuesta:
            ejercicios_finales.append({
                "id": f"[VERBE_{i}]",
                "infinitivo": ej.get('infinitivo'),
                "persona": ej.get('persona'),
                "respuesta_correcta": respuesta
            })
        else:
            logger.warning(f"No se pudo procesar el verbo '{ej.get('infinitivo')}' en la posición {i}")

    return {
        "texto": data_ia['texto'],
        "ejercicios": ejercicios_finales
    }

def calificar_ejercicios(ejercicios) -> list[ResultadoEjercicio]:
    return [
        ResultadoEjercicio(
            id=item.id,
            puntaje=(score := calcular_calificacion(item.respuesta_usuario, item.respuesta_correcta, umbral_minimo=70)),
            es_correcto=score >= 70
        )
        for item in ejercicios
    ]

def crear_sesion(db: Session, usuario_id: int, datos: ValidarLecturaRequest, puntaje_final: float) -> Sesion:
    sesion = Sesion(
        usuario_id=usuario_id,
        modulo="lectura",
        mood=datos.mood,
        tense=datos.tense,
        puntaje_total=puntaje_final,
        texto_generado_ia=datos.texto_base
    )
    db.add(sesion)
    db.flush()
    return sesion

def crear_detalle(sesion_id, original, evaluado) -> DetalleRespuesta:
    return DetalleRespuesta(
        sesion_id=sesion_id,
        verbo_infinitivo=original.id,
        respuesta_correcta=original.respuesta_correcta,
        respuesta_usuario=original.respuesta_usuario,
        puntaje=evaluado.puntaje,
        categoria_error=evaluado.categoria_error,
        feedback_ia=evaluado.feedback_ia
    )