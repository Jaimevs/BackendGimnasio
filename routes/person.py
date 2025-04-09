from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import crud.persons, config.db, schemas.persons, models.persons
import crud.users
from typing import List
from portadortoken import Portador
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from fastapi import File, UploadFile, Form
import base64
import boto3
import os
from botocore.exceptions import NoCredentialsError

# Definir el router al principio del archivo
person = APIRouter()
models.persons.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuración de AWS S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Inicializar cliente S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

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

class PersonUserResponse(BaseModel):
    Nombre: str
    Primer_Apellido: str
    Segundo_Apellido: Optional[str] = None 
    Numero_Telefonico: Optional[str] = None
    Nombre_Usuario: str
    Correo_Electronico: str

class PersonUserBasicCreate(BaseModel):
    Nombre: str
    Primer_Apellido: str
    Numero_Telefonico: Optional[str] = None
    Segundo_Apellido: Optional[str] = None
    Nombre_Usuario: Optional[str] = None
    Correo_Electronico: Optional[str] = None

key = Fernet.generate_key()
f = Fernet(key)

# Endpoint para subir imagen de perfil
@person.post('/upload-profile-image/', tags=['Perfil de Usuario'])
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Validar token y usuario
    user_id = current_user.get("ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Verificar perfil de usuario
    user_profile = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == user_id
    ).first()
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="No se ha encontrado el perfil para este usuario")
    
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        
        # Limitar tamaño de archivo (5MB)
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="El archivo es demasiado grande (máximo 5MB)")
        
        # Generar nombre único para el archivo
        file_extension = file.filename.split(".")[-1].lower()
        
        # Validar extensiones permitidas
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Formato de archivo no permitido. Use: {', '.join(allowed_extensions)}")
        
        file_name = f"user_{user_id}/profile_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        
        # Subir a S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=file_content,
            ContentType=file.content_type,
            ACL='public-read'
        )
        
        # Generar URL de S3
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
        
        # Actualizar perfil de usuario con la URL de la imagen
        user_profile.Fotografia = s3_url
        user_profile.Fecha_Actualizacion = datetime.now()
        db.commit()
        
        return {"message": "Imagen subida exitosamente", "image_url": s3_url}
    
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Error de credenciales de AWS")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")

# Alternativa: Endpoint para subir imagen como Base64
@person.put('/update-profile-image/', tags=['Perfil de Usuario'])
async def update_profile_image(
    image_data: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Validar token y usuario
    user_id = current_user.get("ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Verificar perfil de usuario
    user_profile = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == user_id
    ).first()
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="No se ha encontrado el perfil para este usuario")
    
    try:
        # Verificar formato base64
        if not image_data.startswith('data:image'):
            raise HTTPException(status_code=400, detail="Formato de imagen inválido")
        
        # Separar metadatos y datos binarios
        _, encoded_data = image_data.split(',', 1)
        
        # Decodificar base64
        binary_data = base64.b64decode(encoded_data)
        
        # Verificar tamaño
        if len(binary_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="La imagen es demasiado grande (máximo 5MB)")
            
        # Generar nombre único para el archivo
        file_name = f"user_{user_id}/profile_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        
        # Subir a S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=binary_data,
            ContentType='image/jpeg',
            ACL='public-read'
        )
        
        # Generar URL de S3
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
        
        # Actualizar perfil de usuario con la URL de la imagen
        user_profile.Fotografia = s3_url
        user_profile.Fecha_Actualizacion = datetime.now()
        db.commit()
        
        return {"message": "Imagen actualizada exitosamente", "image_url": s3_url}
    
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Error de credenciales de AWS")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la imagen: {str(e)}")

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


########################

# GET endpoint para obtener información combinada de persona y usuario
@person.get('/personbasic/', response_model=PersonUserResponse, tags=['Perfil de Usuario'])
def get_person_user_basic_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Obtener el ID del usuario desde la información decodificada
    user_id = current_user.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Buscar el usuario en la base de datos
    db_user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Buscar la información personal asociada
    db_person = db.query(models.persons.Person).filter(models.persons.Person.Usuario_ID == user_id).first()
    
    if not db_person:
        raise HTTPException(status_code=404, detail="No se ha encontrado el perfil personal para este usuario")
    
    # Preparar respuesta combinada
    response = PersonUserResponse(
        Nombre=db_person.Nombre,
        Primer_Apellido=db_person.Primer_Apellido,
        Segundo_Apellido=db_person.Segundo_Apellido,  # Incluir Segundo_Apellido
        Numero_Telefonico=db_person.Numero_Telefonico,
        Nombre_Usuario=db_user.Nombre_Usuario,
        Correo_Electronico=db_user.Correo_Electronico
    )
    
    return response

