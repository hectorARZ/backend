import os
from dotenv import load_dotenv
from app.core.database import SessionLocal
from app.models import Usuario
from app.core.security import get_password_hash 

load_dotenv()

def inicializar_db():
    print("🌱 Iniciando el proceso de Seeding...")
    db = SessionLocal()
    
    try:
        admin_email = os.getenv("ADMIN_INIT_EMAIL")
        admin_password = os.getenv("ADMIN_INIT_PASSWORD")
        
        admin_nombre = os.getenv("ADMIN_NAME")
        admin_apellidos = os.getenv("ADMIN_LASTNAME")
        admin_rol = "admin"

        usuario_existente = db.query(Usuario).filter(Usuario.email == admin_email).first()
        
        if usuario_existente:
            print(f"⚠️  El usuario {admin_email} ya existe.")
        else:
            print(f"⚙️  Creando usuario: {admin_nombre}...")
            
            hashed_pwd = get_password_hash(admin_password) 
            
            nuevo_usuario = Usuario(
                nombre=admin_nombre,
                apellidos=admin_apellidos,
                email=admin_email,
                password_hash=hashed_pwd,
                rol=admin_rol,
                is_active=True
            )
            
            db.add(nuevo_usuario)
            db.commit()
            print("✅ ¡Usuario administrador creado con éxito!")

    except Exception as e:
        print(f"❌ Error durante el seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inicializar_db()