from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import crud.ejercicios, config.db, schemas.ejercicios, models.entrenamientos
from typing import List
from portadortoken import Portador

ejercicio = APIRouter()
models.entrenamientos.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas GET existentes
@ejercicio.get('/ejercicios/', response_model=List[schemas.ejercicios.Ejercicio], tags=['Ejercicios'], dependencies=[Depends(Portador())])
def read_ejercicios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_ejercicios = crud.ejercicios.get_ejercicios(db=db, skip=skip, limit=limit)
    return db_ejercicios

@ejercicio.get('/ejercicios/categoria/{categoria}', response_model=List[schemas.ejercicios.Ejercicio], tags=['Ejercicios'], dependencies=[Depends(Portador())])
def read_ejercicios_by_categoria(categoria: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_ejercicios = crud.ejercicios.get_ejercicios_by_categoria(db=db, categoria=categoria, skip=skip, limit=limit)
    return db_ejercicios

@ejercicio.get('/ejercicios/{id}', response_model=schemas.ejercicios.Ejercicio, tags=['Ejercicios'], dependencies=[Depends(Portador())])
def read_ejercicio(id: int, db: Session = Depends(get_db)):
    db_ejercicio = crud.ejercicios.get_ejercicio(db=db, id=id)
    if db_ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return db_ejercicio

# Ruta POST para crear un ejercicio
@ejercicio.post('/ejercicios/', response_model=schemas.ejercicios.Ejercicio, tags=['Ejercicios'], dependencies=[Depends(Portador())])
def create_ejercicio(ejercicio: schemas.ejercicios.EjercicioCreate, db: Session = Depends(get_db)):
    db_ejercicio = crud.ejercicios.get_ejercicio_by_nombre(db, nombre=ejercicio.Nombre)
    if db_ejercicio:
        raise HTTPException(status_code=400, detail="Ya existe un ejercicio con este nombre")
    return crud.ejercicios.create_ejercicio(db=db, ejercicio=ejercicio)

# Ruta PUT para actualizar un ejercicio
@ejercicio.put('/ejercicios/{id}', response_model=schemas.ejercicios.Ejercicio, tags=['Ejercicios'], dependencies=[Depends(Portador())])
def update_ejercicio(id: int, ejercicio: schemas.ejercicios.EjercicioUpdate, db: Session = Depends(get_db)):
    db_ejercicio = crud.ejercicios.update_ejercicio(db=db, id=id, ejercicio=ejercicio)
    if db_ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado para actualizar")
    return db_ejercicio

# Ruta DELETE para eliminar un ejercicio
@ejercicio.delete('/ejercicios/{id}', response_model=schemas.ejercicios.Ejercicio, tags=['Ejercicios'], dependencies=[Depends(Portador())])
def delete_ejercicio(id: int, db: Session = Depends(get_db)):
    db_ejercicio = crud.ejercicios.delete_ejercicio(db=db, id=id)
    if db_ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado para eliminar")
    return db_ejercicio