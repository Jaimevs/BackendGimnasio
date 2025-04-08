from sqlalchemy.orm import Session
import models.quejas
import models.clases
import models.users
import models.persons
import schemas.quejas
from datetime import datetime

# Buscar por ID
def get_queja(db: Session, id: int):
    return db.query(models.quejas.Queja).filter(models.quejas.Queja.ID == id).first()

# Buscar todas las quejas
def get_quejas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.quejas.Queja).offset(skip).limit(limit).all()

# Buscar quejas por usuario
def get_quejas_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.quejas.Queja).filter(
        models.quejas.Queja.Usuario_ID == usuario_id
    ).offset(skip).limit(limit).all()

# Buscar quejas por entrenador
def get_quejas_by_entrenador(db: Session, entrenador_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.quejas.Queja).filter(
        models.quejas.Queja.Entrenador_ID == entrenador_id
    ).offset(skip).limit(limit).all()

# Buscar quejas por clase
def get_quejas_by_clase(db: Session, clase_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.quejas.Queja).filter(
        models.quejas.Queja.Clase_ID == clase_id
    ).offset(skip).limit(limit).all()

# Crear nueva queja
def create_queja(db: Session, queja: schemas.quejas.QuejaCreate, usuario_id: int):
    db_queja = models.quejas.Queja(
        Usuario_ID=usuario_id,
        Entrenador_ID=queja.Entrenador_ID,
        Clase_ID=queja.Clase_ID,
        Calificacion=queja.Calificacion,
        Comentario=queja.Comentario,
        Estatus=queja.Estatus if queja.Estatus is not None else True,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_queja)
    db.commit()
    db.refresh(db_queja)
    return db_queja
# Actualizar queja por ID
def update_queja(db: Session, id: int, queja: schemas.quejas.QuejaUpdate):
    db_queja = db.query(models.quejas.Queja).filter(models.quejas.Queja.ID == id).first()
    if db_queja:
        for var, value in vars(queja).items():
            if value is not None and hasattr(db_queja, var):
                setattr(db_queja, var, value)
        
        # Actualizar fecha de actualización
        db_queja.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_queja)
    return db_queja

# Eliminar queja por ID
def delete_queja(db: Session, id: int):
    db_queja = db.query(models.quejas.Queja).filter(models.quejas.Queja.ID == id).first()
    if db_queja:
        db.delete(db_queja)
        db.commit()
    return db_queja

# Obtener quejas con información detallada
def get_quejas_with_details(db: Session, skip: int = 0, limit: int = 10):
    # Consulta con joins para obtener detalles de usuario, entrenador y clase
    results = db.query(
        models.quejas.Queja,
        models.users.User.Nombre_Usuario.label("usuario_nombre"),
        models.clases.Clase.Nombre.label("clase_nombre"),
        models.users.User.Nombre_Usuario.label("entrenador_nombre")
    ).join(
        models.users.User, models.quejas.Queja.Usuario_ID == models.users.User.ID
    ).join(
        models.clases.Clase, models.quejas.Queja.Clase_ID == models.clases.Clase.ID
    ).join(
        models.users.User, models.quejas.Queja.Entrenador_ID == models.users.User.ID, 
        isouter=True, aliased=True
    ).offset(skip).limit(limit).all()
    
    quejas_con_detalles = []
    for result in results:
        queja = result[0]
        quejas_con_detalles.append({
            "ID": queja.ID,
            "Usuario_ID": queja.Usuario_ID,
            "Entrenador_ID": queja.Entrenador_ID,
            "Clase_ID": queja.Clase_ID,
            "Calificacion": queja.Calificacion,
            "Comentario": queja.Comentario,
            "Estatus": queja.Estatus,
            "Fecha_Registro": queja.Fecha_Registro,
            "Fecha_Actualizacion": queja.Fecha_Actualizacion,
            "Usuario_Nombre": result[1] or "Sin nombre",
            "Clase_Nombre": result[2] or "Sin nombre",
            "Entrenador_Nombre": result[3] or "Sin nombre"
        })
    
    return quejas_con_detalles