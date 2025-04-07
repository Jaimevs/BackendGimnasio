# crud/reservaciones.py
from sqlalchemy.orm import Session
import models.reservaciones
import models.users
import models.clases
import schemas.reservaciones
from datetime import datetime
from sqlalchemy import and_, func

# Buscar por ID
def get_reservacion(db: Session, id: int):
    return db.query(models.reservaciones.Reservacion).filter(models.reservaciones.Reservacion.ID == id).first()

# Buscar todas las reservaciones
def get_reservaciones(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.reservaciones.Reservacion).offset(skip).limit(limit).all()

# Buscar reservaciones por usuario
def get_reservaciones_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.reservaciones.Reservacion).filter(
        models.reservaciones.Reservacion.Usuario_ID == usuario_id
    ).offset(skip).limit(limit).all()

# Buscar reservaciones por clase
def get_reservaciones_by_clase(db: Session, clase_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.reservaciones.Reservacion).filter(
        models.reservaciones.Reservacion.Clase_ID == clase_id
    ).offset(skip).limit(limit).all()

# Verificar si un usuario ya tiene reservada una clase en una fecha específica
def check_reservacion_exists(db: Session, usuario_id: int, clase_id: int, fecha_reservacion: datetime):
    return db.query(models.reservaciones.Reservacion).filter(
        and_(
            models.reservaciones.Reservacion.Usuario_ID == usuario_id,
            models.reservaciones.Reservacion.Clase_ID == clase_id,
            func.date(models.reservaciones.Reservacion.Fecha_Reservacion) == func.date(fecha_reservacion),
            models.reservaciones.Reservacion.Estatus != "Cancelada"
        )
    ).first() is not None

# Crear nueva reservación
def create_reservacion(db: Session, reservacion: schemas.reservaciones.ReservacionCreate):
    db_reservacion = models.reservaciones.Reservacion(
        Usuario_ID=reservacion.Usuario_ID,
        Clase_ID=reservacion.Clase_ID,
        Fecha_Reservacion=reservacion.Fecha_Reservacion,
        Estatus=reservacion.Estatus,
        Comentario=reservacion.Comentario,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_reservacion)
    db.commit()
    db.refresh(db_reservacion)
    return db_reservacion

# Actualizar reservación por ID
def update_reservacion(db: Session, id: int, reservacion: schemas.reservaciones.ReservacionUpdate):
    db_reservacion = db.query(models.reservaciones.Reservacion).filter(models.reservaciones.Reservacion.ID == id).first()
    if db_reservacion:
        # Actualizar campos si están presentes
        if reservacion.Estatus is not None:
            db_reservacion.Estatus = reservacion.Estatus
        if reservacion.Comentario is not None:
            db_reservacion.Comentario = reservacion.Comentario
        if reservacion.Fecha_Reservacion is not None:
            db_reservacion.Fecha_Reservacion = reservacion.Fecha_Reservacion
        
        # Actualizar fecha de actualización
        db_reservacion.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_reservacion)
    return db_reservacion

# Cancelar reservación
def cancel_reservacion(db: Session, id: int):
    db_reservacion = db.query(models.reservaciones.Reservacion).filter(models.reservaciones.Reservacion.ID == id).first()
    if db_reservacion:
        db_reservacion.Estatus = "Cancelada"
        db_reservacion.Fecha_Actualizacion = datetime.now()
        db.commit()
        db.refresh(db_reservacion)
    return db_reservacion

# Marcar asistencia a una reservación
def mark_attendance(db: Session, id: int, asistio: bool):
    db_reservacion = db.query(models.reservaciones.Reservacion).filter(models.reservaciones.Reservacion.ID == id).first()
    if db_reservacion:
        db_reservacion.Estatus = "Asistida" if asistio else "No Asistida"
        db_reservacion.Fecha_Actualizacion = datetime.now()
        db.commit()
        db.refresh(db_reservacion)
    return db_reservacion

