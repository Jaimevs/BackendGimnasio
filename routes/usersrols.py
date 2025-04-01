from fastapi import APIRouter,HTTPException, Depends
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import crud.usersrols, config.db, schemas.usersrols, models.usersrols
from typing import List

from portadortoken import Portador

key = Fernet.generate_key()
f = Fernet(key)

userrol = APIRouter()
models.usersrols.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta para obtener todos los Rols
@userrol.get('/usersrols/', response_model=List[schemas.usersrols.UserRol],tags=['Usuarios-Roles'], dependencies=[Depends(Portador())])
def read_rols(skip: int=0, limit: int=10, db: Session=Depends(get_db)):
    db_userrols = crud.usersrols.get_usersrols(db=db,skip=skip, limit=limit)
    return db_userrols

# Ruta para obtener un usuariorol por usuario ID
@userrol.post("/usersrol/{usuario_id}/{rol_id}", response_model=schemas.usersrols.UserRol, tags=["Usuarios-Roles"], dependencies=[Depends(Portador())])
def get_userrol_by_ids(usuario_id: int, rol_id: int, db: Session = Depends(get_db)):
    db_userrol = crud.usersrols.get_userrol_by_ids(db=db, usuario_id=usuario_id, rol_id=rol_id)
    if db_userrol is None:
        raise HTTPException(status_code=404, detail="User-Rol not found")
    return db_userrol

# Ruta para crear un usuario-rol
@userrol.post('/usersrols/', response_model=schemas.usersrols.UserRol,tags=['Usuarios-Roles'], dependencies=[Depends(Portador())])
def create_rol(userrol: schemas.usersrols.UserRolCreate, db: Session=Depends(get_db)):
    db_userrols = crud.usersrols.get_userrol_by_ids(db, usuario_id=userrol.Usuario_ID, rol_id=userrol.Rol_ID)
    if db_userrols:
        raise HTTPException(status_code=400, detail="User-Rol existente intenta nuevamente")
    return crud.usersrols.create_userrol(db=db, userrol=userrol)

# Ruta para actualizar un usuario-rol
@userrol.put("/usersrol/{usuario_id}/{rol_id}", response_model=schemas.usersrols.UserRol, tags=["Usuarios-Roles"], dependencies=[Depends(Portador())])
def update_userrol(usuario_id: int, rol_id: int, userrol:schemas.usersrols.UserRolUpdate, db: Session = Depends(get_db)):
    db_userrol = crud.usersrols.update_userrol(db=db, usuario_id=usuario_id, rol_id=rol_id, userrol=userrol)
    if db_userrol is None:
        raise HTTPException(status_code=404, detail="User-Rol not found")
    return db_userrol

# Ruta para eliminar un Rol
@userrol.delete('/usersrols/{usuario_id}/{rol_id}', response_model=schemas.usersrols.UserRol,tags=['Usuarios-Roles'], dependencies=[Depends(Portador())])
def delete_rol(usuario_id: int, rol_id: int, db: Session=Depends(get_db)):
    db_userrols = crud.usersrols.delete_userrol(db=db, usuario_id=usuario_id,rol_id=rol_id )
    if db_userrols is None:
        raise HTTPException(status_code=404, detail="User-Rol no existe, no se pudo eliminar ")
    return db_userrols