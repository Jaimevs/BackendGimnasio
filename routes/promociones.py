from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import crud.promociones, config.db, schemas.promociones, models.promociones
from typing import List
from portadortoken import Portador

promocion_router = APIRouter()
models.promociones.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@promocion_router.get('/promociones/', response_model=List[schemas.promociones.Promocion], tags=['Promociones'], dependencies=[Depends(Portador())])
def read_promocions(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    db_promocions = crud.promociones.get_promocions(db=db, skip=skip, limit=limit)
    return db_promocions

@promocion_router.get('/promocion/{id}', response_model=schemas.promociones.Promocion, tags=['Promociones'], dependencies=[Depends(Portador())])
def read_promocion(id: int, db: Session = Depends(get_db)):
    db_promocion = crud.promociones.get_promocion(db=db, id=id)
    if db_promocion is None:
        raise HTTPException(status_code=404, detail="Promocion not found")
    return db_promocion

@promocion_router.post('/promociones/', response_model=schemas.promociones.Promocion, tags=['Promociones'],dependencies=[Depends(Portador())])
def create_promocion(promocion: schemas.promociones.PromocionCreate, db: Session = Depends(get_db)):
    return crud.promociones.create_promocion(db=db, promocion=promocion)

@promocion_router.put('/promociones/{id}', response_model=schemas.promociones.Promocion, tags=['Promociones'], dependencies=[Depends(Portador())])
def update_promocion(id: int, promocion: schemas.promociones.PromocionUpdate, db: Session = Depends(get_db)):
    db_promocion = crud.promociones.update_promocion(db=db, id=id, promocion=promocion)
    if db_promocion is None:
        raise HTTPException(status_code=404, detail="Promocion not found, unable to update")
    return db_promocion

@promocion_router.delete('/promociones/{id}', response_model=schemas.promociones.Promocion, tags=['Promociones'], dependencies=[Depends(Portador())])
def delete_promocion(id: int, db: Session = Depends(get_db)):
    db_promocion = crud.promociones.delete_promocion(db=db, id=id)
    if db_promocion is None:
        raise HTTPException(status_code=404, detail="Promocion not found, unable to delete")
    return db_promocion
