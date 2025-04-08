from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db, engine
from portadortoken import Portador
import crud.opinion_cliente
import schemas.opinion_cliente
import models.users
import models.opinion_cliente
from datetime import datetime

opinion_cliente_router = APIRouter()

models.opinion_cliente.Base.metadata.create_all(bind=engine)

# Ruta para obtener una opinión especifica
@opinion_cliente_router.get('/opiniones/{id}', response_model=schemas.opinion_cliente.OpinionCliente, tags=['Opiniones'], dependencies=[Depends(Portador())])
def read_opinion(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la opinion
    db_opinion = crud.opinion_cliente.get_opinion(db=db, id=id)
    if db_opinion is None:
        raise HTTPException(status_code=404, detail="Opinión no encontrada")
    
    # Verificar si el usuario es el autor de la opinion o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Solo el autor o un administrador pueden ver la opinion
    if db_opinion.Usuario_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta opinión")
    
    return db_opinion

# Ruta para crear una opinion
@opinion_cliente_router.post('/opiniones/', response_model=schemas.opinion_cliente.OpinionCliente, tags=['Opiniones'], dependencies=[Depends(Portador())])
def create_opinion(opinion: schemas.opinion_cliente.OpinionClienteCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return crud.opinion_cliente.create_opinion(db=db, opinion=opinion, usuario_id=user_id)

# Ruta para actualizar una opinion
@opinion_cliente_router.put('/opiniones/{id}', response_model=schemas.opinion_cliente.OpinionCliente, tags=['Opiniones'], dependencies=[Depends(Portador())])
def update_opinion(id: int, opinion: schemas.opinion_cliente.OpinionClienteUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la opinion
    db_opinion = crud.opinion_cliente.get_opinion(db=db, id=id)
    if db_opinion is None:
        raise HTTPException(status_code=404, detail="Opinión no encontrada")
    
    # Verificar si el usuario es el autor de la opinion
    if db_opinion.Usuario_ID != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes actualizar tus propias opiniones")
    
    # No permitir actualizar si ya ha sido respondida
    if db_opinion.Estatus:
        raise HTTPException(status_code=400, detail="No puedes modificar una opinión que ya ha sido respondida")
    
    return crud.opinion_cliente.update_opinion(db=db, id=id, opinion=opinion)

# Ruta para responder a una opinion (solo administradores)
@opinion_cliente_router.put('/opiniones/{id}/responder', response_model=schemas.opinion_cliente.OpinionCliente, tags=['Opiniones'], dependencies=[Depends(Portador())])
def responder_opinion(id: int, respuesta: schemas.opinion_cliente.OpinionClienteRespuesta, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar si el usuario es administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden responder a las opiniones")
    
    # Obtener la opinion
    db_opinion = crud.opinion_cliente.get_opinion(db=db, id=id)
    if db_opinion is None:
        raise HTTPException(status_code=404, detail="Opinión no encontrada")
    
    return crud.opinion_cliente.responder_opinion(db=db, id=id, respuesta=respuesta, respuesta_usuario_id=user_id)

# Ruta para eliminar una opinion
@opinion_cliente_router.delete('/opiniones/{id}', response_model=schemas.opinion_cliente.OpinionCliente, tags=['Opiniones'], dependencies=[Depends(Portador())])
def delete_opinion(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la opinion
    db_opinion = crud.opinion_cliente.get_opinion(db=db, id=id)
    if db_opinion is None:
        raise HTTPException(status_code=404, detail="Opinión no encontrada")
    
    # Verificar si el usuario es el autor de la opinión o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if db_opinion.Usuario_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propias opiniones o ser administrador")
    
    return crud.opinion_cliente.delete_opinion(db=db, id=id)

# Ruta para obtener mis opiniones
@opinion_cliente_router.get('/mis-opiniones/', response_model=List[schemas.opinion_cliente.OpinionCliente], tags=['Opiniones'], dependencies=[Depends(Portador())])
def read_mis_opiniones(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return crud.opinion_cliente.get_opiniones_by_usuario(db=db, usuario_id=user_id, skip=skip, limit=limit)

# Ruta para obtener todas las opiniones (solo administradores)
@opinion_cliente_router.get('/opiniones/', response_model=List[schemas.opinion_cliente.OpinionCliente], tags=['Opiniones'], dependencies=[Depends(Portador())])
def read_opiniones(
    skip: int = 0, 
    limit: int = 10, 
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de opinión"),
    sin_responder: bool = Query(False, description="Mostrar solo opiniones sin responder"),
    db: Session = Depends(get_db), 
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar si el usuario es administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver todas las opiniones")
    
    # Aplicar filtros
    if sin_responder:
        return crud.opinion_cliente.get_opiniones_sin_responder(db=db, skip=skip, limit=limit)
    elif tipo:
        return crud.opinion_cliente.get_opiniones_by_tipo(db=db, tipo=tipo, skip=skip, limit=limit)
    else:
        return crud.opinion_cliente.get_opiniones(db=db, skip=skip, limit=limit)

# Ruta para obtener opiniones con detalles (solo administradores)
@opinion_cliente_router.get('/opiniones/detalles/', tags=['Opiniones'], dependencies=[Depends(Portador())])
def read_opiniones_with_details(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar si el usuario es administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden ver detalles de todas las opiniones")
    
    return crud.opinion_cliente.get_opiniones_with_details(db=db, skip=skip, limit=limit)