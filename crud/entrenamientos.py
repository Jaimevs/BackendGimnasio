from sqlalchemy.orm import Session
import models.entrenamientos
import schemas.entrenamientos
from typing import List

# Obtener todos los entrenamientos
def get_entrenamientos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.entrenamientos.Entrenamiento).offset(skip).limit(limit).all()

# Obtener entrenamientos por usuario
def get_entrenamientos_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.entrenamientos.Entrenamiento).filter(
        models.entrenamientos.Entrenamiento.ID_Usuario == usuario_id
    ).offset(skip).limit(limit).all()

# Obtener un entrenamiento por ID
def get_entrenamiento(db: Session, id: int):
    return db.query(models.entrenamientos.Entrenamiento).filter(
        models.entrenamientos.Entrenamiento.ID == id
    ).first()

# Crear un entrenamiento
def create_entrenamiento(db: Session, entrenamiento: schemas.entrenamientos.EntrenamientoCreate):
    # Crear el entrenamiento
    db_entrenamiento = models.entrenamientos.Entrenamiento(
        Nombre=entrenamiento.Nombre,
        Fecha=entrenamiento.Fecha,
        ID_Usuario=entrenamiento.ID_Usuario
    )
    db.add(db_entrenamiento)
    db.commit()
    db.refresh(db_entrenamiento)
    
    # Agregar los ejercicios al entrenamiento
    for ejercicio_id in entrenamiento.ejercicios_ids:
        db_entrenamiento_ejercicio = models.entrenamientos.EntrenamientoEjercicios(
            ID_Entrenamiento=db_entrenamiento.ID,
            ID_Ejercicio=ejercicio_id
        )
        db.add(db_entrenamiento_ejercicio)
    
    db.commit()
    db.refresh(db_entrenamiento)
    return db_entrenamiento

# Actualizar un entrenamiento
def update_entrenamiento(db: Session, id: int, entrenamiento: schemas.entrenamientos.EntrenamientoUpdate):
    db_entrenamiento = get_entrenamiento(db=db, id=id)
    if db_entrenamiento is None:
        return None
    
    # Actualizar campos básicos
    if entrenamiento.Nombre is not None:
        db_entrenamiento.Nombre = entrenamiento.Nombre
    if entrenamiento.Fecha is not None:
        db_entrenamiento.Fecha = entrenamiento.Fecha
    
    # Actualizar ejercicios si se proporciona una nueva lista
    if entrenamiento.ejercicios_ids is not None:
        # Eliminar relaciones existentes
        db.query(models.entrenamientos.EntrenamientoEjercicios).filter(
            models.entrenamientos.EntrenamientoEjercicios.ID_Entrenamiento == id
        ).delete()
        
        # Agregar nuevas relaciones
        for ejercicio_id in entrenamiento.ejercicios_ids:
            db_entrenamiento_ejercicio = models.entrenamientos.EntrenamientoEjercicios(
                ID_Entrenamiento=id,
                ID_Ejercicio=ejercicio_id
            )
            db.add(db_entrenamiento_ejercicio)
    
    db.commit()
    db.refresh(db_entrenamiento)
    return db_entrenamiento

# Eliminar un entrenamiento
def delete_entrenamiento(db: Session, id: int):
    db_entrenamiento = get_entrenamiento(db=db, id=id)
    if db_entrenamiento is None:
        return None
    
    # Eliminar primero las relaciones con ejercicios
    db.query(models.entrenamientos.EntrenamientoEjercicios).filter(
        models.entrenamientos.EntrenamientoEjercicios.ID_Entrenamiento == id
    ).delete()
    
    # Eliminar el entrenamiento
    db.delete(db_entrenamiento)
    db.commit()
    return db_entrenamiento