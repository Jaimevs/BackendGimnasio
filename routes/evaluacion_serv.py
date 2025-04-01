from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import crud.evaluaciones_serv, config.db, schemas.evaluaciones_serv, models.evaluaciones_serv
from portadortoken import Portador

evaluaciones_serv_router = APIRouter()
models.evaluaciones_serv.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta para obtener todas las evaluaciones
@evaluaciones_serv_router.get('/evaluaciones_serv/', response_model=List[schemas.evaluaciones_serv.Evaluaciones_serv], tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def read_evaluaciones(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    db_evaluaciones = crud.evaluaciones_serv.get_evaluaciones(db=db, skip=skip, limit=limit)
    return db_evaluaciones

# Ruta para obtener una evaluación por ID
@evaluaciones_serv_router.get('/evaluaciones_serv/{id}', response_model=schemas.evaluaciones_serv.Evaluaciones_serv, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def read_evaluacion(id: int, db: Session = Depends(get_db)):
    db_evaluacion = crud.evaluaciones_serv.get_evaluacion(db=db, id=id)
    if db_evaluacion is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return db_evaluacion

# Ruta para crear una nueva evaluación
@evaluaciones_serv_router.post('/evaluaciones_serv/', response_model=schemas.evaluaciones_serv.Evaluaciones_serv, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def create_evaluacion(evaluacion: schemas.evaluaciones_serv.Evaluaciones_servCreate, db: Session = Depends(get_db)):
    # Validación previa si es necesario (p.ej., verificar duplicados)
    # Aquí podrías agregar lógica para comprobar si la evaluación ya existe si es relevante
    return crud.evaluaciones_serv.create_evaluacion(db=db, evaluacion=evaluacion)

# Ruta para actualizar una evaluación
@evaluaciones_serv_router.put('/evaluaciones_serv/{id}', response_model=schemas.evaluaciones_serv.Evaluaciones_serv, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def update_evaluacion(id: int, evaluacion: schemas.evaluaciones_serv.Evaluaciones_servUpdate, db: Session = Depends(get_db)):
    db_evaluacion = crud.evaluaciones_serv.update_evaluacion(db=db, id=id, evaluacion=evaluacion)
    if db_evaluacion is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada, no se pudo actualizar")
    return db_evaluacion

# Ruta para eliminar una evaluación
@evaluaciones_serv_router.delete('/evaluaciones_serv/{id}', response_model=schemas.evaluaciones_serv.Evaluaciones_serv, tags=['Evaluaciones'], dependencies=[Depends(Portador())])
def delete_evaluacion(id: int, db: Session = Depends(get_db)):
    db_evaluacion = crud.evaluaciones_serv.delete_evaluacion(db=db, id=id)
    if db_evaluacion is None:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada, no se pudo eliminar")
    return db_evaluacion
