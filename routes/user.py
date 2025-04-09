from fastapi import status
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
from pydantic import BaseModel
from security import verify_password, hash_password
from datetime import datetime
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from typing import Union

# Modelos de datos para las peticiones
class PasswordChangeRequest(BaseModel):
    new_password: str

class PasswordHashResponse(BaseModel):
    password_hash: str
    is_google_account: bool = False

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

class UserWithRolesResponse(BaseModel):
    ID: int
    Nombre_Usuario: str
    Correo_Electronico: str
    Roles: List[str]
    Estatus: str
        
# Ruta de bienvenida
@user.get('/')
def bienvenido():
    return 'Bienvenido al sistema de APIs'


#Ruta abierta para registro de un usuario
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
    
    # Modificación: Establecer un valor por defecto para Numero_Telefonico_Movil
    # Esto evitará el error de validación si no se proporciona un número
    if not user.Numero_Telefonico_Movil:
        user.Numero_Telefonico_Movil = ""  # Establecer como string vacío
    
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
    
    # Convertir el modelo Pydantic a un diccionario, asegurándose de manejar Numero_Telefonico_Movil
    user_dict = user.dict()
    user_dict['Numero_Telefonico_Movil'] = user_dict.get('Numero_Telefonico_Movil', '')
    
    token = store_pending_registration(user_dict, verification_code)
    
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
    
    # Asegurar que Numero_Telefonico_Movil sea un string
    if "Numero_Telefonico_Movil" not in user_data or user_data["Numero_Telefonico_Movil"] is None:
        user_data["Numero_Telefonico_Movil"] = ""
    
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

@user.post('/login/', response_model=None, tags=['User Login'])
def read_credentials(usuario: schemas.users.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.users.get_user_by_email_password(
        db, 
        email=usuario.Correo_Electronico,
        password=usuario.Contrasena
    )
    
    if db_user is None:
        return JSONResponse(content={'mensaje':'Credenciales incorrectas'}, status_code=401)
    
    # Depuración: imprimir atributos disponibles
    print(f"Atributos del usuario: {dir(db_user)}")
    
    # Intentar verificar si es un usuario de Google de manera segura
    try:
        # Buscar el atributo que almacena el ID de Google (google_id, googleId, etc.)
        # Imprime todos los atributos que contienen la palabra "google" en su nombre
        google_attrs = [attr for attr in dir(db_user) if 'google' in attr.lower()]
        print(f"Posibles atributos de Google: {google_attrs}")
        
        # No usar el atributo Google_ID hasta encontrar el nombre correcto
    except Exception as e:
        print(f"Error al buscar atributos de Google: {str(e)}")
    
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


@user.post('/users/change-password', tags=['Usuarios']) 
def change_password(
    password_data: PasswordChangeRequest, 
    db: Session = Depends(get_db), 
    token_data: dict = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("ID")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: no contiene ID de usuario"
        )
    
    # Buscar el usuario en la base de datos
    db_user = crud.users.get_user(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado"
        )
    
    # Depuración: imprimir atributos disponibles
    print(f"Atributos del usuario: {dir(db_user)}")
    
    # Intentar determinar el nombre correcto del atributo de Google ID
    google_attrs = [attr for attr in dir(db_user) if 'google' in attr.lower()]
    print(f"Posibles atributos de Google: {google_attrs}")
    
    # Generar hash de la nueva contraseña
    hashed_password = hash_password(password_data.new_password)
    
    # Actualizar la contraseña
    db_user.Contrasena = hashed_password
    db_user.Fecha_Actualizacion = datetime.now()
    
    # No intentaremos configurar Tipo_Autenticacion hasta conocer los nombres correctos
    
    db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"mensaje": "Contraseña actualizada correctamente"}
    )


