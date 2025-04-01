import models.opinion_cliente
import schemas.opinion_cliente
from sqlalchemy.orm import Session

def get_opinion_cliente(db: Session, id: int):
    return db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.id == id).first()

def get_opinion_clientes(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.opinion_cliente.OpinionCliente).offset(skip).limit(limit).all()

def create_opinion_cliente(db: Session, opinion_cliente: schemas.opinion_cliente.OpinionClienteCreate):
    db_opinion_cliente = models.opinion_cliente.OpinionCliente(
        descripcion=opinion_cliente.descripcion,
        tipo=opinion_cliente.tipo,
        respuesta=opinion_cliente.respuesta,
        estatus=opinion_cliente.estatus,
        atencion_personal=opinion_cliente.atencion_personal,
        fecha_registro=opinion_cliente.fecha_registro,
        fecha_actualizacion=opinion_cliente.fecha_actualizacion
    )
    db.add(db_opinion_cliente)
    db.commit()
    db.refresh(db_opinion_cliente)
    return db_opinion_cliente

def update_opinion_cliente(db: Session, id: int, opinion_cliente: schemas.opinion_cliente.OpinionClienteUpdate):
    db_opinion_cliente = db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.id == id).first()
    if db_opinion_cliente:
        for var, value in vars(opinion_cliente).items():
            setattr(db_opinion_cliente, var, value) if value is not None else None
        db.commit()
        db.refresh(db_opinion_cliente)
    return db_opinion_cliente

def delete_opinion_cliente(db: Session, id: int):
    db_opinion_cliente = db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.id == id).first()
    if db_opinion_cliente:
        db.delete(db_opinion_cliente)
        db.commit()
    return db_opinion_cliente
