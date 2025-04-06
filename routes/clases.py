# routes/clases.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from config.db import get_db, engine
from portadortoken import Portador
from jwt_config import decode_token
import crud.clases
import schemas.clases
import models.users
import models.clases
from datetime import datetime

clase_router = APIRouter()

# Crear la tabla
models.clases.Base.metadata.create_all(bind=engine)

# Ruta para obtener todas las clases (solo administradores)
@clase_router.get('/clases/', response_model=List[schemas.clases.Clase], tags=['Clases'])
def read_clases(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    """Obtener todas las clases (solo administradores)"""
    # Extraer el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar roles del usuario
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si es admin
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Solo los administradores pueden ver todas las clases
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver todas las clases")
    
    return crud.clases.get_clases(db=db, skip=skip, limit=limit)

# Ruta para que los entrenadores vean solo sus propias clases
@clase_router.get('/mis-clases/', response_model=List[schemas.clases.Clase], tags=['Clases'])
def read_mis_clases(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    """Obtener clases del entrenador actual"""
    # Extraer el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario exista
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si tiene rol de entrenador
    is_entrenador = False
    for rol in user.roles:
        if rol.Nombre == "entrenador":
            is_entrenador = True
            break
    
    if not is_entrenador:
        raise HTTPException(status_code=403, detail="Solo los entrenadores pueden ver sus clases")
    
    # Devolver solo las clases del entrenador actual
    return crud.clases.get_clases_by_entrenador(db=db, entrenador_id=user_id, skip=skip, limit=limit)

# Ruta para crear una clase (solo entrenadores)
@clase_router.post('/clases/', response_model=schemas.clases.Clase, tags=['Clases'])
def create_clase(clase: schemas.clases.ClaseCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    """Crear una nueva clase usando el ID del entrenador desde el token"""
    # Extraer el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario tenga rol de entrenador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si tiene rol de entrenador
    is_entrenador = False
    for rol in user.roles:
        if rol.Nombre == "entrenador":
            is_entrenador = True
            break
    
    if not is_entrenador:
        raise HTTPException(status_code=403, detail="Solo los entrenadores pueden crear clases")
    
    # Pasar el ID del entrenador directamente a la función de creación
    return crud.clases.create_clase(db=db, clase=clase, entrenador_id=user_id)

# Ruta para actualizar una clase (solo el entrenador que la creó o admin)
@clase_router.put('/clases/{id}', response_model=schemas.clases.Clase, tags=['Clases'])
def update_clase(id: int, clase: schemas.clases.ClaseUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    """Actualizar una clase (solo el entrenador que la creó o admin)"""
    # Extraer el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la clase actual
    db_clase = crud.clases.get_clase(db=db, id=id)
    if db_clase is None:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    # Verificar si el usuario es el entrenador de la clase o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Solo permitir actualizar si es el entrenador que creó la clase o es admin
    if db_clase.Entrenador_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Solo puedes actualizar tus propias clases")
    
    return crud.clases.update_clase(db=db, id=id, clase=clase)

# Ruta para eliminar una clase (solo el entrenador que la creó o admin)
@clase_router.delete('/clases/{id}', response_model=schemas.clases.Clase, tags=['Clases'])
def delete_clase(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    """Eliminar una clase (solo el entrenador que la creó o admin)"""
    # Extraer el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la clase actual
    db_clase = crud.clases.get_clase(db=db, id=id)
    if db_clase is None:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    # Verificar si el usuario es el entrenador de la clase o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Solo permitir eliminar si es el entrenador que creó la clase o es admin
    if db_clase.Entrenador_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propias clases")
    
    return crud.clases.delete_clase(db=db, id=id)