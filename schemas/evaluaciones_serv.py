from typing import List, Union
from pydantic  import BaseModel
from datetime import datetime

class Evaluaciones_servBase(BaseModel):
    Usuario_ID:int
    Servicios:str
    Calificacion:str
    Criterio:str
    Estatus:bool
    Fecha_Registro: datetime
   
    
    

class Evaluaciones_servCreate(Evaluaciones_servBase):
    pass

class Evaluaciones_servUpdate(Evaluaciones_servBase):
    pass

class Evaluaciones_serv(Evaluaciones_servBase):
    ID:int
    class Config:
        orm_mode = True

        