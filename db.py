import os
from typing import Annotated
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session, create_engine

# Cargar variables de entorno
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tiendadb")

# Cadena de conexión hacia PostgreSQL en Amazon RDS
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Motor de base de datos
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Ciclo de vida para crear tablas automáticamente en RDS
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

# Inyección de dependencia para las sesiones
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]