###Edpoint para administrador###
@user.get('/users-with-roles/', response_model=List[UserWithRolesResponse], tags=['Usuarios'])
def get_all_users_with_roles(
    db: Session = Depends(get_db), 
    token_data: dict = Depends(Portador())
):
    try:
        # Imprimir los datos del token para depuración
        print(f"Datos del token: {token_data}")
        
        # Obtener roles del token
        user_roles = token_data.get("roles", [])
        
        # Verificar si el usuario es admin
        if "admin" not in user_roles and "administrador" not in user_roles:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver todos los usuarios"
            )
        
        # Obtener todos los usuarios
        users = db.query(models.users.User).all()
        
        # Preparar respuesta con roles
        users_with_roles = []
        for user in users:
            # Obtener nombres de roles
            roles = [rol.Nombre for rol in user.roles] if user.roles else []
            
            users_with_roles.append(UserWithRolesResponse(
                ID=user.ID,
                Nombre_Usuario=user.Nombre_Usuario,
                Correo_Electronico=user.Correo_Electronico,
                Roles=roles,
                Estatus=user.Estatus.value if user.Estatus else None
            ))
        
        return users_with_roles
    
    except Exception as e:
        # Capturar y loguear cualquier error
        print(f"Error al procesar token: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail=f"Error de autenticación: {str(e)}"
        )@user.get('/users-with-roles/', response_model=List[UserWithRolesResponse], tags=['Usuarios'])
def get_all_users_with_roles(
    db: Session = Depends(get_db), 
    token: Union[str, dict] = Depends(Portador())
):
    try:
        # Imprimir el token recibido para depuración
        print(f"Token recibido: {token}")
        print(f"Tipo de token: {type(token)}")
        
        # Manejar caso cuando el token ya está decodificado
        if isinstance(token, dict):
            token_data = token
        else:
            # Si es un string, decodificar
            token_data = valida_token(token)
        
        # Imprimir datos del token para depuración
        print(f"Datos del token: {token_data}")
        
        user_roles = token_data.get("roles", [])
        
        # Verificar si el usuario es admin
        if "admin" not in user_roles and "administrador" not in user_roles:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver todos los usuarios"
            )
        
        # Obtener todos los usuarios
        users = db.query(models.users.User).all()
        
        # Preparar respuesta con roles
        users_with_roles = []
        for user in users:
            # Obtener nombres de roles
            roles = [rol.Nombre for rol in user.roles] if user.roles else []
            
            users_with_roles.append(UserWithRolesResponse(
                ID=user.ID,
                Nombre_Usuario=user.Nombre_Usuario,
                Correo_Electronico=user.Correo_Electronico,
                Roles=roles,
                Estatus=user.Estatus.value if user.Estatus else None
            ))
        
        return users_with_roles
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Token inválido"
        )
    except Exception as e:
        # Capturar y loguear cualquier error
        print(f"Error al procesar token: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail=f"Error de autenticación: {str(e)}"
        )@user.get('/users-with-roles/', response_model=List[UserWithRolesResponse], tags=['Usuarios'])
def get_all_users_with_roles(
    db: Session = Depends(get_db), 
    token: str = Depends(Portador())
):
    try:
        # Imprimir el token recibido para depuración
        print(f"Token recibido: {token}")
        print(f"Tipo de token: {type(token)}")
        
        # Decodificar el token para validar roles
        token_data = valida_token(token)
        
        # Imprimir datos del token para depuración
        print(f"Datos del token: {token_data}")
        
        user_roles = token_data.get("roles", [])
        
        # Verificar si el usuario es admin
        if "admin" not in user_roles and "administrador" not in user_roles:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver todos los usuarios"
            )
        
        # Obtener todos los usuarios
        users = db.query(models.users.User).all()
        
        # Preparar respuesta con roles
        users_with_roles = []
        for user in users:
            # Obtener nombres de roles
            roles = [rol.Nombre for rol in user.roles] if user.roles else []
            
            users_with_roles.append(UserWithRolesResponse(
                ID=user.ID,
                Nombre_Usuario=user.Nombre_Usuario,
                Correo_Electronico=user.Correo_Electronico,
                Roles=roles,
                Estatus=user.Estatus.value if user.Estatus else None
            ))
        
        return users_with_roles
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Token inválido"
        )
    except Exception as e:
        # Capturar y loguear cualquier error
        print(f"Error al procesar token: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail=f"Error de autenticación: {str(e)}"
        )# Agregar estas importaciones si no existen
