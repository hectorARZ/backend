from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_usuario_actual
from app.models.response_detail import DetalleRespuesta
from app.models.session import Sesion
from app.schemas.session import DashboardResponse, ReportDataSchema, SesionResumenResponse, SesionCompletaResponse, TenseStatSchema, WeakestTenseSchema, WeaknessItemSchema

router = APIRouter(prefix="/sessions", tags=["Historial de Sesiones"])

@router.get("/me", response_model=List[SesionResumenResponse])
def obtener_mi_historial(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):

    sesiones = db.query(Sesion).filter(
        Sesion.usuario_id == usuario_actual.id
    ).order_by(Sesion.fecha.desc()).all()
    
    return sesiones

@router.get("/me/{sesion_id}", response_model=SesionCompletaResponse)
def obtener_detalle_de_sesion(
    sesion_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):
    sesion = db.query(Sesion).filter(
        Sesion.id == sesion_id,
        Sesion.usuario_id == usuario_actual.id
    ).first()
    
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada o no tienes permisos para verla")
    
    return sesion

@router.get("/dashboard", response_model=DashboardResponse)
def obtener_dashboard_stats(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):

    total_ejercicios = db.query(Sesion).filter(Sesion.usuario_id == usuario_actual.id).count()

    if total_ejercicios == 0:
        return DashboardResponse(
            totalExercises=0,
            weakestTense=None,
            stats=[],
            report={"recommendations": ["Completa tu primer ejercicio para ver tus estadísticas."], "weaknesses": []}
        )


    tenses_data = db.query(
        Sesion.tense,
        func.avg(Sesion.puntaje_total).label("promedio"),
        func.count(Sesion.id).label("total")
    ).filter(Sesion.usuario_id == usuario_actual.id).group_by(Sesion.tense).all()

    stats = [
        TenseStatSchema(
            name=t.tense.capitalize(), 
            score=round(t.promedio, 2), 
            total=t.total
        )
        for t in tenses_data
    ]

    weakest = None
    if stats:

        weakest_stat = min(stats, key=lambda x: x.score)
        weakest = WeakestTenseSchema(name=weakest_stat.name, score=weakest_stat.score)

    errores_data = db.query(
        DetalleRespuesta.categoria_error,
        func.count(DetalleRespuesta.id).label("conteo_errores"),
        func.avg(DetalleRespuesta.puntaje).label("mastery")
    ).join(Sesion).filter(
        Sesion.usuario_id == usuario_actual.id,
        DetalleRespuesta.categoria_error.isnot(None),
        DetalleRespuesta.puntaje < 100
    ).group_by(DetalleRespuesta.categoria_error)\
     .order_by(func.count(DetalleRespuesta.id).desc()).limit(5).all()

    weaknesses = [
        WeaknessItemSchema(
            category=err.categoria_error,
            mastery_level=round(err.mastery, 2),
            error_count=err.conteo_errores
        )
        for err in errores_data
    ]

    recomendaciones = []
    if weakest:
        recomendaciones.append(f"Te sugerimos enfocar tu práctica en el tiempo: {weakest.name}.")
    
    for w in weaknesses[:2]:
        recomendaciones.append(f"Repasa las reglas de: {w.category.lower()}.")

    if not recomendaciones:
        recomendaciones.append("¡Excelente trabajo! Sigue practicando para mantener el nivel.")


    return DashboardResponse(
        totalExercises=total_ejercicios,
        weakestTense=weakest,
        stats=stats,
        report=ReportDataSchema(
            recommendations=recomendaciones,
            weaknesses=weaknesses
        )
    )

@router.get("/admin/user-dashboard/{usuario_id}", response_model=DashboardResponse)
def obtener_dashboard_de_usuario_para_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):

    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="¡Acceso denegado! Solo los administradores pueden ver los reportes de otros usuarios."
        )


    total_ejercicios = db.query(Sesion).filter(Sesion.usuario_id == usuario_id).count()

    if total_ejercicios == 0:
        return DashboardResponse(
            totalExercises=0,
            weakestTense=None,
            stats=[],
            report={"recommendations": ["El usuario aún no ha completado ejercicios."], "weaknesses": []}
        )

    tenses_data = db.query(
        Sesion.tense,
        func.avg(Sesion.puntaje_total).label("promedio"),
        func.count(Sesion.id).label("total")
    ).filter(Sesion.usuario_id == usuario_id).group_by(Sesion.tense).all()

    stats = [
        TenseStatSchema(
            name=t.tense.capitalize(), 
            score=round(t.promedio, 2), 
            total=t.total
        )
        for t in tenses_data
    ]

    weakest = None
    if stats:
        weakest_stat = min(stats, key=lambda x: x.score)
        weakest = WeakestTenseSchema(name=weakest_stat.name, score=weakest_stat.score)


    errores_data = db.query(
        DetalleRespuesta.categoria_error,
        func.count(DetalleRespuesta.id).label("conteo_errores"),
        func.avg(DetalleRespuesta.puntaje).label("mastery")
    ).join(Sesion).filter(
        Sesion.usuario_id == usuario_id,
        DetalleRespuesta.categoria_error.isnot(None),
        DetalleRespuesta.puntaje < 100
    ).group_by(DetalleRespuesta.categoria_error)\
     .order_by(func.count(DetalleRespuesta.id).desc()).limit(5).all()

    weaknesses = [
        WeaknessItemSchema(
            category=err.categoria_error,
            mastery_level=round(err.mastery, 2),
            error_count=err.conteo_errores
        )
        for err in errores_data
    ]

    recomendaciones = []
    if weakest:
        recomendaciones.append(f"El usuario necesita enfocar su práctica en el tiempo: {weakest.name}.")
    
    for w in weaknesses[:2]:
        recomendaciones.append(f"Debería repasar las reglas de: {w.category.lower()}.")

    if not recomendaciones:
        recomendaciones.append("El usuario tiene un excelente desempeño.")

    return DashboardResponse(
        totalExercises=total_ejercicios,
        weakestTense=weakest,
        stats=stats,
        report=ReportDataSchema(
            recommendations=recomendaciones,
            weaknesses=weaknesses
        )
    )