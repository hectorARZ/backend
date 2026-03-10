from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import sessions, reading, users, auth, speaking, writing, listening
from app.core.database import engine, Base

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [
    reading.router,
    speaking.router,
    users.router,
    auth.router,
    writing.router,
    listening.router,
    sessions.router,
]

for router in routers:
    app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"mensaje": f"Bienvenido a {settings.PROJECT_NAME}"}