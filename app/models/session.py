from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    modulo = Column(String(50), nullable=False)
    mood = Column(String(50), nullable=False)
    tense = Column(String(50), nullable=False)
    
    puntaje_total = Column(Float, nullable=False)
    
    texto_generado_ia = Column(Text, nullable=True) 
    
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="sesiones")
    detalles = relationship("DetalleRespuesta", back_populates="sesion", cascade="all, delete-orphan")