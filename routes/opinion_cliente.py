from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

import crud.opinion_cliente
import schemas.opinion_cliente
import models.opinion_cliente
import config.db
from portadortoken import Portador

opinion_cliente_router = APIRouter()
models.opinion_cliente.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@opinion_cliente_router.get('/opiniones_clientes/', response_model=List[schemas.opinion_cliente.OpinionCliente], tags=['OpinionesCliente'], dependencies=[Depends(Portador())])
def read_opinion_clientes(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return crud.opinion_cliente.get_opinion_clientes(db=db, skip=skip, limit=limit)

@opinion_cliente_router.get('/opinion_cliente/{id}', response_model=schemas.opinion_cliente.OpinionCliente, tags=['OpinionesCliente'], dependencies=[Depends(Portador())])
def read_opinion_cliente(id: int, db: Session = Depends(get_db)):
    db_opinion_cliente = crud.opinion_cliente.get_opinion_cliente(db=db, id=id)
    if db_opinion_cliente is None:
        raise HTTPException(status_code=404, detail="Opinión del cliente no encontrada")
    return db_opinion_cliente

@opinion_cliente_router.post('/opiniones_clientes/', response_model=schemas.opinion_cliente.OpinionCliente, tags=['OpinionesCliente'], dependencies=[Depends(Portador())])
def create_opinion_cliente(opinion_cliente: schemas.opinion_cliente.OpinionClienteCreate, db: Session = Depends(get_db)):
    return crud.opinion_cliente.create_opinion_cliente(db=db, opinion_cliente=opinion_cliente)

@opinion_cliente_router.put('/opiniones_clientes/{id}', response_model=schemas.opinion_cliente.OpinionCliente, tags=['OpinionesCliente'], dependencies=[Depends(Portador())])
def update_opinion_cliente(id: int, opinion_cliente: schemas.opinion_cliente.OpinionClienteUpdate, db: Session = Depends(get_db)):
    db_opinion_cliente = crud.opinion_cliente.update_opinion_cliente(db=db, id=id, opinion_cliente=opinion_cliente)
    if db_opinion_cliente is None:
        raise HTTPException(status_code=404, detail="Opinión del cliente no encontrada")
    return db_opinion_cliente

@opinion_cliente_router.delete('/opiniones_clientes/{id}', response_model=schemas.opinion_cliente.OpinionCliente, tags=['OpinionesCliente'], dependencies=[Depends(Portador())])
def delete_opinion_cliente(id: int, db: Session = Depends(get_db)):
    db_opinion_cliente = crud.opinion_cliente.delete_opinion_cliente(db=db, id=id)
    if db_opinion_cliente is None:
        raise HTTPException(status_code=404, detail="Opinión del cliente no encontrada")
    return db_opinion_cliente
