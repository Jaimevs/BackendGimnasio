from fastapi import APIRouter,HTTPException, Depends
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import crud.rols, config.db, schemas.rols, models.rols
from typing import List
from portadortoken import Portador

key = Fernet.generate_key()
f = Fernet(key)

rol = APIRouter()
models.rols.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta para obtener todos los Rols
@rol.get('/rols/', response_model=List[schemas.rols.Rol],tags=['Roles'], dependencies=[Depends(Portador())])
def read_rols(skip: int=0, limit: int=10, db: Session=Depends(get_db)):
    db_rols = crud.rols.get_rols(db=db,skip=skip, limit=limit)
    return db_rols

# Ruta para obtener un Rol por ID
@rol.post("/rol/{id}", response_model=schemas.rols.Rol, tags=["Roles"], dependencies=[Depends(Portador())])
def read_rol(id: int, db: Session = Depends(get_db)):
    db_rol= crud.rols.get_rol(db=db, id=id)
    if db_rol is None:
        raise HTTPException(status_code=404, detail="Rol not found")
    return db_rol

# Ruta para crear un usurio
@rol.post('/rols/', response_model=schemas.rols.Rol,tags=['Roles'], dependencies=[Depends(Portador())])
def create_rol(rol: schemas.rols.RolCreate, db: Session=Depends(get_db)):
    db_rols = crud.rols.get_rol_by_nombre(db,nombre=rol.Nombre)
    if db_rols:
        raise HTTPException(status_code=400, detail="Rol existente intenta nuevamente")
    return crud.rols.create_rol(db=db, rol=rol)

# Ruta para actualizar un Rol
@rol.put('/rols/{id}', response_model=schemas.rols.Rol,tags=['Roles'], dependencies=[Depends(Portador())])
def update_rol(id:int,rol: schemas.rols.RolUpdate, db: Session=Depends(get_db)):
    db_rols = crud.rols.update_rol(db=db, id=id, rol=rol)
    if db_rols is None:
        raise HTTPException(status_code=404, detail="Rol no existe, no se pudo actualizar ")
    return db_rols

# Ruta para eliminar un Rol
@rol.delete('/rols/{id}', response_model=schemas.rols.Rol,tags=['Roles'], dependencies=[Depends(Portador())])
def delete_rol(id:int, db: Session=Depends(get_db)):
    db_rols = crud.rols.delete_rol(db=db, id=id)
    if db_rols is None:
        raise HTTPException(status_code=404, detail="Rol no existe, no se pudo eliminar ")
    return db_rols