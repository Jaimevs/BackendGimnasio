from fastapi import APIRouter,HTTPException,Depends,Request
from sqlalchemy.orm import Session
from portadortoken import Portador
import crud.servicios_clientes,config.db,schemas.servicios_clientes,models.servicios_clientes
from typing import List

servicio_cliente = APIRouter()

models.servicios_clientes.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@servicio_cliente.get("/servicios_clientes/", response_model=List[schemas.servicios_clientes.Servicio_Cliente], tags=["Servicios_Clientes"] ,dependencies=[Depends(Portador())])
def read_servicios_clientes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_servicios_clientes= crud.servicios_clientes.get_servicios_clientes(db=db, skip=skip, limit=limit)
    return db_servicios_clientes

@servicio_cliente.post("/servicio_cliente/{ID}", response_model=schemas.servicios_clientes.Servicio_Cliente, tags=["Servicios_Clientes"] ,dependencies=[Depends(Portador())])
def read_servicio_cliente(ID: int, db: Session = Depends(get_db)):
    db_servicios_clientes= crud.servicios_clientes.get_servicio_cliente(db=db, ID=ID)
    if db_servicios_clientes is None:
        raise HTTPException(status_code=404, detail="Servicio_Cliente not found")
    return db_servicios_clientes

@servicio_cliente.post("/servicios_clientes/", response_model=schemas.servicios_clientes.Servicio_Cliente, tags=["Servicios_Clientes"],dependencies=[Depends(Portador())])
def create_servicio_cliente(servicio_cliente: schemas.servicios_clientes.Servicio_ClienteCreate, db: Session = Depends(get_db)):
    db_servicio_cliente = crud.servicios_clientes.get_servicio_cliente_by_Tipo_Servicio(db, Tipo_Servicio=servicio_cliente.Tipo_Servicio)
    if db_servicio_cliente:
        raise HTTPException(status_code=400, detail="Servicio_Cliente existente intenta nuevamente")
    return crud.servicios_clientes.create_servicio_cliente(db=db, servicio_cliente=servicio_cliente)

@servicio_cliente.put("/servicio_cliente/{ID}", response_model=schemas.servicios_clientes.Servicio_Cliente, tags=["Servicios_Clientes"] ,dependencies=[Depends(Portador())])
def update_servicio_cliente(ID: int, servicio_cliente: schemas.servicios_clientes.Servicio_ClienteUpdate, db: Session = Depends(get_db)):
    db_servicio_cliente = crud.servicios_clientes.update_servicio_cliente(db = db, ID = ID, servicio_cliente = servicio_cliente)
    if db_servicio_cliente is None:
        raise HTTPException(status_code=404, detail="Servicio_Cliente no existente, no esta actuaizado")
    return db_servicio_cliente

@servicio_cliente.delete("/servicio_cliente/{ID}", response_model=schemas.servicios_clientes.Servicio_Cliente, tags=["Servicios_Clientes"] ,dependencies=[Depends(Portador())])
def delete_servicio_cliente(ID: int, db: Session = Depends(get_db)):
    db_servicio_cliente = crud.servicios_clientes.delete_servicio_cliente(db = db, ID = ID)
    if db_servicio_cliente is None:
        raise HTTPException(status_code=404, detail="Servicio_Cliente no existe, no se pudo eliminar")
    return db_servicio_cliente

