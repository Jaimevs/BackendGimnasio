from typing import List,Union
from pydantic import BaseModel
from datetime import datetime
from models.servicios_clientes import MyTipo


class Servicio_ClienteBase(BaseModel):
    Persona_ID: str
    Tipo_Servicio:  MyTipo 
    Descripcion: str
    Comentarios: str
    Estatus:bool
    Fecha_Registro:datetime
    Fecha_Actualizacion:datetime

class Servicio_ClienteCreate(Servicio_ClienteBase):
    pass
class Servicio_ClienteUpdate(Servicio_ClienteBase):
    pass
class Servicio_Cliente(Servicio_ClienteBase):
    ID:int
    #owner_id:int clave foranea
    
    class Config:
        orm_mode=True
