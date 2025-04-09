from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db, engine
from portadortoken import Portador
import crud.servicios
import crud.evaluaciones_serv
import schemas.servicios
import models.users
import models.usersrols
import models.servicios
from datetime import datetime

servicios_router = APIRouter()

# Crear las tablas si no existen
models.servicios.Base.metadata.create_all(bind=engine)

# Ruta para obtener todos los servicios (accesible para todos)
@servicios_router.get('/servicios/', response_model=List[schemas.servicios.Servicio], tags=['Servicios'])
def read_servicios(skip: int = 0, limit: int = 10, estatus: Optional[bool] = True, db: Session = Depends(get_db)):
    return crud.servicios.get_servicios(db=db, skip=skip, limit=limit, estatus=estatus)

# Ruta para obtener un servicio específico (accesible para todos)
@servicios_router.get('/servicios/{id}', response_model=schemas.servicios.Servicio, tags=['Servicios'])
def read_servicio(id: int, db: Session = Depends(get_db)):
    db_servicio = crud.servicios.get_servicio(db=db, id=id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

# Ruta para crear un servicio (solo admin)
@servicios_router.post('/servicios/', response_model=schemas.servicios.Servicio, tags=['Servicios Admin'], dependencies=[Depends(Portador())])
def create_servicio(servicio: schemas.servicios.ServicioCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario sea administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear servicios")
    
    # Obtener el rol de usuario administrador
    user_rol = db.query(models.usersrols.UserRol).filter(
        models.usersrols.UserRol.Usuario_ID == user_id
    ).first()
    
    if not user_rol:
        raise HTTPException(status_code=404, detail="Rol de usuario no encontrado")
    
    return crud.servicios.create_servicio(db=db, servicio=servicio, usuario_id=user_rol.Usuario_ID)

# Ruta para actualizar un servicio (solo admin)
@servicios_router.put('/servicios/{id}', response_model=schemas.servicios.Servicio, tags=['Servicios Admin'], dependencies=[Depends(Portador())])
def update_servicio(id: int, servicio: schemas.servicios.ServicioUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario sea administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden actualizar servicios")
    
    # Verificar que el servicio exista
    db_servicio = crud.servicios.get_servicio(db=db, id=id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    return crud.servicios.update_servicio(db=db, id=id, servicio=servicio)

# Ruta para eliminar un servicio (solo admin)
@servicios_router.delete('/servicios/{id}', response_model=schemas.servicios.Servicio, tags=['Servicios Admin'], dependencies=[Depends(Portador())])
def delete_servicio(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario sea administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar servicios")
    
    # Verificar que el servicio exista
    db_servicio = crud.servicios.get_servicio(db=db, id=id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    # Verificar si hay evaluaciones asociadas al servicio
    evaluaciones = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(
        models.evaluaciones_serv.Evaluaciones_serv.Servicio_ID == id
    ).count()
    
    if evaluaciones > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar el servicio porque tiene {evaluaciones} evaluaciones asociadas. Considere desactivarlo en su lugar."
        )
    
    return crud.servicios.delete_servicio(db=db, id=id)

# Ruta para obtener servicios con detalles (solo admin)
@servicios_router.get('/admin/servicios/', tags=['Servicios Admin'], dependencies=[Depends(Portador())])
def get_servicios_admin(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario sea administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden acceder a esta información")
    
    return crud.servicios.get_servicios_with_details(db=db, skip=skip, limit=limit)

# Ruta para buscar servicios por rango de precio
@servicios_router.get('/servicios/buscar/', response_model=List[schemas.servicios.Servicio], tags=['Servicios'])
def search_servicios(
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="El precio mínimo no puede ser mayor que el precio máximo")
    
    return crud.servicios.get_servicios_by_price_range(
        db=db, 
        min_price=min_price, 
        max_price=max_price, 
        skip=skip, 
        limit=limit
    )

# Ruta para obtener los servicios mejor evaluados
@servicios_router.get('/servicios/top-rated/', response_model=List[schemas.servicios.Servicio], tags=['Servicios'])
def get_top_rated_servicios(limit: int = 5, db: Session = Depends(get_db)):
    return crud.servicios.get_top_rated_servicios(db=db, limit=limit)