from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class ProgresoHabilidad(Base):
    __tablename__ = "progreso_habilidades"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    categoria = Column(String(50), nullable=False) 
    
    puntaje = Column(Integer, default=0, nullable=False)