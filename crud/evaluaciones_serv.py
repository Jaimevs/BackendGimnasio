import models.evaluaciones_serv
import schemas.evaluaciones_serv
from sqlalchemy.orm import Session
import models, schemas

# Búsqueda por id
def get_evaluacion(db: Session, id: int):
    return db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(models.evaluaciones_serv.Evaluaciones_serv.ID == id).first()

# Buscar todas las evaluaciones con opciones de paginación
def get_evaluaciones(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.evaluaciones_serv.Evaluaciones_serv).offset(skip).limit(limit).all()

# Crear nueva evaluación
def create_evaluacion(db: Session, evaluacion: schemas.evaluaciones_serv.Evaluaciones_servCreate):
    db_evaluacion = models.evaluaciones_serv.Evaluaciones_serv(
        Usuario_ID=evaluacion.Usuario_ID,
        Servicios=evaluacion.Servicios,
        Calificacion=evaluacion.Calificacion,
        Criterio=evaluacion.Criterio,
        Estatus=evaluacion.Estatus,
        Fecha_Registro=evaluacion.Fecha_Registro
    )
    db.add(db_evaluacion)
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion

# Actualizar una evaluación por id
def update_evaluacion(db: Session, id: int, evaluacion: schemas.evaluaciones_serv.Evaluaciones_servUpdate):
    db_evaluacion = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(models.evaluaciones_serv.Evaluaciones_serv.ID == id).first()
    if db_evaluacion:
        for var, value in vars(evaluacion).items():
            setattr(db_evaluacion, var, value) if value else None
        db.commit()
        db.refresh(db_evaluacion)
    return db_evaluacion

# Eliminar una evaluación por id
def delete_evaluacion(db: Session, id: int):
    db_evaluacion = db.query(models.evaluaciones_serv.Evaluaciones_serv).filter(models.evaluaciones_serv.Evaluaciones_serv.ID == id).first()
    if db_evaluacion:
        db.delete(db_evaluacion)
        db.commit()
    return db_evaluacion
