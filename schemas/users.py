from typing import List, Union, Optional
from pydantic  import BaseModel
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    Persona_Id: Optional[int] = None
    Nombre_Usuario:str
    Contrasena:str
    Correo_Electronico:str
    Numero_Telefonico_Movil:str
    Estatus:str
    Fecha_Registro: datetime
    Fecha_Actualizacion: datetime

class EstatusUsuario(str, Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    BLOQUEADO = "Bloqueado"
    SUSPENDIDO = "Suspendido"

class UserCreate(UserBase):
    Contrasena: str
    Numero_Telefonico_Movil: Optional[str] = None
    Estatus: EstatusUsuario = EstatusUsuario.ACTIVO
    Google_ID: Optional[str] = None
    Foto_Perfil: Optional[str] = None
    Fecha_Registro: Optional[datetime] = None
    Fecha_Actualizacion: Optional[datetime] = None

class UserUpdate(UserBase):
    pass

class User(UserBase):
    ID:int
    Persona_Id: Optional[int] = None
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    Correo_Electronico: str
    Contrasena: str

class UserCreateRequest(BaseModel):
    Nombre_Usuario: str
    Correo_Electronico: str
    Contrasena: str
    Numero_Telefonico_Movil: Optional[str] = None

class UserVerifyByCode(BaseModel):
    email: str
    code: str

class UserLoginResponse(BaseModel):
    ID: int
    Nombre_Usuario: str
    Correo_Electronico: str
    roles: List[str] = []
    token: str
    
    class Config:
        from_attributes = True