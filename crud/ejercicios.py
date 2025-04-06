from sqlalchemy.orm import Session
import models.entrenamientos
import schemas.ejercicios
from typing import List, Optional

# Obtener todos los ejercicios
def get_ejercicios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.entrenamientos.Ejercicio).offset(skip).limit(limit).all()

# Obtener ejercicios por categoría
def get_ejercicios_by_categoria(db: Session, categoria: str, skip: int = 0, limit: int = 100):
    return db.query(models.entrenamientos.Ejercicio).filter(
        models.entrenamientos.Ejercicio.Categoria == categoria
    ).offset(skip).limit(limit).all()

# Obtener un ejercicio por ID
def get_ejercicio(db: Session, id: int):
    return db.query(models.entrenamientos.Ejercicio).filter(
        models.entrenamientos.Ejercicio.ID == id
    ).first()

# Obtener un ejercicio por nombre
def get_ejercicio_by_nombre(db: Session, nombre: str):
    return db.query(models.entrenamientos.Ejercicio).filter(
        models.entrenamientos.Ejercicio.Nombre == nombre
    ).first()

# Crear un ejercicio
def create_ejercicio(db: Session, ejercicio: schemas.ejercicios.EjercicioCreate):
    db_ejercicio = models.entrenamientos.Ejercicio(
        Nombre=ejercicio.Nombre,
        Categoria=ejercicio.Categoria
    )
    db.add(db_ejercicio)
    db.commit()
    db.refresh(db_ejercicio)
    return db_ejercicio

# Actualizar un ejercicio
def update_ejercicio(db: Session, id: int, ejercicio: schemas.ejercicios.EjercicioUpdate):
    db_ejercicio = get_ejercicio(db=db, id=id)
    if db_ejercicio is None:
        return None
    
    update_data = ejercicio.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ejercicio, key, value)
    
    db.commit()
    db.refresh(db_ejercicio)
    return db_ejercicio

# Eliminar un ejercicio
def delete_ejercicio(db: Session, id: int):
    db_ejercicio = get_ejercicio(db=db, id=id)
    if db_ejercicio is None:
        return None
    
    db.delete(db_ejercicio)
    db.commit()
    return db_ejercicio