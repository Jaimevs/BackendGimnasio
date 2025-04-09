from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import models.promociones
import models.users
import models.usersrols
import schemas.promociones
from datetime import datetime
from typing import List, Optional

# Buscar por ID
def get_promocion(db: Session, id: int):
    return db.query(models.promociones.Promocion).filter(models.promociones.Promocion.ID == id).first()

# Buscar todas las promociones
def get_promociones(db: Session, skip: int = 0, limit: int = 10, estatus: Optional[bool] = None, tipo: Optional[str] = None):
    query = db.query(models.promociones.Promocion)
    
    if estatus is not None:
        query = query.filter(models.promociones.Promocion.Estatus == estatus)
    
    if tipo is not None:
        query = query.filter(models.promociones.Promocion.Tipo == tipo)
    
    return query.offset(skip).limit(limit).all()

# Buscar promociones activas (estatus=True y fecha_fin > hoy o nula)
def get_promociones_activas(db: Session, skip: int = 0, limit: int = 10, tipo: Optional[str] = None):
    now = datetime.now()
    query = db.query(models.promociones.Promocion).filter(
        models.promociones.Promocion.Estatus == True,
        models.promociones.Promocion.Fecha_Inicio <= now,
        or_(
            models.promociones.Promocion.Fecha_Fin >= now,
            models.promociones.Promocion.Fecha_Fin == None
        )
    )
    
    if tipo is not None:
        query = query.filter(models.promociones.Promocion.Tipo == tipo)
    
    return query.offset(skip).limit(limit).all()

# Crear nueva promoción
def create_promocion(db: Session, promocion: schemas.promociones.PromocionCreate):
    db_promocion = models.promociones.Promocion(
        Usuario_ID=promocion.Usuario_ID,
        # Producto_id=promocion.Producto_id,  # Comentado por ahora
        Nombre=promocion.Nombre,
        Descripcion=promocion.Descripcion,
        Tipo=promocion.Tipo,
        Descuento=promocion.Descuento,
        Aplicacion_en=promocion.Aplicacion_en,
        Fecha_Inicio=promocion.Fecha_Inicio,
        Fecha_Fin=promocion.Fecha_Fin,
        Estatus=promocion.Estatus if promocion.Estatus is not None else True,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_promocion)
    db.commit()
    db.refresh(db_promocion)
    return db_promocion

# Actualizar promoción por ID
def update_promocion(db: Session, id: int, promocion: schemas.promociones.PromocionUpdate):
    db_promocion = db.query(models.promociones.Promocion).filter(models.promociones.Promocion.ID == id).first()
    if db_promocion:
        for var, value in vars(promocion).items():
            if value is not None and hasattr(db_promocion, var):
                setattr(db_promocion, var, value)
        
        # Actualizar fecha de actualización
        db_promocion.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_promocion)
    return db_promocion

# Eliminar promoción por ID
def delete_promocion(db: Session, id: int):
    db_promocion = db.query(models.promociones.Promocion).filter(models.promociones.Promocion.ID == id).first()
    if db_promocion:
        db.delete(db_promocion)
        db.commit()
    return db_promocion

# Obtener promociones con información detallada
def get_promociones_with_details(db: Session, skip: int = 0, limit: int = 10):
    # Consulta con joins para obtener detalles del usuario
    results = db.query(
        models.promociones.Promocion,
        models.users.User.Nombre_Usuario
    ).join(
        models.usersrols.UserRol, models.promociones.Promocion.Usuario_ID == models.usersrols.UserRol.Usuario_ID
    ).join(
        models.users.User, models.usersrols.UserRol.Usuario_ID == models.users.User.ID
    ).offset(skip).limit(limit).all()
    
    promociones_con_detalles = []
    for result in results:
        promocion = result[0]
        promociones_con_detalles.append({
            "ID": promocion.ID,
            "Usuario_ID": promocion.Usuario_ID,
            # "Producto_id": promocion.Producto_id,  # Comentado por ahora
            "Nombre": promocion.Nombre,
            "Descripcion": promocion.Descripcion,
            "Tipo": promocion.Tipo.value,
            "Descuento": promocion.Descuento,
            "Aplicacion_en": promocion.Aplicacion_en.value,
            "Fecha_Inicio": promocion.Fecha_Inicio,
            "Fecha_Fin": promocion.Fecha_Fin,
            "Estatus": promocion.Estatus,
            "Fecha_Registro": promocion.Fecha_Registro,
            "Fecha_Actualizacion": promocion.Fecha_Actualizacion,
            "Usuario_Nombre": result[1]
            # "Producto_Nombre": "No disponible"  # Comentado por ahora
        })
    
    return promociones_con_detalles