from fastapi import APIRouter,HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import json
import crud.users, config.db, schemas.users, models.users
from typing import List
from jwt_config import solicita_token, valida_token
from portadortoken import Portador
from gmail_service import send_verification_email
from token_verification import store_pending_registration, get_pending_registration, verify_code

key = Fernet.generate_key()
f = Fernet(key)

user = APIRouter()
models.users.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Ruta de bienvenida
@user.get('/')
def bienvenido():
    return 'Bienvenido al sistema de APIs'

# Ruta para obtener todos los usuarios
@user.get('/users/', response_model=List[schemas.users.User],tags=['Usuarios'], dependencies=[Depends(Portador())])
def read_users(skip: int=0, limit: int=10, db: Session=Depends(get_db)):
    db_users = crud.users.get_users(db=db,skip=skip, limit=limit)
    return db_users

# Ruta para obtener un usuario por ID
@user.post("/user/{id}", response_model=schemas.users.User, tags=["Usuarios"], dependencies=[Depends(Portador())])
def read_user(id: int, db: Session = Depends(get_db)):
    db_user= crud.users.get_user(db=db, id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Ruta para crear un usurio
@user.post('/users/', response_model=schemas.users.User,tags=['Usuarios'])
def create_user(user: schemas.users.UserCreate, db: Session=Depends(get_db)):
    db_users = crud.users.get_user_by_usuario(db,usuario=user.Nombre_Usuario)
    if db_users:
        raise HTTPException(status_code=400, detail="Usuario existente intenta nuevamente")
    return crud.users.create_user(db=db, user=user)

# Ruta para actualizar un usuario
@user.put('/users/{id}', response_model=schemas.users.User,tags=['Usuarios'], dependencies=[Depends(Portador())])
def update_user(id:int,user: schemas.users.UserUpdate, db: Session=Depends(get_db)):
    db_users = crud.users.update_user(db=db, id=id, user=user)
    if db_users is None:
        raise HTTPException(status_code=404, detail="Usuario no existe, no se pudo actualizar ")
    return db_users

# Ruta para eliminar un usuario
@user.delete('/users/{id}', response_model=schemas.users.User,tags=['Usuarios'], dependencies=[Depends(Portador())])
def delete_user(id:int, db: Session=Depends(get_db)):
    db_users = crud.users.delete_user(db=db, id=id)
    if db_users is None:
        raise HTTPException(status_code=404, detail="Usuario no existe, no se pudo eliminar ")
    return db_users
'''
@user.post('/login/', response_model=schemas.users.UserLogin, tags=['User Login'])
def read_credentials(usuario:schemas.users.UserLogin, db: Session = Depends(get_db)):
    db_credentials = crud.users.get_user_by_creentials(db, username=usuario.Nombre_Usuario,
                                                       correo=usuario.Correo_Electronico,
                                                       telefono=usuario.Numero_Telefonico_Movil,
                                                       password=usuario.Contrasena)
    if db_credentials is None:
        return JSONResponse(content={'mensaje':'Acceso denegado'},status_code=404)
    token:str=solicita_token(usuario.dict())
    return JSONResponse(status_code=200, content=token)
'''

#Ruta abierta para registro normla de un usuario
@user.post('/users/register/', tags=['Usuarios'])
async def register_user(user: schemas.users.UserCreateRequest, db: Session=Depends(get_db)):
    # Verificar si ya existe el usuario
    db_user = crud.users.get_user_by_usuario(db, usuario=user.Nombre_Usuario)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    # Verificar si ya existe el correo
    email_exists = crud.users.get_user_by_email(db, email=user.Correo_Electronico)
    if email_exists:
        raise HTTPException(status_code=400, detail="Correo electrónico ya registrado")
    
    # Enviar email con código de verificación
    result = await send_verification_email(user.Correo_Electronico, "")
    
    if not result.get('success', False):
        # Manejo de errores en el envío del correo
        raise HTTPException(
            status_code=500, 
            detail=f"Error al enviar correo de verificación: {result.get('error', 'Error desconocido')}"
        )
    
    # Almacenar datos de usuario y código de verificación
    verification_code = result.get('verification_code')
    token = store_pending_registration(user.dict(), verification_code)
    
    return {
        "message": "Se ha enviado un código de verificación a tu correo electrónico.",
        "email": user.Correo_Electronico
    }

@user.post('/api/users/verify/', response_model=schemas.users.User, tags=['Usuarios'])
def verify_user_by_code(verification: schemas.users.UserVerifyByCode, db: Session=Depends(get_db)):
    # Verificar el código
    user_data = verify_code(verification.email, verification.code)
    
    if not user_data:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")
    
    # Añadir fechas si no existen
    from datetime import datetime
    current_time = datetime.now()
    
    if "Fecha_Registro" not in user_data or user_data["Fecha_Registro"] is None:
        user_data["Fecha_Registro"] = current_time
        
    if "Fecha_Actualizacion" not in user_data or user_data["Fecha_Actualizacion"] is None:
        user_data["Fecha_Actualizacion"] = current_time
    
    # Crear usuario con los datos almacenados
    user = schemas.users.UserCreate(**user_data)
    
    # Verificar si ya existe el usuario
    db_user = crud.users.get_user_by_usuario(db, usuario=user.Nombre_Usuario)
    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    # Verificar si ya existe el correo
    email_exists = crud.users.get_user_by_email(db, email=user.Correo_Electronico)
    if email_exists:
        raise HTTPException(status_code=400, detail="Correo electrónico ya registrado")
    
    # Crear el usuario
    new_user = crud.users.create_user(db=db, user=user)
    
    # Asignar rol de usuario por defecto
    role = crud.users.get_role_by_name(db, "usuario")
    if role:
        crud.users.assign_role_to_user(db, user_id=new_user.ID, role_id=role.ID)
    
    return new_user

#Login de usuario
@user.post('/login/', response_model=None, tags=['User Login'])
def read_credentials(usuario: schemas.users.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.users.get_user_by_email_password(
        db, 
        email=usuario.Correo_Electronico,
        password=usuario.Contrasena
    )
    
    if db_user is None:
        return JSONResponse(content={'mensaje':'Acceso denegado'}, status_code=404)
    
    # Obtener los roles del usuario
    roles_names = [rol.Nombre for rol in db_user.roles] if db_user.roles else ["usuario"]
    
    # Crear datos para el token
    token_data = {
        "ID": db_user.ID,
        "Nombre_Usuario": db_user.Nombre_Usuario,
        "Correo_Electronico": db_user.Correo_Electronico
    }
    
    # Generar token incluyendo roles
    token_response = solicita_token(token_data, roles=roles_names)
    
    # Preparar respuesta personalizada
    response = {
        "ID": db_user.ID,
        "Nombre_Usuario": db_user.Nombre_Usuario,
        "Correo_Electronico": db_user.Correo_Electronico,
        "roles": roles_names,
        "token": token_response
    }
    
    return JSONResponse(status_code=200, content=response)

# Endpoint para obtener usuarios (todos o solo el propio según el rol)
@user.get('/users-by-role/', response_model=List[schemas.users.User], tags=['Usuarios'])
def get_users_by_role(db: Session = Depends(get_db), token: str = Depends(Portador())):
    # Decodificar el token para obtener la información del usuario y sus roles
    token_data = valida_token(token)
    user_id = token_data.get("ID")
    user_roles = token_data.get("roles", [])
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # Verificar si el usuario tiene rol de admin
    is_admin = "admin" in user_roles or "administrador" in user_roles
    
    if is_admin:
        # Si es admin, devolver todos los usuarios
        return crud.users.get_users(db=db, skip=0, limit=100)
    else:
        # Si es usuario normal, devolver solo su propio perfil
        db_user = crud.users.get_user(db=db, id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return [db_user]