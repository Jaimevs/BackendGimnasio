import models.users
import schemas.users
from sqlalchemy.orm import Session
import models, schemas
from security import hash_password
from security import verify_password

# Busqueda por id
def get_user(db:Session, id: int):
    return db.query(models.users.User).filter(models.users.User.ID == id).first()

# Busqueda por USUARIO
def get_user_by_usuario(db:Session, usuario: str):
    return db.query(models.users.User).filter(models.users.User.Nombre_Usuario == usuario).first()

def get_user_by_creentials(db:Session, username: str, correo:str, telefono:str, password:str):
    return db.query(models.users.User).filter((models.users.User.Nombre_Usuario == username) |
                                               (models.users.User.Correo_Electronico == correo) |
                                               (models.users.User.Numero_Telefonico_Movil == telefono),
                                                 models.users.User.Contrasena == password).first()

# Buscar todos los usuarios
def get_users(db:Session, skip: int=0, limit:int=10):
    return db.query(models.users.User).offset(skip).limit(limit).all()

# Crear nuevo usuario
def create_user(db:Session, user: schemas.users.UserCreate):

    hashed_password = hash_password(user.Contrasena)

    db_user = models.users.User(
                                Nombre_Usuario=user.Nombre_Usuario, 
                                Correo_Electronico=user.Correo_Electronico,
                                Contrasena=hashed_password, 
                                Numero_Telefonico_Movil=user.Numero_Telefonico_Movil, 
                                Estatus=user.Estatus, 
                                Fecha_Registro=user.Fecha_Registro, 
                                Fecha_Actualizacion=user.Fecha_Actualizacion)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Actualizar un usuario por id
def update_user(db:Session, id:int, user:schemas.users.UserUpdate):
    db_user = db.query(models.users.User).filter(models.users.User.ID == id).first()
    if db_user:
        for var, value in vars(user).items():
            setattr(db_user, var, value) if value else None
        db.commit()
        db.refresh(db_user)
    return db_user

# Eliminar un usuario por id
def delete_user(db:Session, id:int):
    db_user = db.query(models.users.User).filter(models.users.User.ID == id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.users.User).filter(models.users.User.Correo_Electronico == email).first()

def get_role_by_name(db: Session, name: str):
    return db.query(models.rols.Rol).filter(models.rols.Rol.Nombre == name).first()

def get_role(db: Session, id: int):
    return db.query(models.rols.Rol).filter(models.rols.Rol.ID == id).first()


# Funciones para relación usuario-rol
def assign_role_to_user(db: Session, user_id: int, role_id: int):
    # Verificar que existan usuario y rol
    user = get_user(db, user_id)
    role = get_role(db, role_id)
    
    if not user or not role:
        return None
    
    # Verificar si ya tiene asignado ese rol
    if role in user.roles:
        return user
    
    # Asignar rol
    user.roles.append(role)
    db.commit()
    db.refresh(user)
    return user

# Función para obtener usuario por email y contraseña- Login
def get_user_by_email_password(db: Session, email: str, password: str):
    user = db.query(models.users.User).filter(
        models.users.User.Correo_Electronico == email
    ).first()
    
    if user and verify_password(password, user.Contrasena):
        return user
    return None
