from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db, engine
from portadortoken import Portador
import crud.evaluaciones_serv
import crud.servicios
import schemas.evaluaciones_serv
import models.users
import models.evaluaciones_serv
import models.servicios
import models.usersrols
from datetime import datetime

evaluaciones_router = APIRouter()

# Crear las tablas si no existen
models.evaluaciones_serv.Base.metadata.create_all(bind=engine)

# Ruta para obtener una evaluación específica
@evaluaciones_router.get('/evaluaciones/{id}', response_model=schemas.evaluaciones_serv.EvaluacionServ, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def read_evaluacion(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la evaluación
    db_evaluacion = crud.evaluaciones_serv.get_evaluacion(db=db, id=id)
    if db_evaluacion is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    # Verificar si el usuario es el autor de la evaluación o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Aquí se verifica que el usuario sea el autor de la evaluación
    # Como el Usuario_ID está relacionado con tbd_usuarios_roles, debemos hacer la verificación adecuada
    user_roles = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == user_id).all()
    user_rol_ids = [ur.Usuario_ID for ur in user_roles]
    
    if db_evaluacion.Usuario_ID not in user_rol_ids and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta evaluación")
    
    return db_evaluacion

# Ruta para crear una evaluación
@evaluaciones_router.post('/evaluaciones/', response_model=schemas.evaluaciones_serv.EvaluacionServ, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def create_evaluacion(evaluacion: schemas.evaluaciones_serv.EvaluacionServCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el servicio exista
    servicio = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == evaluacion.Servicio_ID).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    # Verificar que el servicio esté activo
    if not servicio.Estatus:
        raise HTTPException(status_code=400, detail="No se puede evaluar un servicio inactivo")
    
    # Verificar que la calificación esté entre 1 y 5
    if evaluacion.Calificacion < 1 or evaluacion.Calificacion > 5:
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5 estrellas")
    
    # Obtener el ID del rol del usuario
    user_rol = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == user_id).first()
    if not user_rol:
        raise HTTPException(status_code=404, detail="Rol de usuario no encontrado")
    
    return crud.evaluaciones_serv.create_evaluacion(db=db, evaluacion=evaluacion, usuario_id=user_rol.Usuario_ID)

# Ruta para actualizar una evaluación
@evaluaciones_router.put('/evaluaciones/{id}', response_model=schemas.evaluaciones_serv.EvaluacionServ, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def update_evaluacion(id: int, evaluacion: schemas.evaluaciones_serv.EvaluacionServUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la evaluación
    db_evaluacion = crud.evaluaciones_serv.get_evaluacion(db=db, id=id)
    if db_evaluacion is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    # Verificar si el usuario es el autor de la evaluación
    user_roles = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == user_id).all()
    user_rol_ids = [ur.Usuario_ID for ur in user_roles]
    
    if db_evaluacion.Usuario_ID not in user_rol_ids:
        raise HTTPException(status_code=403, detail="Solo puedes actualizar tus propias evaluaciones")
    
    # Verificar que la calificación esté entre 1 y 5 si se proporciona
    if evaluacion.Calificacion is not None and (evaluacion.Calificacion < 1 or evaluacion.Calificacion > 5):
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5 estrellas")
    
    # Si se actualiza el servicio, verificar que exista
    if evaluacion.Servicio_ID is not None:
        servicio = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == evaluacion.Servicio_ID).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
        # Verificar que el servicio esté activo
        if not servicio.Estatus:
            raise HTTPException(status_code=400, detail="No se puede evaluar un servicio inactivo")
    
    return crud.evaluaciones_serv.update_evaluacion(db=db, id=id, evaluacion=evaluacion)

# Ruta para eliminar una evaluación
@evaluaciones_router.delete('/evaluaciones/{id}', response_model=schemas.evaluaciones_serv.EvaluacionServ, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def delete_evaluacion(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la evaluación
    db_evaluacion = crud.evaluaciones_serv.get_evaluacion(db=db, id=id)
    if db_evaluacion is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    # Verificar si el usuario es el autor de la evaluación o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Verificar los roles del usuario
    user_roles = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == user_id).all()
    user_rol_ids = [ur.Usuario_ID for ur in user_roles]
    
    if db_evaluacion.Usuario_ID not in user_rol_ids and not is_admin:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propias evaluaciones o ser administrador")
    
    return crud.evaluaciones_serv.delete_evaluacion(db=db, id=id)

# Ruta para obtener mis evaluaciones
@evaluaciones_router.get('/mis-evaluaciones/', response_model=List[schemas.evaluaciones_serv.EvaluacionServ], tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def read_mis_evaluaciones(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener el ID del rol del usuario
    user_rol = db.query(models.usersrols.UserRol).filter(models.usersrols.UserRol.Usuario_ID == user_id).first()
    if not user_rol:
        return []
    
    return crud.evaluaciones_serv.get_evaluaciones_by_usuario(db=db, usuario_id=user_rol.Usuario_ID, skip=skip, limit=limit)

# Ruta para obtener todas las evaluaciones por servicio
@evaluaciones_router.get('/evaluaciones/servicio/{servicio_id}', response_model=List[schemas.evaluaciones_serv.EvaluacionServ], tags=['Evaluaciones'])
def read_evaluaciones_by_servicio(servicio_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Verificar que el servicio exista
    servicio = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
    return crud.evaluaciones_serv.get_evaluaciones_by_servicio(db=db, servicio_id=servicio_id, skip=skip, limit=limit)

# Ruta para obtener estadísticas de evaluaciones por servicio
@evaluaciones_router.get('/evaluaciones/servicio/{servicio_id}/estadisticas', tags=['Evaluaciones'])
def get_estadisticas_servicio(servicio_id: int, db: Session = Depends(get_db)):
    # Verificar que el servicio exista
    servicio = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
    return crud.evaluaciones_serv.get_estadisticas_servicio(db=db, servicio_id=servicio_id)