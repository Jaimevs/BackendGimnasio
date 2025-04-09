from sqlalchemy.orm import Session
import models.servicios
import models.evaluaciones_serv
import models.users
import models.usersrols
import schemas.servicios
from datetime import datetime
from sqlalchemy import func

# Buscar por ID
def get_servicio(db: Session, id: int):
    return db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == id).first()

# Buscar todos los servicios
def get_servicios(db: Session, skip: int = 0, limit: int = 10, estatus: bool = None):
    query = db.query(models.servicios.Servicios)
    
    if estatus is not None:
        query = query.filter(models.servicios.Servicios.Estatus == estatus)
    
    return query.offset(skip).limit(limit).all()

# Buscar servicios por usuario
def get_servicios_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.servicios.Servicios).filter(
        models.servicios.Servicios.Usuario_ID == usuario_id
    ).offset(skip).limit(limit).all()

# Crear nuevo servicio
def create_servicio(db: Session, servicio: schemas.servicios.ServicioCreate, usuario_id: int):
    db_servicio = models.servicios.Servicios(
        Nombre=servicio.Nombre,
        Descripcion=servicio.Descripcion,
        Costo=servicio.Costo,
        # Area_ID=servicio.Area_ID,  # Comentado por ahora
        Usuario_ID=usuario_id,
        Estatus=servicio.Estatus if servicio.Estatus is not None else True,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_servicio)
    db.commit()
    db.refresh(db_servicio)
    return db_servicio

# Actualizar servicio por ID
def update_servicio(db: Session, id: int, servicio: schemas.servicios.ServicioUpdate):
    db_servicio = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == id).first()
    if db_servicio:
        for var, value in vars(servicio).items():
            if value is not None and hasattr(db_servicio, var):
                setattr(db_servicio, var, value)
        
        # Actualizar fecha de actualización
        db_servicio.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_servicio)
    return db_servicio

# Eliminar servicio por ID
def delete_servicio(db: Session, id: int):
    db_servicio = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.ID == id).first()
    if db_servicio:
        db.delete(db_servicio)
        db.commit()
    return db_servicio

# Obtener servicios con información detallada
def get_servicios_with_details(db: Session, skip: int = 0, limit: int = 10):
    servicios = db.query(models.servicios.Servicios).offset(skip).limit(limit).all()
    
    servicios_con_detalles = []
    for servicio in servicios:
        # Obtener usuario/rol creador
        user_rol = db.query(models.usersrols.UserRol).filter(
            models.usersrols.UserRol.Usuario_ID == servicio.Usuario_ID
        ).first()
        
        # Obtener usuario
        user_nombre = "Desconocido"
        if user_rol:
            user = db.query(models.users.User).filter(models.users.User.ID == user_rol.Usuario_ID).first()
            if user:
                user_nombre = user.Nombre_Usuario
        
        # Obtener estadísticas de evaluaciones
        evaluaciones = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(
            models.evaluaciones_serv.Evaluaciones_serv.Servicio_ID == servicio.ID
        ).all()
        
        total_evaluaciones = len(evaluaciones)
        promedio_calificacion = 0.0
        
        if total_evaluaciones > 0:
            suma_calificaciones = sum(eval.Calificacion for eval in evaluaciones)
            promedio_calificacion = round(suma_calificaciones / total_evaluaciones, 2)
        
        servicios_con_detalles.append({
            "ID": servicio.ID,
            "Nombre": servicio.Nombre,
            "Descripcion": servicio.Descripcion,
            "Costo": servicio.Costo,
            "Usuario_ID": servicio.Usuario_ID,
            "Estatus": servicio.Estatus,
            "Fecha_Registro": servicio.Fecha_Registro,
            "Fecha_Actualizacion": servicio.Fecha_Actualizacion,
            "Usuario_Nombre": user_nombre,
            "Total_Evaluaciones": total_evaluaciones,
            "Promedio_Calificacion": promedio_calificacion
        })
    
    return servicios_con_detalles

# Buscar servicios por precio (rango)
def get_servicios_by_price_range(db: Session, min_price: float = None, max_price: float = None, skip: int = 0, limit: int = 10):
    query = db.query(models.servicios.Servicios)
    
    if min_price is not None:
        query = query.filter(models.servicios.Servicios.Costo >= min_price)
    
    if max_price is not None:
        query = query.filter(models.servicios.Servicios.Costo <= max_price)
    
    return query.offset(skip).limit(limit).all()

# Buscar servicios mejor evaluados
def get_top_rated_servicios(db: Session, limit: int = 5):
    # Obtener todos los servicios
    servicios = db.query(models.servicios.Servicios).filter(models.servicios.Servicios.Estatus == True).all()
    
    # Para cada servicio, calcular su calificación promedio
    servicios_rating = []
    for servicio in servicios:
        evaluaciones = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(
            models.evaluaciones_serv.Evaluaciones_serv.Servicio_ID == servicio.ID,
            models.evaluaciones_serv.Evaluaciones_serv.Estatus == True
        ).all()
        
        total_evaluaciones = len(evaluaciones)
        promedio = 0.0
        
        if total_evaluaciones > 0:
            suma = sum(eval.Calificacion for eval in evaluaciones)
            promedio = suma / total_evaluaciones
        
        servicios_rating.append({
            "servicio": servicio,
            "promedio": promedio,
            "total_evaluaciones": total_evaluaciones
        })
    
    # Ordenar por promedio (descendente) y luego por total de evaluaciones (descendente)
    servicios_rating.sort(key=lambda x: (x["promedio"], x["total_evaluaciones"]), reverse=True)
    
    # Devolver los top N servicios
    return [item["servicio"] for item in servicios_rating[:limit]]