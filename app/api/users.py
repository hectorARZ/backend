from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_password_hash, verify_password, get_usuario_actual
from app.models.habilities import ProgresoHabilidad
from app.schemas.user import UsuarioCreate, UsuarioResponse, UsuarioUpdateAdmin, UsuarioUpdatePassword
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models import Usuario
from app.schemas.user import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    
    #if usuario_actual.rol != "admin":
    #    raise HTTPException(
    #        status_code=status.HTTP_403_FORBIDDEN,
    #        detail="¡Solo los administradores pueden crear usuarios nuevos."
    #    )
    
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este correo ya está registrado en el sistema"
        )

    hashed_password = get_password_hash(usuario.password)

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        email=usuario.email,
        password_hash=hashed_password,
        rol=usuario.rol
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario

@router.get("/", response_model=List[UsuarioResponse])
def obtener_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_usuario_actual)):
    
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="¡Acceso denegado! Solo los administradores pueden ver esta lista."
        )

    usuarios = db.query(Usuario).filter(
        Usuario.rol != "admin"
    ).offset(skip).limit(limit).all()

    return usuarios

@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def suspender_usuario(usuario_id: int, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_usuario_actual)):
    
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="¡Acceso denegado! No tienes permisos para suspender cuentas."
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    usuario.is_active = False
    
    db.commit()
    
    return {"message": f"El usuario {usuario.nombre} ha sido suspendido exitosamente"}

@router.get("/me", response_model=UsuarioResponse)
def obtener_mi_perfil(usuario_actual: Usuario = Depends(get_usuario_actual)):
    return usuario_actual

@router.patch("/{usuario_id}/reactivar", status_code=status.HTTP_200_OK)
def reactivar_usuario(usuario_id: int, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(get_usuario_actual)):
    
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="¡Acceso denegado! No tienes permisos para reactivar cuentas."
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    if usuario.is_active:
        return {"message": f"El usuario {usuario.nombre} ya estaba activo"}
        
    usuario.is_active = True
    
    db.commit()
    
    return {"message": f"¡El usuario {usuario.nombre} ha sido reactivado con éxito!"}

@router.patch("/{usuario_id}/password", status_code=status.HTTP_200_OK)
def actualizar_password(
    usuario_id: int, 
    datos: UsuarioUpdatePassword, 
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if not verify_password(datos.password_actual, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    nueva_password_hasheada = get_password_hash(datos.password_nueva)
    usuario.password_hash = nueva_password_hasheada
    
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}

@router.get("/stats")
def obtener_estadisticas_gramaticales(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):
    stats = db.query(ProgresoHabilidad).filter(
        ProgresoHabilidad.usuario_id == usuario_actual.id
    ).all()

    return {
        "usuario": usuario_actual.email,
        "habilidades": {s.categoria: s.puntaje for s in stats}
    }

@router.patch("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def actualizar_usuario_como_admin(
    usuario_id: int, 
    datos_actualizados: UsuarioUpdateAdmin, 
    db: Session = Depends(get_db), 
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="¡Acceso denegado! Solo los administradores pueden editar perfiles de otros usuarios."
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en la base de datos."
        )

    if datos_actualizados.email and datos_actualizados.email != usuario.email:
        email_ocupado = db.query(Usuario).filter(Usuario.email == datos_actualizados.email).first()
        if email_ocupado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ese correo electrónico ya está siendo usado por otro usuario."
            )

    datos_dict = datos_actualizados.model_dump(exclude_unset=True)
    
    for key, value in datos_dict.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)

    return usuario