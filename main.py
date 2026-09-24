from typing import List
from fastapi import FastAPI, HTTPException, status
from sqlmodel import select
from db import lifespan, SessionDep
from models import Usuario, UsuarioCreate, UsuarioUpdate, Reserva, ReservaCreate, ReservaUpdate

app = FastAPI(
    title="Gamer Store API (AWS RDS)",
    description="API RESTful conectada a Amazon RDS PostgreSQL",
    lifespan=lifespan
)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "database": "Amazon RDS PostgreSQL",
        "documentation": "/docs"
    }

# ==========================================
# CRUD ENTIDAD 1: USUARIOS
# ==========================================
@app.post("/usuarios/", response_model=Usuario, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(data: UsuarioCreate, session: SessionDep):
    usuario_db = Usuario.model_validate(data)
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db

@app.get("/usuarios/", response_model=List[Usuario], tags=["Usuarios"])
def listar_usuarios(session: SessionDep):
    return session.exec(select(Usuario)).all()

@app.get("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"])
def obtener_usuario(usuario_id: int, session: SessionDep):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, data: UsuarioUpdate, session: SessionDep):
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario_db, key, value)
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db

@app.delete("/usuarios/{usuario_id}", tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, session: SessionDep):
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(usuario_db)
    session.commit()
    return {"mensaje": f"Usuario con ID {usuario_id} eliminado exitosamente de RDS"}

# ==========================================
# CRUD ENTIDAD 2: RESERVAS
# ==========================================
@app.post("/reservas/", response_model=Reserva, status_code=status.HTTP_201_CREATED, tags=["Reservas"])
def crear_reserva(data: ReservaCreate, session: SessionDep):
    # Validar que el usuario exista en la base de datos de RDS
    if not session.get(Usuario, data.usuario_id):
        raise HTTPException(status_code=404, detail=f"El usuario_id {data.usuario_id} no existe en RDS")
    reserva_db = Reserva.model_validate(data)
    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)
    return reserva_db

@app.get("/reservas/", response_model=List[Reserva], tags=["Reservas"])
def listar_reservas(session: SessionDep):
    return session.exec(select(Reserva)).all()

@app.get("/reservas/{reserva_id}", response_model=Reserva, tags=["Reservas"])
def obtener_reserva(reserva_id: int, session: SessionDep):
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@app.put("/reservas/{reserva_id}", response_model=Reserva, tags=["Reservas"])
def actualizar_reserva(reserva_id: int, data: ReservaUpdate, session: SessionDep):
    reserva_db = session.get(Reserva, reserva_id)
    if not reserva_db:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    update_data = data.model_dump(exclude_unset=True)
    if "usuario_id" in update_data and not session.get(Usuario, update_data["usuario_id"]):
        raise HTTPException(status_code=404, detail="El nuevo usuario_id no existe en RDS")
    for key, value in update_data.items():
        setattr(reserva_db, key, value)
    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)
    return reserva_db

@app.delete("/reservas/{reserva_id}", tags=["Reservas"])
def eliminar_reserva(reserva_id: int, session: SessionDep):
    reserva_db = session.get(Reserva, reserva_id)
    if not reserva_db:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    session.delete(reserva_db)
    session.commit()
    return {"mensaje": f"Reserva con ID {reserva_id} eliminada exitosamente de RDS"}
    session.commit()
    return {"mensaje": f"Reserva con ID {reserva_id} eliminada exitosamente de RDS"}