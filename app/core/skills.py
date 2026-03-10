from sqlalchemy.orm import Session
from app.models.habilities import ProgresoHabilidad

def actualizar_progreso_habilidad(db: Session, usuario_id: int, categoria: str, puntos: int):
    habilidad = db.query(ProgresoHabilidad).filter(
        ProgresoHabilidad.usuario_id == usuario_id,
        ProgresoHabilidad.categoria == categoria
    ).first()

    if not habilidad:
        habilidad = ProgresoHabilidad(
            usuario_id=usuario_id, 
            categoria=categoria, 
            puntaje=puntos
        )
        db.add(habilidad)
    else:
        habilidad.puntaje += puntos