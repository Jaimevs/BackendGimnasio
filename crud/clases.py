# crud/clases.py
from sqlalchemy.orm import Session
import models.clases
import models.users
import models.persons
import schemas.clases
from datetime import datetime

# Buscar por ID
def get_clase(db: Session, id: int):
    return db.query(models.clases.Clase).filter(models.clases.Clase.ID == id).first()

# Buscar por nombre
def get_clase_by_nombre(db: Session, nombre: str):
    return db.query(models.clases.Clase).filter(models.clases.Clase.Nombre == nombre).first()

# Buscar todas las clases
def get_clases(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.clases.Clase).offset(skip).limit(limit).all()

# Buscar clases por entrenador
def get_clases_by_entrenador(db: Session, entrenador_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.clases.Clase).filter(
        models.clases.Clase.Entrenador_ID == entrenador_id
    ).offset(skip).limit(limit).all()

# Crear nueva clase
def create_clase(db: Session, clase: schemas.clases.ClaseCreate, entrenador_id: int):
    db_clase = models.clases.Clase(
        Entrenador_ID=entrenador_id,  # Usar el ID proporcionado
        Nombre=clase.Nombre,
        Descripcion=clase.Descripcion,
        Dia_Inicio=clase.Dia_Inicio,
        Dia_Fin=clase.Dia_Fin,
        Hora_Inicio=clase.Hora_Inicio,
        Hora_Fin=clase.Hora_Fin,
        Duracion_Minutos=clase.Duracion_Minutos,
        Estatus=clase.Estatus,
        Fecha_Registro=datetime.now(),
        Fecha_Actualizacion=datetime.now()
    )
    
    db.add(db_clase)
    db.commit()
    db.refresh(db_clase)
    return db_clase

# Actualizar clase por ID
def update_clase(db: Session, id: int, clase: schemas.clases.ClaseUpdate):
    db_clase = db.query(models.clases.Clase).filter(models.clases.Clase.ID == id).first()
    if db_clase:
        for var, value in vars(clase).items():
            if value is not None and hasattr(db_clase, var):
                setattr(db_clase, var, value)
        
        # Actualizar fecha de actualización
        db_clase.Fecha_Actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_clase)
    return db_clase

# Eliminar clase por ID
def delete_clase(db: Session, id: int):
    # Primero, obtener la clase para verificar que existe
    db_clase = db.query(models.clases.Clase).filter(models.clases.Clase.ID == id).first()
    
    if db_clase:
        # Eliminar primero todas las reservaciones asociadas a esta clase
        reservaciones = db.query(models.reservaciones.Reservacion).filter(
            models.reservaciones.Reservacion.Clase_ID == id
        ).all()
        
        # Registrar el número de reservaciones que se eliminarán
        num_reservaciones = len(reservaciones)
        
        # Eliminar cada reservación
        for reservacion in reservaciones:
            db.delete(reservacion)
        
        # Ahora eliminar la clase
        db.delete(db_clase)
        db.commit()
        
        print(f"Clase ID {id} eliminada junto con {num_reservaciones} reservaciones asociadas")
    
    return db_clase

# Función para obtener detalles de clase con información del entrenador
def get_clase_with_entrenador_details(db: Session, clase_id: int):
    # Consulta única con join para obtener información de la clase y del entrenador
    result = db.query(
        models.clases.Clase,
        models.users.User.Nombre_Usuario.label("entrenador_nombre"),
        models.persons.Person.Nombre.label("entrenador_nombre_completo"),
        models.persons.Person.Primer_Apellido.label("entrenador_apellido")
    ).join(
        models.users.User, models.clases.Clase.Entrenador_ID == models.users.User.ID
    ).outerjoin(
        models.persons.Person, models.users.User.ID == models.persons.Person.Usuario_ID
    ).filter(
        models.clases.Clase.ID == clase_id
    ).first()
    
    if not result:
        return None
    
    # Extraer los datos de la clase
    clase = result[0]
    
    # Crear un objeto con todos los detalles
    clase_detalle = {
        "ID": clase.ID,
        "Entrenador_ID": clase.Entrenador_ID,
        "Nombre": clase.Nombre,
        "Descripcion": clase.Descripcion,
        "Dia_Inicio": clase.Dia_Inicio,
        "Dia_Fin": clase.Dia_Fin,
        "Hora_Inicio": clase.Hora_Inicio,
        "Hora_Fin": clase.Hora_Fin,
        "Duracion_Minutos": clase.Duracion_Minutos,
        "Estatus": clase.Estatus,
        "Fecha_Registro": clase.Fecha_Registro,
        "Fecha_Actualizacion": clase.Fecha_Actualizacion,
        "Entrenador_Nombre": result[1] or "Sin nombre",
        "Entrenador_Nombre_Completo": result[2] or "",
        "Entrenador_Apellido": result[3] or ""
    }
    
    return clase_detalle

# Obtener todas las clases con detalles del entrenador
def get_clases_with_entrenador(db: Session, skip: int = 0, limit: int = 10):
    # Consulta con join para obtener clases con datos de entrenador
    results = db.query(
        models.clases.Clase,
        models.users.User.Nombre_Usuario.label("entrenador_nombre"),
        models.persons.Person.Nombre.label("entrenador_nombre_completo"),
        models.persons.Person.Primer_Apellido.label("entrenador_apellido")
    ).join(
        models.users.User, models.clases.Clase.Entrenador_ID == models.users.User.ID
    ).outerjoin(
        models.persons.Person, models.users.User.ID == models.persons.Person.Usuario_ID
    ).offset(skip).limit(limit).all()
    
    clases_con_detalles = []
    for result in results:
        clase = result[0]
        clases_con_detalles.append({
            "ID": clase.ID,
            "Entrenador_ID": clase.Entrenador_ID,
            "Nombre": clase.Nombre,
            "Descripcion": clase.Descripcion,
            "Dia_Inicio": clase.Dia_Inicio,
            "Dia_Fin": clase.Dia_Fin,
            "Hora_Inicio": clase.Hora_Inicio,
            "Hora_Fin": clase.Hora_Fin,
            "Duracion_Minutos": clase.Duracion_Minutos,
            "Estatus": clase.Estatus,
            "Fecha_Registro": clase.Fecha_Registro,
            "Fecha_Actualizacion": clase.Fecha_Actualizacion,
            "Entrenador_Nombre": result[1] or "Sin nombre",
            "Entrenador_Nombre_Completo": result[2] or "",
            "Entrenador_Apellido": result[3] or ""
        })
    
    return clases_con_detalles