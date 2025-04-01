from typing import List, Union
from pydantic import BaseModel
from datetime import datetime

class PromocionBase(BaseModel):
    Producto_id: int
    Tipo: str
    Aplicacion_en: str
    Fecha_Registro: datetime
    Fecha_Actualizacion: datetime
    Estatus: bool

class PromocionCreate(PromocionBase):
    pass

class PromocionUpdate(PromocionBase):
    pass

class Promocion(PromocionBase):
    ID: int
    class Config:
        orm_mode = True
