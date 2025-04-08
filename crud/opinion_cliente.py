from sqlalchemy.orm import Session
import models.opinion_cliente
import models.users
import schemas.opinion_cliente
from datetime import datetime

# Buscar por ID
def get_opinion(db: Session, id: int):
    return db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.ID == id).first()

# Buscar todas las opiniones
def get_opiniones(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.opinion_cliente.OpinionCliente).offset(skip).limit(limit).all()

# Buscar opiniones sin responder
def get_opiniones_sin_responder(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.opinion_cliente.OpinionCliente).filter(
        models.opinion_cliente.OpinionCliente.Estatus == False
    ).offset(skip).limit(limit).all()

# Buscar opiniones por usuario
def get_opiniones_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.opinion_cliente.OpinionCliente).filter(
        models.opinion_cliente.OpinionCliente.Usuario_ID == usuario_id
    ).offset(skip).limit(limit).all()

# Buscar opiniones por tipo
def get_opiniones_by_tipo(db: Session, tipo: str, skip: int = 0, limit: int = 10):
    return db.query(models.opinion_cliente.OpinionCliente).filter(
        models.opinion_cliente.OpinionCliente.Tipo == tipo
    ).offset(skip).limit(limit).all()

# Crear nueva opinión
def create_opinion(db: Session, opinion: schemas.opinion_cliente.OpinionClienteCreate, usuario_id: int):
    db_opinion = models.opinion_cliente.OpinionCliente(
        Usuario_ID=usuario_id,
        Tipo=opinion.Tipo,
        Descripcion=opinion.Descripcion,
        Estatus=False,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_opinion)
    db.commit()
    db.refresh(db_opinion)
    return db_opinion

# Actualizar opinión por ID
def update_opinion(db: Session, id: int, opinion: schemas.opinion_cliente.OpinionClienteUpdate):
    db_opinion = db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.ID == id).first()
    if db_opinion:
        for var, value in vars(opinion).items():
            if value is not None and hasattr(db_opinion, var):
                setattr(db_opinion, var, value)
        
        # Actualizar fecha de actualización
        db_opinion.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_opinion)
    return db_opinion

# Responder a una opinión
def responder_opinion(db: Session, id: int, respuesta: schemas.opinion_cliente.OpinionClienteRespuesta, respuesta_usuario_id: int):
    db_opinion = db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.ID == id).first()
    if db_opinion:
        db_opinion.Respuesta = respuesta.Respuesta
        db_opinion.Respuesta_Usuario_ID = respuesta_usuario_id
        db_opinion.Estatus = True
        db_opinion.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_opinion)
    return db_opinion

# Eliminar opinión por ID
def delete_opinion(db: Session, id: int):
    db_opinion = db.query(models.opinion_cliente.OpinionCliente).filter(models.opinion_cliente.OpinionCliente.ID == id).first()
    if db_opinion:
        db.delete(db_opinion)
        db.commit()
    return db_opinion

# Obtener opiniones con información detallada
def get_opiniones_with_details(db: Session, skip: int = 0, limit: int = 10):
    results = db.query(
        models.opinion_cliente.OpinionCliente,
        models.users.User.Nombre_Usuario.label("usuario_nombre"),
        models.users.User.Nombre_Usuario.label("respuesta_usuario_nombre")
    ).join(
        models.users.User, 
        models.opinion_cliente.OpinionCliente.Usuario_ID == models.users.User.ID
    ).outerjoin(
        models.users.User, 
        models.opinion_cliente.OpinionCliente.Respuesta_Usuario_ID == models.users.User.ID,
        isouter=True, aliased=True
    ).offset(skip).limit(limit).all()
    
    opiniones_con_detalles = []
    for result in results:
        opinion = result[0]
        opiniones_con_detalles.append({
            "ID": opinion.ID,
            "Usuario_ID": opinion.Usuario_ID,
            "Tipo": opinion.Tipo,
            "Descripcion": opinion.Descripcion,
            "Respuesta_Usuario_ID": opinion.Respuesta_Usuario_ID,
            "Respuesta": opinion.Respuesta,
            "Estatus": opinion.Estatus,
            "Fecha_Registro": opinion.Fecha_Registro,
            "Fecha_Actualizacion": opinion.Fecha_Actualizacion,
            "Usuario_Nombre": result[1] or "Sin nombre",
            "Respuesta_Usuario_Nombre": result[2] or "Sin nombre" if opinion.Respuesta_Usuario_ID else None
        })
    
    return opiniones_con_detalles