# Obtener reservación con detalles completos
def get_reservacion_with_details(db: Session, id: int):
    # Usar aliases para evitar conflictos
    usuario_alias = aliased(models.users.User)
    entrenador_alias = aliased(models.users.User)
    
    result = db.query(
        models.reservaciones.Reservacion,
        usuario_alias.Nombre_Usuario,
        models.clases.Clase.Nombre.label("nombre_clase"),
        models.clases.Clase.Dia_Inicio.label("dia_clase"),
        models.clases.Clase.Hora_Inicio,
        models.clases.Clase.Hora_Fin,
        entrenador_alias.Nombre_Usuario.label("entrenador_nombre")
    ).join(
        usuario_alias, models.reservaciones.Reservacion.Usuario_ID == usuario_alias.ID
    ).join(
        models.clases.Clase, models.reservaciones.Reservacion.Clase_ID == models.clases.Clase.ID
    ).join(
        entrenador_alias, models.clases.Clase.Entrenador_ID == entrenador_alias.ID, isouter=True
    ).filter(
        models.reservaciones.Reservacion.ID == id
    ).first()
    
    if not result:
        return None
    
    # Extraer los datos de la reservación
    reservacion = result[0]
    
    # Crear un objeto con todos los detalles
    reservacion_detalle = {
        "ID": reservacion.ID,
        "Usuario_ID": reservacion.Usuario_ID,
        "Clase_ID": reservacion.Clase_ID,
        "Fecha_Reservacion": reservacion.Fecha_Reservacion,
        "Estatus": reservacion.Estatus,
        "Comentario": reservacion.Comentario,
        "Fecha_Registro": reservacion.Fecha_Registro,
        "Fecha_Actualizacion": reservacion.Fecha_Actualizacion,
        "Nombre_Usuario": result[1],
        "Nombre_Clase": result[2],
        "Dia_Clase": result[3],
        "Hora_Inicio": result[4],
        "Hora_Fin": result[5],
        "Entrenador_Nombre": result[6]
    }
    
    return reservacion_detalle

# Obtener todas las reservaciones con detalles completos
def get_reservaciones_with_details(db: Session, skip: int = 0, limit: int = 10):
    # Consulta con joins para obtener información detallada de todas las reservaciones
    results = db.query(
        models.reservaciones.Reservacion,
        models.users.User.Nombre_Usuario,
        models.clases.Clase.Nombre.label("nombre_clase"),
        models.clases.Clase.Dia_Inicio.label("dia_clase"),
        models.clases.Clase.Hora_Inicio,
        models.clases.Clase.Hora_Fin,
        models.users.User.Nombre_Usuario.label("entrenador_nombre")
    ).join(
        models.users.User, models.reservaciones.Reservacion.Usuario_ID == models.users.User.ID
    ).join(
        models.clases.Clase, models.reservaciones.Reservacion.Clase_ID == models.clases.Clase.ID
    ).join(
        models.users.User, models.clases.Clase.Entrenador_ID == models.users.User.ID, isouter=True
    ).offset(skip).limit(limit).all()
    
    reservaciones_con_detalles = []
    for result in results:
        reservacion = result[0]
        reservaciones_con_detalles.append({
            "ID": reservacion.ID,
            "Usuario_ID": reservacion.Usuario_ID,
            "Clase_ID": reservacion.Clase_ID,
            "Fecha_Reservacion": reservacion.Fecha_Reservacion,
            "Estatus": reservacion.Estatus,
            "Comentario": reservacion.Comentario,
            "Fecha_Registro": reservacion.Fecha_Registro,
            "Fecha_Actualizacion": reservacion.Fecha_Actualizacion,
            "Nombre_Usuario": result[1],
            "Nombre_Clase": result[2],
            "Dia_Clase": result[3],
            "Hora_Inicio": result[4],
            "Hora_Fin": result[5],
            "Entrenador_Nombre": result[6]
        })
    
    return reservaciones_con_detalles