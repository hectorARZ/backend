from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class DetalleRespuesta(Base):
    __tablename__ = "detalle_respuestas"

    id = Column(Integer, primary_key=True, index=True)
    
    sesion_id = Column(Integer, ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False)
    
    verbo_infinitivo = Column(String(50), nullable=False)
    respuesta_correcta = Column(Text, nullable=False)
    respuesta_usuario = Column(Text, nullable=False)
    
    puntaje = Column(Float, nullable=False)

    categoria_error = Column(String(100), nullable=True)

    feedback_ia = Column(Text, nullable=True)

    sesion = relationship("Sesion", back_populates="detalles")