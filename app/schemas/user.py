from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr
    rol: Optional[str] = "estudiante"

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdatePassword(BaseModel):
    password_actual: str
    password_nueva: str

class UsuarioResponse(UsuarioBase):
    id: int
    is_active: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

from typing import Optional

class UsuarioUpdateAdmin(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None