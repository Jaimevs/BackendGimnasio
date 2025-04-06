from typing import List, Union, Optional
from pydantic import BaseModel
from datetime import datetime, date

class PersonBase(BaseModel):
    Titulo_Cortesia: Optional[str] = None
    Nombre: str
    Primer_Apellido: str
    Segundo_Apellido: Optional[str] = None
    Fecha_Nacimiento: Optional[datetime] = None
    Fotografia: Optional[str] = None
    Genero: Optional[str] = None
    Tipo_Sangre: Optional[str] = None
    Estatus: bool
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None
    # Nuevos campos añadidos
    Numero_Telefonico: Optional[str] = None
    Estatura: Optional[float] = None
    Peso: Optional[float] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class Person(PersonBase):
    ID: int
    Usuario_ID: Optional[int] = None
    
    class Config:
        orm_mode = True