# routes/reservaciones.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db
from portadortoken import Portador
from jwt_config import decode_token
import crud.reservaciones
import crud.clases
import schemas.reservaciones
import models.users
import models.clases
from config.db import get_db, engine
import models.reservaciones
from datetime import datetime, date, timedelta
from sqlalchemy import func

reservacion_router = APIRouter()

# Crear la tabla si no existe
models.reservaciones.Base.metadata.create_all(bind=engine)

# Ruta para obtener una reservación por ID con detalles
@reservacion_router.get('/reservaciones/{id}/with-details/', tags=['Reservaciones'], dependencies=[Depends(Portador())])
def read_reservacion_with_details(
    id: int, 
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la reservación con detalles
    db_reservacion = crud.reservaciones.get_reservacion_with_details(db=db, id=id)
    if db_reservacion is None:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Verificar que sea el usuario dueño de la reservación o un administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Verificar si es el dueño de la reservación o un administrador
    if db_reservacion["Usuario_ID"] != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta reservación")
    
    return db_reservacion

# Ruta para obtener reservaciones del usuario actual
@reservacion_router.get('/mis-reservaciones/', tags=['Reservaciones'], dependencies=[Depends(Portador())])
def read_mis_reservaciones(
    skip: int = 0, 
    limit: int = 10,
    fecha_inicio: Optional[date] = Query(None, description="Filtrar desde esta fecha"),
    fecha_fin: Optional[date] = Query(None, description="Filtrar hasta esta fecha"),
    estatus: Optional[str] = Query(None, description="Filtrar por estatus (Confirmada, Cancelada, Asistida, No Asistida)"),
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener usuario
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Consulta base
    query = db.query(
        models.reservaciones.Reservacion,
        models.clases.Clase.Nombre.label("nombre_clase"),
        models.clases.Clase.Dia_Inicio.label("dia_clase"),
        models.clases.Clase.Hora_Inicio,
        models.clases.Clase.Hora_Fin,
        models.users.User.Nombre_Usuario.label("entrenador_nombre")
    ).join(
        models.clases.Clase, models.reservaciones.Reservacion.Clase_ID == models.clases.Clase.ID
    ).join(
        models.users.User, models.clases.Clase.Entrenador_ID == models.users.User.ID, isouter=True
    ).filter(
        models.reservaciones.Reservacion.Usuario_ID == user_id
    )
    
    # Aplicar filtros si están presentes
    if fecha_inicio:
        query = query.filter(models.reservaciones.Reservacion.Fecha_Reservacion >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(models.reservaciones.Reservacion.Fecha_Reservacion <= fecha_fin)
    
    if estatus:
        query = query.filter(models.reservaciones.Reservacion.Estatus == estatus)
    
    # Ejecutar consulta
    results = query.offset(skip).limit(limit).all()
    
    # Construir respuesta
    reservaciones_con_detalles = []
    for result in results:
        reservacion = result[0]
        reservaciones_con_detalles.append({
            "ID": reservacion.ID,
            "Usuario_ID": reservacion.Usuario_ID,
            "Clase_ID": reservacion.Clase_ID,
            "Fecha_Reservacion": reservacion.Fecha_Reservacion,
            "Estatus": reservacion.Estatus,
            "Comentario": reservacion.Comentario,
            "Fecha_Registro": reservacion.Fecha_Registro,
            "Fecha_Actualizacion": reservacion.Fecha_Actualizacion,
            "Nombre_Clase": result[1],
            "Dia_Clase": result[2],
            "Hora_Inicio": result[3],
            "Hora_Fin": result[4],
            "Entrenador_Nombre": result[5]
        })
    
    return reservaciones_con_detalles

# Ruta para obtener reservaciones de una clase específica (para entrenadores)
@reservacion_router.get('/reservaciones/clase/{clase_id}', tags=['Reservaciones'], dependencies=[Depends(Portador())])
def read_reservaciones_by_clase(
    clase_id: int, 
    skip: int = 0, 
    limit: int = 10,
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la clase
    db_clase = crud.clases.get_clase(db=db, id=clase_id)
    if db_clase is None:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    # Verificar que el usuario sea el entrenador de la clase o un administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Verificar si es el entrenador de la clase o un administrador
    if db_clase.Entrenador_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Solo el entrenador de la clase o un administrador puede ver las reservaciones")
    
    # Consulta base
    query = db.query(
        models.reservaciones.Reservacion,
        models.users.User.Nombre_Usuario,
        models.clases.Clase.Nombre.label("nombre_clase")
    ).join(
        models.users.User, models.reservaciones.Reservacion.Usuario_ID == models.users.User.ID
    ).join(
        models.clases.Clase, models.reservaciones.Reservacion.Clase_ID == models.clases.Clase.ID
    ).filter(
        models.reservaciones.Reservacion.Clase_ID == clase_id
    )
    
    # Aplicar filtro de fecha si está presente
    if fecha:
        query = query.filter(func.date(models.reservaciones.Reservacion.Fecha_Reservacion) == fecha)
    
    # Ejecutar consulta
    results = query.offset(skip).limit(limit).all()
    
    # Construir respuesta
    reservaciones_con_detalles = []
    for result in results:
        reservacion = result[0]
        reservaciones_con_detalles.append({
            "ID": reservacion.ID,
            "Usuario_ID": reservacion.Usuario_ID,
            "Clase_ID": reservacion.Clase_ID,
            "Fecha_Reservacion": reservacion.Fecha_Reservacion,
            "Estatus": reservacion.Estatus,
            "Comentario": reservacion.Comentario,
            "Fecha_Registro": reservacion.Fecha_Registro,
            "Fecha_Actualizacion": reservacion.Fecha_Actualizacion,
            "Nombre_Usuario": result[1],
            "Nombre_Clase": result[2]
        })
    
    return reservaciones_con_detalles

# Ruta para crear una nueva reservación
@reservacion_router.post('/reservaciones/', response_model=schemas.reservaciones.Reservacion, tags=['Reservaciones'], dependencies=[Depends(Portador())])
def create_reservacion(
    reservacion: schemas.reservaciones.ReservacionCreate, 
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar si el usuario está creando una reservación para sí mismo o si es un administrador
    if reservacion.Usuario_ID != user_id:
        user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        is_admin = False
        for rol in user.roles:
            if rol.Nombre == "admin":
                is_admin = True
                break
        
        if not is_admin:
            raise HTTPException(status_code=403, detail="Solo puedes crear reservaciones para ti mismo")
    
    # Verificar que la clase exista
    db_clase = crud.clases.get_clase(db=db, id=reservacion.Clase_ID)
    if db_clase is None:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    # Verificar que la clase esté activa
    if not db_clase.Estatus:
        raise HTTPException(status_code=400, detail="La clase no está disponible para reservaciones")
    
    # Verificar si ya existe una reservación para esta clase en la misma fecha
    if crud.reservaciones.check_reservacion_exists(
        db=db, 
        usuario_id=reservacion.Usuario_ID, 
        clase_id=reservacion.Clase_ID, 
        fecha_reservacion=reservacion.Fecha_Reservacion
    ):
        raise HTTPException(status_code=400, detail="Ya tienes una reservación para esta clase en la misma fecha")
    
    # Crear la reservación
    return crud.reservaciones.create_reservacion(db=db, reservacion=reservacion)

# Ruta para actualizar una reservación
@reservacion_router.put('/reservaciones/{id}', response_model=schemas.reservaciones.Reservacion, tags=['Reservaciones'], dependencies=[Depends(Portador())])
def update_reservacion(
    id: int, 
    reservacion: schemas.reservaciones.ReservacionUpdate, 
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la reservación
    db_reservacion = crud.reservaciones.get_reservacion(db=db, id=id)
    if db_reservacion is None:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Verificar que sea el usuario dueño de la reservación o un administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Verificar si es el dueño de la reservación o un administrador o el entrenador de la clase
    is_entrenador = False
    db_clase = crud.clases.get_clase(db=db, id=db_reservacion.Clase_ID)
    if db_clase and db_clase.Entrenador_ID == user_id:
        is_entrenador = True
    
    if db_reservacion.Usuario_ID != user_id and not is_admin and not is_entrenador:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar esta reservación")
    
    # Si está cambiando el estatus a "Asistida" o "No Asistida", verificar que sea entrenador o admin
    if reservacion.Estatus in ["Asistida", "No Asistida"] and not (is_admin or is_entrenador):
        raise HTTPException(status_code=403, detail="Solo el entrenador o un administrador puede marcar la asistencia")
    
    return crud.reservaciones.update_reservacion(db=db, id=id, reservacion=reservacion)

# Ruta para cancelar una reservación
@reservacion_router.put('/reservaciones/{id}/cancelar', response_model=schemas.reservaciones.Reservacion, tags=['Reservaciones'], dependencies=[Depends(Portador())])
def cancel_reservacion(
    id: int, 
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la reservación
    db_reservacion = crud.reservaciones.get_reservacion(db=db, id=id)
    if db_reservacion is None:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Verificar que sea el usuario dueño de la reservación o un administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Verificar si es el dueño de la reservación o un administrador
    if db_reservacion.Usuario_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta reservación")
    
    # No permitir cancelar si ya está cancelada o asistida
    if db_reservacion.Estatus in ["Cancelada", "Asistida", "No Asistida"]:
        raise HTTPException(status_code=400, detail=f"No se puede cancelar una reservación con estatus '{db_reservacion.Estatus}'")
    
    return crud.reservaciones.cancel_reservacion(db=db, id=id)

# Ruta para marcar asistencia a una reservación (solo entrenadores y admin)
@reservacion_router.put('/reservaciones/{id}/asistencia', tags=['Reservaciones'], dependencies=[Depends(Portador())])
def mark_attendance(
    id: int,
    asistio: bool = Query(..., description="True si asistió, False si no asistió"),
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la reservación
    db_reservacion = crud.reservaciones.get_reservacion(db=db, id=id)
    if db_reservacion is None:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Verificar que sea un entrenador de la clase o un administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    # Verificar si es el entrenador de la clase o un admin
    db_clase = crud.clases.get_clase(db=db, id=db_reservacion.Clase_ID)
    is_entrenador = db_clase and db_clase.Entrenador_ID == user_id
    
    if not is_admin and not is_entrenador:
        raise HTTPException(status_code=403, detail="Solo el entrenador de la clase o un administrador puede marcar la asistencia")
    
    # No permitir marcar asistencia si ya está cancelada
    if db_reservacion.Estatus == "Cancelada":
        raise HTTPException(status_code=400, detail="No se puede marcar asistencia en una reservación cancelada")
    
    return crud.reservaciones.mark_attendance(db=db, id=id, asistio=asistio)