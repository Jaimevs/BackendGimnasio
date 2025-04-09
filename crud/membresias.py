from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import models.membresias
import models.users
import models.usersrols
import schemas.membresias
from datetime import datetime
from typing import List, Optional

# Buscar por ID
def get_membresia(db: Session, id: int):
    return db.query(models.membresias.Membresia).filter(models.membresias.Membresia.ID == id).first()

# Buscar por Usuario_ID
def get_membresia_by_usuario(db: Session, usuario_id: int):
    return db.query(models.membresias.Membresia).filter(
        models.membresias.Membresia.Usuario_ID == usuario_id,
        models.membresias.Membresia.Estatus == True
    ).first()

# Buscar todas las membresías
def get_membresias(db: Session, skip: int = 0, limit: int = 10, estatus: Optional[bool] = None):
    query = db.query(models.membresias.Membresia)
    
    if estatus is not None:
        query = query.filter(models.membresias.Membresia.Estatus == estatus)
    
    return query.offset(skip).limit(limit).all()

# Crear nueva membresía
def create_membresia(db: Session, membresia: schemas.membresias.MembresiaCreate):
    db_membresia = models.membresias.Membresia(
        Usuario_ID=membresia.Usuario_ID,
        Codigo=membresia.Codigo,
        Tipo=membresia.Tipo,
        Tipo_Servicios=membresia.Tipo_Servicios,
        Tipo_Plan=membresia.Tipo_Plan,
        Nivel=membresia.Nivel,
        Fecha_Inicio=membresia.Fecha_Inicio,
        Fecha_Fin=membresia.Fecha_Fin,
        Estatus=membresia.Estatus if membresia.Estatus is not None else True,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_membresia)
    db.commit()
    db.refresh(db_membresia)
    return db_membresia

# Actualizar membresía por ID
def update_membresia(db: Session, id: int, membresia: schemas.membresias.MembresiaUpdate):
    db_membresia = db.query(models.membresias.Membresia).filter(models.membresias.Membresia.ID == id).first()
    if db_membresia:
        for var, value in vars(membresia).items():
            if value is not None and hasattr(db_membresia, var):
                setattr(db_membresia, var, value)
        
        # Actualizar fecha de actualización
        db_membresia.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_membresia)
    return db_membresia

# Eliminar membresía por ID
def delete_membresia(db: Session, id: int):
    db_membresia = db.query(models.membresias.Membresia).filter(models.membresias.Membresia.ID == id).first()
    if db_membresia:
        db.delete(db_membresia)
        db.commit()
    return db_membresia

# Obtener membresías con información detallada del usuario
def get_membresias_with_details(db: Session, skip: int = 0, limit: int = 10):
    # Consulta con joins para obtener detalles de usuario
    results = db.query(
        models.membresias.Membresia,
        models.users.User.Nombre_Usuario,
        models.users.User.Correo_Electronico
    ).join(
        models.usersrols.UserRol, models.membresias.Membresia.Usuario_ID == models.usersrols.UserRol.Usuario_ID
    ).join(
        models.users.User, models.usersrols.UserRol.Usuario_ID == models.users.User.ID
    ).offset(skip).limit(limit).all()
    
    membresias_con_detalles = []
    for result in results:
        membresia = result[0]
        membresias_con_detalles.append({
            "ID": membresia.ID,
            "Usuario_ID": membresia.Usuario_ID,
            "Codigo": membresia.Codigo,
            "Tipo": membresia.Tipo.value,
            "Tipo_Servicios": membresia.Tipo_Servicios.value,
            "Tipo_Plan": membresia.Tipo_Plan.value,
            "Nivel": membresia.Nivel.value,
            "Fecha_Inicio": membresia.Fecha_Inicio,
            "Fecha_Fin": membresia.Fecha_Fin,
            "Estatus": membresia.Estatus,
            "Fecha_Registro": membresia.Fecha_Registro,
            "Fecha_Actualizacion": membresia.Fecha_Actualizacion,
            "Usuario_Nombre": result[1],
            "Usuario_Correo": result[2]
        })
    
    return membresias_con_detalles

# Obtener usuarios con rol de "usuario"
def get_usuarios_rol_usuario(db: Session, skip: int = 0, limit: int = 10):
    # Buscar el ID del rol "usuario"
    rol_usuario = db.query(models.users.Rol).filter(models.users.Rol.Nombre == "usuario").first()
    
    if not rol_usuario:
        return []
    
    # Buscar los usuarios que tienen el rol "usuario"
    usuarios = db.query(
        models.users.User
    ).join(
        models.usersrols.UserRol, models.users.User.ID == models.usersrols.UserRol.Usuario_ID
    ).filter(
        models.usersrols.UserRol.Rol_ID == rol_usuario.ID
    ).offset(skip).limit(limit).all()
    
    return usuarios

# Obtener usuarios con membresía específica
def get_usuarios_por_membresia(db: Session, tipo_membresia: Optional[str] = None, skip: int = 0, limit: int = 10):
    query = db.query(
        models.users.User,
        models.membresias.Membresia
    ).join(
        models.usersrols.UserRol, models.users.User.ID == models.usersrols.UserRol.Usuario_ID
    ).join(
        models.membresias.Membresia, models.usersrols.UserRol.Usuario_ID == models.membresias.Membresia.Usuario_ID
    )
    
    if tipo_membresia:
        query = query.filter(models.membresias.Membresia.Tipo == tipo_membresia)
    
    results = query.offset(skip).limit(limit).all()
    
    usuarios_con_membresia = []
    for user, membresia in results:
        usuarios_con_membresia.append({
            "usuario_id": user.ID,
            "nombre_usuario": user.Nombre_Usuario,
            "correo_electronico": user.Correo_Electronico,
            "membresia_id": membresia.ID,
            "tipo_membresia": membresia.Tipo.value,
            "tipo_servicios": membresia.Tipo_Servicios.value,
            "tipo_plan": membresia.Tipo_Plan.value,
            "nivel": membresia.Nivel.value,
            "fecha_inicio": membresia.Fecha_Inicio,
            "fecha_fin": membresia.Fecha_Fin,
            "estatus": membresia.Estatus
        })
    
    return usuarios_con_membresia