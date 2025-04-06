from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import crud.entrenamientos, config.db, schemas.entrenamientos, models.entrenamientos
from typing import List
from portadortoken import Portador

entrenamiento = APIRouter()
models.entrenamientos.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas GET existentes
@entrenamiento.get('/entrenamientos/', response_model=List[schemas.entrenamientos.Entrenamiento], tags=['Entrenamientos'], dependencies=[Depends(Portador())])
def read_entrenamientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_entrenamientos = crud.entrenamientos.get_entrenamientos(db=db, skip=skip, limit=limit)
    return db_entrenamientos

@entrenamiento.get('/entrenamientos/usuario/{usuario_id}', response_model=List[schemas.entrenamientos.Entrenamiento], tags=['Entrenamientos'], dependencies=[Depends(Portador())])
def read_entrenamientos_by_usuario(usuario_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_entrenamientos = crud.entrenamientos.get_entrenamientos_by_usuario(db=db, usuario_id=usuario_id, skip=skip, limit=limit)
    return db_entrenamientos

@entrenamiento.get('/entrenamientos/{id}', response_model=schemas.entrenamientos.Entrenamiento, tags=['Entrenamientos'], dependencies=[Depends(Portador())])
def read_entrenamiento(id: int, db: Session = Depends(get_db)):
    db_entrenamiento = crud.entrenamientos.get_entrenamiento(db=db, id=id)
    if db_entrenamiento is None:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return db_entrenamiento

# Ruta POST para crear un entrenamiento
@entrenamiento.post('/entrenamientos/', response_model=schemas.entrenamientos.Entrenamiento, tags=['Entrenamientos'], dependencies=[Depends(Portador())])
def create_entrenamiento(entrenamiento: schemas.entrenamientos.EntrenamientoCreate, db: Session = Depends(get_db)):
    return crud.entrenamientos.create_entrenamiento(db=db, entrenamiento=entrenamiento)

# Ruta PUT para actualizar un entrenamiento
@entrenamiento.put('/entrenamientos/{id}', response_model=schemas.entrenamientos.Entrenamiento, tags=['Entrenamientos'], dependencies=[Depends(Portador())])
def update_entrenamiento(id: int, entrenamiento: schemas.entrenamientos.EntrenamientoUpdate, db: Session = Depends(get_db)):
    db_entrenamiento = crud.entrenamientos.update_entrenamiento(db=db, id=id, entrenamiento=entrenamiento)
    if db_entrenamiento is None:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado para actualizar")
    return db_entrenamiento

# Ruta DELETE para eliminar un entrenamiento
@entrenamiento.delete('/entrenamientos/{id}', response_model=schemas.entrenamientos.Entrenamiento, tags=['Entrenamientos'], dependencies=[Depends(Portador())])
def delete_entrenamiento(id: int, db: Session = Depends(get_db)):
    db_entrenamiento = crud.entrenamientos.delete_entrenamiento(db=db, id=id)
    if db_entrenamiento is None:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado para eliminar")
    return db_entrenamiento