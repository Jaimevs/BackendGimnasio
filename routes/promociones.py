from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db, engine
from portadortoken import Portador
import crud.promociones
import schemas.promociones
import models.users
import models.usersrols
import models.promociones
from datetime import datetime

promociones_router = APIRouter()

# Crear las tablas si no existen
models.promociones.Base.metadata.create_all(bind=engine)

# Ruta para obtener todas las promociones (admin)
@promociones_router.get('/admin/promociones/', tags=['Promociones Admin'], dependencies=[Depends(Portador())])
def read_promociones_admin(
    skip: int = 0,
    limit: int = 10,
    estatus: Optional[bool] = None,
    tipo: Optional[str] = None,
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
    
    return crud.promociones.get_promociones_with_details(db=db, skip=skip, limit=limit)

# Ruta para obtener una promoción específica (admin)
@promociones_router.get('/admin/promociones/{id}', response_model=schemas.promociones.Promocion, tags=['Promociones Admin'], dependencies=[Depends(Portador())])
def read_promocion_admin(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
    
    db_promocion = crud.promociones.get_promocion(db=db, id=id)
    if db_promocion is None:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    
    return db_promocion

# Ruta para crear una promoción (admin)
@promociones_router.post('/admin/promociones/', response_model=schemas.promociones.Promocion, tags=['Promociones Admin'], dependencies=[Depends(Portador())])
def create_promocion(promocion: schemas.promociones.PromocionCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear promociones")
    
    # Verificar que el usuario_id exista en usuarios_roles
    user_rol = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == promocion.Usuario_ID).first()
    if not user_rol:
        raise HTTPException(status_code=404, detail="El usuario especificado no existe o no tiene un rol asignado")
    
    # Verificar fechas de inicio y fin
    if promocion.Fecha_Inicio and promocion.Fecha_Fin and promocion.Fecha_Inicio > promocion.Fecha_Fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin")
    
    return crud.promociones.create_promocion(db=db, promocion=promocion)

# Ruta para actualizar una promoción (admin)
@promociones_router.put('/admin/promociones/{id}', response_model=schemas.promociones.Promocion, tags=['Promociones Admin'], dependencies=[Depends(Portador())])
def update_promocion(id: int, promocion: schemas.promociones.PromocionUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
        raise HTTPException(status_code=403, detail="Solo los administradores pueden actualizar promociones")
    
    # Verificar que la promoción exista
    db_promocion = crud.promociones.get_promocion(db=db, id=id)
    if db_promocion is None:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    
    # Verificar fechas de inicio y fin
    nueva_fecha_inicio = promocion.Fecha_Inicio if promocion.Fecha_Inicio is not None else db_promocion.Fecha_Inicio
    nueva_fecha_fin = promocion.Fecha_Fin if promocion.Fecha_Fin is not None else db_promocion.Fecha_Fin
    
    if nueva_fecha_inicio and nueva_fecha_fin and nueva_fecha_inicio > nueva_fecha_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin")
    
    return crud.promociones.update_promocion(db=db, id=id, promocion=promocion)

# Ruta para eliminar una promoción (admin)
@promociones_router.delete('/admin/promociones/{id}', response_model=schemas.promociones.Promocion, tags=['Promociones Admin'], dependencies=[Depends(Portador())])
def delete_promocion(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
        raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar promociones")
    
    # Verificar que la promoción exista
    db_promocion = crud.promociones.get_promocion(db=db, id=id)
    if db_promocion is None:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    
    return crud.promociones.delete_promocion(db=db, id=id)