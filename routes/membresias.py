from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db, engine
from portadortoken import Portador
import crud.membresias
import schemas.membresias
import models.users
import models.usersrols
import models.membresias
from datetime import datetime

membresias_router = APIRouter()

models.membresias.Base.metadata.create_all(bind=engine)

# Ruta para que un usuario vea su propia membresía
@membresias_router.get('/mi-membresia/', response_model=schemas.membresias.Membresia, tags=['Membresías Usuario'], dependencies=[Depends(Portador())])
def read_mi_membresia(db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener el rol del usuario
    user_rol = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == user_id).first()
    if not user_rol:
        raise HTTPException(status_code=404, detail="Rol de usuario no encontrado")
    
    # Obtener la membresía del usuario
    db_membresia = crud.membresias.get_membresia_by_usuario(db=db, usuario_id=user_rol.Usuario_ID)
    if db_membresia is None:
        raise HTTPException(status_code=404, detail="No tienes una membresía activa")
    
    return db_membresia

# Ruta para que el admin vea todas las membresías (con detalles)
@membresias_router.get('/admin/membresias/', tags=['Membresías Admin'], dependencies=[Depends(Portador())])
def read_all_membresias(
    skip: int = 0, 
    limit: int = 10, 
    estatus: Optional[bool] = None,
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
    
    return crud.membresias.get_membresias_with_details(db=db, skip=skip, limit=limit)

# Ruta para que el admin cree una membresía para un usuario
@membresias_router.post('/admin/membresias/', response_model=schemas.membresias.Membresia, tags=['Membresías Admin'], dependencies=[Depends(Portador())])
def create_membresia(membresia: schemas.membresias.MembresiaCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear membresías")
    
    # Verificar que el usuario_id exista en usuarios_roles
    user_rol = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == membresia.Usuario_ID).first()
    if not user_rol:
        raise HTTPException(status_code=404, detail="El usuario especificado no existe o no tiene un rol asignado")
    
    # Verificar si el usuario ya tiene una membresía activa
    existente = crud.membresias.get_membresia_by_usuario(db=db, usuario_id=membresia.Usuario_ID)
    if existente and existente.Estatus:
        raise HTTPException(
            status_code=400, 
            detail=f"El usuario ya tiene una membresía activa (ID: {existente.ID}). Actualice o desactive esa membresía primero."
        )
    
    # Verificar que el código sea único
    codigo_existente = db.query(models.membresias.Membresia).filter(models.membresias.Membresia.Codigo == membresia.Codigo).first()
    if codigo_existente:
        raise HTTPException(status_code=400, detail="Ya existe una membresía con ese código")
    
    # Verificar que la fecha de inicio sea válida
    if membresia.Fecha_Inicio and membresia.Fecha_Fin and membresia.Fecha_Inicio > membresia.Fecha_Fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin")
    
    return crud.membresias.create_membresia(db=db, membresia=membresia)

# Ruta para que el admin actualice una membresía
@membresias_router.put('/admin/membresias/{id}', response_model=schemas.membresias.Membresia, tags=['Membresías Admin'], dependencies=[Depends(Portador())])
def update_membresia(id: int, membresia: schemas.membresias.MembresiaUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
        raise HTTPException(status_code=403, detail="Solo los administradores pueden actualizar membresías")
    
    # Verificar que la membresía exista
    db_membresia = crud.membresias.get_membresia(db=db, id=id)
    if db_membresia is None:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    
    # Verificar que el código sea único si se está actualizando
    if membresia.Codigo and membresia.Codigo != db_membresia.Codigo:
        codigo_existente = db.query(models.membresias.Membresia).filter(
            models.membresias.Membresia.Codigo == membresia.Codigo,
            models.membresias.Membresia.ID != id
        ).first()
        if codigo_existente:
            raise HTTPException(status_code=400, detail="Ya existe otra membresía con ese código")
    
    # Verificar fechas de inicio y fin
    nueva_fecha_inicio = membresia.Fecha_Inicio if membresia.Fecha_Inicio is not None else db_membresia.Fecha_Inicio
    nueva_fecha_fin = membresia.Fecha_Fin if membresia.Fecha_Fin is not None else db_membresia.Fecha_Fin
    
    if nueva_fecha_inicio and nueva_fecha_fin and nueva_fecha_inicio > nueva_fecha_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin")
    
    return crud.membresias.update_membresia(db=db, id=id, membresia=membresia)

# Ruta para que el admin elimine una membresía
@membresias_router.delete('/admin/membresias/{id}', response_model=schemas.membresias.Membresia, tags=['Membresías Admin'], dependencies=[Depends(Portador())])
def delete_membresia(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
        raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar membresías")
    
    # Verificar que la membresía exista
    db_membresia = crud.membresias.get_membresia(db=db, id=id)
    if db_membresia is None:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    
    return crud.membresias.delete_membresia(db=db, id=id)

# Ruta para obtener usuarios con rol "usuario"
@membresias_router.get('/admin/usuarios-disponibles/', response_model=List[dict], tags=['Membresías Admin'], dependencies=[Depends(Portador())])
def get_usuarios_disponibles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
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
    
    usuarios = crud.membresias.get_usuarios_rol_usuario(db=db, skip=skip, limit=limit)
    
    # Convertir resultado a formato dict para la respuesta
    resultado = []
    for usuario in usuarios:
        # Verificar si el usuario ya tiene una membresía activa
        membresia = db.query(models.membresias.Membresia).filter(
            models.membresias.Membresia.Usuario_ID == usuario.ID,
            models.membresias.Membresia.Estatus == True
        ).first()
        
        resultado.append({
            "id": usuario.ID,
            "nombre_usuario": usuario.Nombre_Usuario,
            "correo_electronico": usuario.Correo_Electronico,
            "tiene_membresia_activa": membresia is not None
        })
    
    return resultado

# Ruta para obtener usuarios con una membresía específica
@membresias_router.get('/admin/usuarios-membresia/', response_model=List[dict], tags=['Membresías Admin'], dependencies=[Depends(Portador())])
def get_usuarios_con_membresia(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de membresía"),
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
    
    return crud.membresias.get_usuarios_por_membresia(db=db, tipo_membresia=tipo, skip=skip, limit=limit)