from typing import List
from fastapi import HTTPException

# Esquema para la respuesta de usuarios con roles
class UserWithRolesResponse(BaseModel):
    ID: int
    Nombre_Usuario: str
    Correo_Electronico: str
    Roles: List[str]
    Estatus: str

# Nuevo endpoint para obtener todos los usuarios con sus roles (solo para admin)
@user.get('/users-with-roles/', response_model=List[UserWithRolesResponse], tags=['Usuarios'])
def get_all_users_with_roles(
    db: Session = Depends(get_db), 
    token_str: str = Depends(Portador())
):
    try:
        # Imprimir el token para depuración
        print(f"Token recibido: {token_str}")
        print(f"Tipo de token: {type(token_str)}")
        
        # Convertir el token a bytes si es necesario
        if isinstance(token_str, str):
            token = token_str.encode('utf-8')
        else:
            token = token_str
        
        # Decodificar el token para validar roles
        token_data = valida_token(token)
        
        # Imprimir datos del token para depuración
        print(f"Datos del token: {token_data}")
        
        user_roles = token_data.get("roles", [])
        
        # Verificar si el usuario es admin
        if "admin" not in user_roles and "administrador" not in user_roles:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver todos los usuarios"
            )
        
        # Obtener todos los usuarios
        users = db.query(models.users.User).all()
        
        # Preparar respuesta con roles
        users_with_roles = []
        for user in users:
            # Obtener nombres de roles
            roles = [rol.Nombre for rol in user.roles] if user.roles else []
            
            users_with_roles.append(UserWithRolesResponse(
                ID=user.ID,
                Nombre_Usuario=user.Nombre_Usuario,
                Correo_Electronico=user.Correo_Electronico,
                Roles=roles,
                Estatus=user.Estatus.value if user.Estatus else None
            ))
        
        return users_with_roles
    
    except Exception as e:
        # Capturar y loguear cualquier error
        print(f"Error al procesar token: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail=f"Error de autenticación: {str(e)}"
        )

# Esquema para solicitud de cambio de rol
class ChangeUserRoleRequest(BaseModel):
    user_id: int
    new_role_name: str

# Nuevo endpoint para cambiar rol de usuario (solo para admin)
@user.put('/change-user-role/', tags=['Usuarios'])
def change_user_role(
    role_change: ChangeUserRoleRequest,
    db: Session = Depends(get_db), 
    token: str = Depends(Portador())
):
    print(f"Token recibido: {token}")
    print(f"Tipo de token: {type(token)}")

    # Si el token ya está decodificado (por el Portador), usarlo directamente
    if isinstance(token, dict):
        token_data = token
    else:
        try:
            # Convertir a bytes si es un string
            if isinstance(token, str):
                token = token.encode('utf-8')
            
            # Decodificar el token
            token_data = valida_token(token)
        except Exception as e:
            print(f"Error al decodificar token: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail=f"Error de autenticación: {str(e)}"
            )

    print(f"Datos del token: {token_data}")
    
    # Verificar roles del usuario
    user_roles = token_data.get("roles", [])
    
    # Verificar si el usuario es admin
    if "admin" not in user_roles and "administrador" not in user_roles:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permisos para cambiar roles de usuarios"
        )
    
    # Buscar el usuario
    user = db.query(models.users.User).filter(models.users.User.ID == role_change.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Buscar el nuevo rol
    new_role = db.query(models.rols.Rol).filter(models.rols.Rol.Nombre == role_change.new_role_name).first()
    if not new_role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    # Limpiar roles existentes
    user.roles.clear()
    
    # Asignar nuevo rol
    user.roles.append(new_role)
    
    # Guardar cambios
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Rol de usuario actualizado exitosamente",
        "user_id": user.ID,
        "new_role": new_role.Nombre
    }