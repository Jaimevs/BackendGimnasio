from sqlalchemy.orm import Session
import models.evaluaciones_serv
import models.servicios
import models.users
import models.usersrols
import schemas.evaluaciones_serv
from datetime import datetime

# Buscar por ID
def get_evaluacion(db: Session, id: int):
    return db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(models.evaluaciones_serv.Evaluaciones_serv.ID == id).first()

# Buscar todas las evaluaciones
def get_evaluaciones(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.evaluaciones_serv.Evaluaciones_serv).offset(skip).limit(limit).all()

# Buscar evaluaciones por usuario
def get_evaluaciones_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(
        models.evaluaciones_serv.Evaluaciones_serv.Usuario_ID == usuario_id
    ).offset(skip).limit(limit).all()

# Buscar evaluaciones por servicio
def get_evaluaciones_by_servicio(db: Session, servicio_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(
        models.evaluaciones_serv.Evaluaciones_serv.Servicio_ID == servicio_id
    ).offset(skip).limit(limit).all()

# Crear nueva evaluación
def create_evaluacion(db: Session, evaluacion: schemas.evaluaciones_serv.EvaluacionServCreate, usuario_id: int):
    db_evaluacion = models.evaluaciones_serv.Evaluaciones_serv(
        Usuario_ID=usuario_id,
        Servicio_ID=evaluacion.Servicio_ID,
        Tipo_Servicio=evaluacion.Tipo_Servicio,
        Calificacion=evaluacion.Calificacion,
        Comentario=evaluacion.Comentario,
        Estatus=evaluacion.Estatus if evaluacion.Estatus is not None else True,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_evaluacion)
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion

# Actualizar evaluación por ID
def update_evaluacion(db: Session, id: int, evaluacion: schemas.evaluaciones_serv.EvaluacionServUpdate):
    db_evaluacion = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(models.evaluaciones_serv.Evaluaciones_serv.ID == id).first()
    if db_evaluacion:
        for var, value in vars(evaluacion).items():
            if value is not None and hasattr(db_evaluacion, var):
                setattr(db_evaluacion, var, value)
        
        # Actualizar fecha de actualización
        db_evaluacion.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_evaluacion)
    return db_evaluacion

# Eliminar evaluación por ID
def delete_evaluacion(db: Session, id: int):
    db_evaluacion = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(models.evaluaciones_serv.Evaluaciones_serv.ID == id).first()
    if db_evaluacion:
        db.delete(db_evaluacion)
        db.commit()
    return db_evaluacion

# Obtener evaluaciones con información detallada
def get_evaluaciones_with_details(db: Session, skip: int = 0, limit: int = 10):
    # Consulta con joins para obtener detalles de usuario y servicio
    results = db.query(
        models.evaluaciones_serv.Evaluaciones_serv,
        models.users.User.Nombre_Usuario.label("usuario_nombre"),
        models.servicios.Servicios.Nombre.label("servicio_nombre")
    ).join(
        models.usersrols.UserRol, models.evaluaciones_serv.Evaluaciones_serv.Usuario_ID == models.usersrols.UserRol.Usuario_ID
    ).join(
        models.users.User, models.usersrols.UserRol.Usuario_ID == models.users.User.ID
    ).join(
        models.servicios.Servicios, models.evaluaciones_serv.Evaluaciones_serv.Servicio_ID == models.servicios.Servicios.ID
    ).offset(skip).limit(limit).all()
    
    evaluaciones_con_detalles = []
    for result in results:
        evaluacion = result[0]
        evaluaciones_con_detalles.append({
            "ID": evaluacion.ID,
            "Usuario_ID": evaluacion.Usuario_ID,
            "Servicio_ID": evaluacion.Servicio_ID,
            "Tipo_Servicio": evaluacion.Tipo_Servicio.value,
            "Calificacion": evaluacion.Calificacion,
            "Comentario": evaluacion.Comentario,
            "Estatus": evaluacion.Estatus,
            "Fecha_Registro": evaluacion.Fecha_Registro,
            "Fecha_Actualizacion": evaluacion.Fecha_Actualizacion,
            "Usuario_Nombre": result[1] or "Sin nombre",
            "Servicio_Nombre": result[2] or "Sin nombre"
        })
    
    return evaluaciones_con_detalles

# Obtener estadísticas de evaluaciones por servicio
def get_estadisticas_servicio(db: Session, servicio_id: int):
    # Obtener todas las evaluaciones del servicio
    evaluaciones = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(
        models.evaluaciones_serv.Evaluaciones_serv.Servicio_ID == servicio_id
    ).all()
    
    total_evaluaciones = len(evaluaciones)
    
    if total_evaluaciones == 0:
        return {
            "servicio_id": servicio_id,
            "total_evaluaciones": 0,
            "promedio_calificacion": 0,
            "distribucion_calificaciones": {
                "5_estrellas": 0,
                "4_estrellas": 0,
                "3_estrellas": 0,
                "2_estrellas": 0,
                "1_estrella": 0
            }
        }
    
    # Calcular promedio de calificaciones
    suma_calificaciones = sum(evaluacion.Calificacion for evaluacion in evaluaciones)
    promedio_calificacion = round(suma_calificaciones / total_evaluaciones, 2)
    
    # Calcular distribución de calificaciones
    distribucion = {
        "5_estrellas": 0,
        "4_estrellas": 0,
        "3_estrellas": 0,
        "2_estrellas": 0,
        "1_estrella": 0
    }
    
    for evaluacion in evaluaciones:
        if evaluacion.Calificacion == 5:
            distribucion["5_estrellas"] += 1
        elif evaluacion.Calificacion == 4:
            distribucion["4_estrellas"] += 1
        elif evaluacion.Calificacion == 3:
            distribucion["3_estrellas"] += 1
        elif evaluacion.Calificacion == 2:
            distribucion["2_estrellas"] += 1
        elif evaluacion.Calificacion == 1:
            distribucion["1_estrella"] += 1
    
    # Calcular porcentajes
    for key in distribucion:
        distribucion[key] = round((distribucion[key] / total_evaluaciones) * 100, 2)
    
    # Obtener información del servicio
    servicio = db.query(models.servicios.Servicios).filter(
        models.servicios.Servicios.ID == servicio_id
    ).first()
    
    return {
        "servicio_id": servicio_id,
        "nombre_servicio": servicio.Nombre if servicio else "Desconocido",
        "total_evaluaciones": total_evaluaciones,
        "promedio_calificacion": promedio_calificacion,
        "distribucion_calificaciones": distribucion
    }