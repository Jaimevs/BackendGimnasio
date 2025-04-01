import models.servicios_clientes
import schemas.servicios_clientes
from sqlalchemy.orm import Session

def get_servicio_cliente(db:Session, ID:int):
    return db.query(models.servicios_clientes.Servicio_Cliente).filter(models.servicios_clientes.Servicio_Cliente.ID == ID).first()

def get_servicio_cliente_by_Tipo_Servicio(db: Session, Tipo_Servicio: str):
    return db.query(models.servicios_clientes.Servicio_Cliente).filter(models.servicios_clientes.Servicio_Cliente == get_servicio_cliente_by_Tipo_Servicio).first()

def get_servicios_clientes(db: Session, skip:int=0,limit:int=10):
    return db.query(models.servicios_clientes.Servicio_Cliente).offset(skip).limit(limit).all()

def create_servicio_cliente(db: Session, servicio_cliente:schemas.servicios_clientes.Servicio_ClienteCreate):
    db_servicio_cliente = models.servicios_clientes.Servicio_Cliente(Persona_ID=servicio_cliente.Persona_ID, Tipo_Servicio=servicio_cliente.Tipo_Servicio, Descripcion=servicio_cliente.Descripcion,Comentarios=servicio_cliente.Comentarios,Estatus=servicio_cliente.Estatus,Fecha_Registro=servicio_cliente.Fecha_Registro,Fecha_Actualizacion=servicio_cliente.Fecha_Actualizacion)
    db.add(db_servicio_cliente)
    db.commit()
    db.refresh(db_servicio_cliente)
    return db_servicio_cliente

def update_servicio_cliente(db: Session, ID: int, servicio_cliente: schemas.servicios_clientes.Servicio_ClienteUpdate):
    db_servicio_cliente = db.query(models.servicios_clientes.Servicio_Cliente).filter(models.servicios_clientes.Servicio_Cliente.ID == ID).first()
    if db_servicio_cliente:
        for var, value in vars(servicio_cliente).items():
            setattr(db_servicio_cliente, var, value) if value else None
        db.commit()
        db.refresh(db_servicio_cliente)
    return db_servicio_cliente

def delete_servicio_cliente(db: Session, ID: int):
    db_servicio_cliente = db.query(models.servicios_clientes.Servicio_Cliente).filter(models.servicios_clientes.Servicio_Cliente.ID == ID).first()
    if  db_servicio_cliente:
        db.delete(db_servicio_cliente)
        db.commit()
    return db_servicio_cliente
