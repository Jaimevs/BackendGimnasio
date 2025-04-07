from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from config.db import get_db, engine
from portadortoken import Portador
import crud.quejas
import schemas.quejas
import models.users
import models.quejas
import models.clases
from datetime import datetime

feedback_router = APIRouter()

# Crear las tablas si no existen
models.quejas.Base.metadata.create_all(bind=engine)

# Ruta para obtener una queja específica
@feedback_router.get('/quejas/{id}', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def read_queja(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la queja
    db_queja = crud.quejas.get_queja(db=db, id=id)
    if db_queja is None:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    # Verificar si el usuario es el autor de la queja, el entrenador evaluado o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if db_queja.Usuario_ID != user_id and db_queja.Entrenador_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta queja")
    
    return db_queja

# Ruta para crear una queja
@feedback_router.post('/quejas/', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def create_queja(queja: schemas.quejas.QuejaCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el entrenador exista y tenga rol de entrenador
    entrenador = db.query(models.users.User).filter(models.users.User.ID == queja.Entrenador_ID).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    
    # Verificar si tiene rol de entrenador
    is_entrenador = False
    for rol in entrenador.roles:
        if rol.Nombre == "entrenador":
            is_entrenador = True
            break
    
    if not is_entrenador:
        raise HTTPException(status_code=400, detail="El usuario seleccionado no es un entrenador")
    
    # Verificar que la clase exista y pertenezca al entrenador
    clase = db.query(models.clases.Clase).filter(models.clases.Clase.ID == queja.Clase_ID).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    if clase.Entrenador_ID != queja.Entrenador_ID:
        raise HTTPException(status_code=400, detail="La clase seleccionada no pertenece al entrenador indicado")
    
    # Verificar que la calificación esté entre 1 y 5
    if queja.Calificacion < 1 or queja.Calificacion > 5:
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5 estrellas")
    
    return crud.quejas.create_queja(db=db, queja=queja, usuario_id=user_id)

# Ruta para actualizar una queja
@feedback_router.put('/quejas/{id}', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def update_queja(id: int, queja: schemas.quejas.QuejaUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la queja
    db_queja = crud.quejas.get_queja(db=db, id=id)
    if db_queja is None:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    # Verificar si el usuario es el autor de la queja
    if db_queja.Usuario_ID != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes actualizar tus propias quejas")
    
    # Verificar que la calificación esté entre 1 y 5 si se proporciona
    if queja.Calificacion is not None and (queja.Calificacion < 1 or queja.Calificacion > 5):
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5 estrellas")
    
    return crud.quejas.update_queja(db=db, id=id, queja=queja)

# Ruta para eliminar una queja
@feedback_router.delete('/quejas/{id}', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def delete_queja(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la queja
    db_queja = crud.quejas.get_queja(db=db, id=id)
    if db_queja is None:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    # Verificar si el usuario es el autor de la queja o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if db_queja.Usuario_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propias quejas o ser administrador")
    
    return crud.quejas.delete_queja(db=db, id=id)

# Ruta para obtener mis quejas
@feedback_router.get('/mis-quejas/', response_model=List[schemas.quejas.Queja], tags=['Feedback'], dependencies=[Depends(Portador())])
def read_mis_quejas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return crud.quejas.get_quejas_by_usuario(db=db, usuario_id=user_id, skip=skip, limit=limit)