# POST endpoint para crear información básica de persona y actualizar usuario
@person.post('/personbasic/', response_model=PersonUserResponse, tags=['Perfil de Usuario'])
def create_person_user_basic_info(
    data: PersonUserBasicCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Obtener el ID del usuario desde la información decodificada
    user_id = current_user.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Buscar el usuario en la base de datos
    db_user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el usuario ya tiene un perfil personal asociado
    existing_profile = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == user_id
    ).first()
    
    if existing_profile:
        raise HTTPException(status_code=400, detail="El usuario ya tiene un perfil creado. Use PUT para actualizar.")
    
    # Actualizar información del usuario si se proporcionó
    if data.Nombre_Usuario and data.Nombre_Usuario != db_user.Nombre_Usuario:
        # Verificar si el nuevo nombre de usuario ya existe
        existing_username = db.query(models.users.User).filter(
            models.users.User.Nombre_Usuario == data.Nombre_Usuario,
            models.users.User.ID != user_id
        ).first()
        
        if existing_username:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
        
        db_user.Nombre_Usuario = data.Nombre_Usuario
    
    if data.Correo_Electronico and data.Correo_Electronico != db_user.Correo_Electronico:
        # Verificar si el nuevo correo ya existe
        existing_email = db.query(models.users.User).filter(
            models.users.User.Correo_Electronico == data.Correo_Electronico,
            models.users.User.ID != user_id
        ).first()
        
        if existing_email:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está en uso")
        
        db_user.Correo_Electronico = data.Correo_Electronico
    
    # Crear la información personal básica
    current_time = datetime.now()
    new_person = models.persons.Person(
        Nombre=data.Nombre,
        Primer_Apellido=data.Primer_Apellido,
        Segundo_Apellido=data.Segundo_Apellido,  # Incluir Segundo_Apellido
        Numero_Telefonico=data.Numero_Telefonico,
        Usuario_ID=user_id,
        Estatus=True,
        Fecha_Registro=current_time,
        Fecha_Actualizacion=current_time
    )
    
    # Guardar cambios
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    db.refresh(db_user)
    
    # Preparar respuesta
    response = PersonUserResponse(
        Nombre=new_person.Nombre,
        Primer_Apellido=new_person.Primer_Apellido,
        Segundo_Apellido=new_person.Segundo_Apellido,  # Incluir Segundo_Apellido
        Numero_Telefonico=new_person.Numero_Telefonico,
        Nombre_Usuario=db_user.Nombre_Usuario,
        Correo_Electronico=db_user.Correo_Electronico
    )
    
    return response

# PUT endpoint para actualizar información básica de persona y usuario
@person.put('/personbasic/', response_model=PersonUserResponse, tags=['Perfil de Usuario'])
def update_person_user_basic_info(
    data: PersonUserBasicCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(Portador())
):
    # Obtener el ID del usuario desde la información decodificada
    user_id = current_user.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")
    
    # Buscar el usuario en la base de datos
    db_user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Buscar la información personal asociada
    db_person = db.query(models.persons.Person).filter(models.persons.Person.Usuario_ID == user_id).first()
    
    if not db_person:
        # Si no existe el perfil personal, crear uno nuevo en lugar de dar error
        current_time = datetime.now()
        db_person = models.persons.Person(
            Nombre=data.Nombre,
            Primer_Apellido=data.Primer_Apellido,
            Segundo_Apellido=data.Segundo_Apellido,  # Incluir Segundo_Apellido
            Numero_Telefonico=data.Numero_Telefonico,
            Usuario_ID=user_id,
            Estatus=True,
            Fecha_Registro=current_time,
            Fecha_Actualizacion=current_time
        )
        db.add(db_person)
    else:
        # Actualizar datos personales existentes
        if data.Nombre:
            db_person.Nombre = data.Nombre
        if data.Primer_Apellido:
            db_person.Primer_Apellido = data.Primer_Apellido
        if data.Segundo_Apellido is not None:  # Verificar explícitamente None para permitir strings vacíos
            db_person.Segundo_Apellido = data.Segundo_Apellido
        if data.Numero_Telefonico:
            db_person.Numero_Telefonico = data.Numero_Telefonico
        
        db_person.Fecha_Actualizacion = datetime.now()
    
    # Actualizar información del usuario si se proporcionó
    if data.Nombre_Usuario and data.Nombre_Usuario != db_user.Nombre_Usuario:
        # Verificar si el nuevo nombre de usuario ya existe
        existing_username = db.query(models.users.User).filter(
            models.users.User.Nombre_Usuario == data.Nombre_Usuario,
            models.users.User.ID != user_id
        ).first()
        
        if existing_username:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
        
        db_user.Nombre_Usuario = data.Nombre_Usuario
    
    if data.Correo_Electronico and data.Correo_Electronico != db_user.Correo_Electronico:
        # Verificar si el nuevo correo ya existe
        existing_email = db.query(models.users.User).filter(
            models.users.User.Correo_Electronico == data.Correo_Electronico,
            models.users.User.ID != user_id
        ).first()
        
        if existing_email:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está en uso")
        
        db_user.Correo_Electronico = data.Correo_Electronico
    
    # Actualizar fecha de actualización del usuario
    db_user.Fecha_Actualizacion = datetime.now()
    
    # Guardar cambios
    db.commit()
    db.refresh(db_person)
    db.refresh(db_user)
    
    # Preparar respuesta
    response = PersonUserResponse(
        Nombre=db_person.Nombre,
        Primer_Apellido=db_person.Primer_Apellido,
        Segundo_Apellido=db_person.Segundo_Apellido,  # Incluir Segundo_Apellido
        Numero_Telefonico=db_person.Numero_Telefonico,
        Nombre_Usuario=db_user.Nombre_Usuario,
        Correo_Electronico=db_user.Correo_Electronico
    )
    
    return response