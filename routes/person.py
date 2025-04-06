from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import crud.persons, config.db, schemas.persons, models.persons
import crud.users
from typing import List
from portadortoken import Portador
from datetime import datetime
from pydantic import BaseModel

# Modelo para la creación/actualización de personas vinculadas a un usuario
class PersonUserCreate(BaseModel):
    Titulo_Cortesia: str = None
    Nombre: str
    Primer_Apellido: str
    Segundo_Apellido: str = None
    Fecha_Nacimiento: datetime = None
    Fotografia: str = None
    Genero: str = None
    Tipo_Sangre: str = None
    Numero_Telefonico: str = None
    Estatura: float = None
    Peso: float = None

key = Fernet.generate_key()
f = Fernet(key)

person = APIRouter()
models.persons.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para que el usuario cree su información personal
@person.post('/userprofile/', response_model=schemas.persons.Person, tags=['Perfil de Usuario'])
def create_user_profile(
    person_data: PersonUserCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Obtener el ID del usuario desde la información decodificada
    user_id = current_user.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Buscar el usuario en la base de datos
    db_user = crud.users.get_user(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el usuario ya tiene un perfil asociado
    existing_profile = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == user_id
    ).first()
    
    if existing_profile:
        raise HTTPException(status_code=400, detail="El usuario ya tiene un perfil creado. Use PUT para actualizar.")
    
    # Crear objeto Person con la información proporcionada
    current_time = datetime.now()
    person_create = schemas.persons.PersonCreate(
        Titulo_Cortesia=person_data.Titulo_Cortesia,
        Nombre=person_data.Nombre,
        Primer_Apellido=person_data.Primer_Apellido,
        Segundo_Apellido=person_data.Segundo_Apellido,
        Fecha_Nacimiento=person_data.Fecha_Nacimiento,
        Fotografia=person_data.Fotografia,
        Genero=person_data.Genero,
        Tipo_Sangre=person_data.Tipo_Sangre,
        Estatus=True,
        Fecha_Registro=current_time,
        Fecha_Actualizacion=current_time
    )
    
    # Crear la persona en la base de datos
    db_person = crud.persons.create_person(db=db, person=person_create)
    
    # Asociar la persona con el usuario
    db_person.Usuario_ID = user_id
    db_person.Numero_Telefonico = person_data.Numero_Telefonico
    db_person.Estatura = person_data.Estatura
    db_person.Peso = person_data.Peso
    
    db.commit()
    db.refresh(db_person)
    
    return db_person

# Endpoint para que el usuario obtenga su información personal
@person.get('/userprofile/', response_model=schemas.persons.Person, tags=['Perfil de Usuario'])
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Obtener el ID del usuario desde la información decodificada
    user_id = current_user.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Buscar el perfil del usuario en la base de datos
    user_profile = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == user_id
    ).first()
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="No se ha encontrado el perfil para este usuario")
    
    return user_profile

# Endpoint para que el usuario actualice su información personal
@person.put('/userprofile/', response_model=schemas.persons.Person, tags=['Perfil de Usuario'])
def update_user_profile(
    person_data: PersonUserCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Obtener el ID del usuario desde la información decodificada
    user_id = current_user.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Buscar el perfil del usuario en la base de datos
    user_profile = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == user_id
    ).first()
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="No se ha encontrado el perfil para este usuario. Debe crear uno primero.")
    
    # Actualizar los campos con los nuevos valores
    if person_data.Titulo_Cortesia is not None:
        user_profile.Titulo_Cortesia = person_data.Titulo_Cortesia
    if person_data.Nombre is not None:
        user_profile.Nombre = person_data.Nombre
    if person_data.Primer_Apellido is not None:
        user_profile.Primer_Apellido = person_data.Primer_Apellido
    if person_data.Segundo_Apellido is not None:
        user_profile.Segundo_Apellido = person_data.Segundo_Apellido
    if person_data.Fecha_Nacimiento is not None:
        user_profile.Fecha_Nacimiento = person_data.Fecha_Nacimiento
    if person_data.Fotografia is not None:
        user_profile.Fotografia = person_data.Fotografia
    if person_data.Genero is not None:
        user_profile.Genero = person_data.Genero
    if person_data.Tipo_Sangre is not None:
        user_profile.Tipo_Sangre = person_data.Tipo_Sangre
    if person_data.Numero_Telefonico is not None:
        user_profile.Numero_Telefonico = person_data.Numero_Telefonico
    if person_data.Estatura is not None:
        user_profile.Estatura = person_data.Estatura
    if person_data.Peso is not None:
        user_profile.Peso = person_data.Peso
    
    user_profile.Fecha_Actualizacion = datetime.now()
    
    db.commit()
    db.refresh(user_profile)
    
    return user_profile