from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    
    nombre = Column(String(50), nullable=False)
    apellidos = Column(String(100), nullable=False)
    
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    password_hash = Column(String(255), nullable=False)
    
    rol = Column(String(20), default="estudiante") 
    
    is_active = Column(Boolean, default=True)
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")