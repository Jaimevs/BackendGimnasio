from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class TipoEnum(str, Enum):
    Miembro = "Miembro"
    Empleado = "Empleado"
    Usuario = "Usuario"

class AplicacionEnum(str, Enum):
    Tienda_Virtual = "Tienda virtual"
    Tienda_Presencial = "Tienda presencial"

class PromocionBase(BaseModel):
    Nombre: str
    Descripcion: Optional[str] = None
    Tipo: TipoEnum
    Descuento: float = Field(..., ge=0.0, le=100.0)  # Descuento entre 0 y 100%
    Aplicacion_en: AplicacionEnum
    Fecha_Inicio: datetime
    Fecha_Fin: Optional[datetime] = None
    Estatus: Optional[bool] = True
    
    @validator('Fecha_Fin')
    def fecha_fin_despues_de_inicio(cls, v, values):
        if v and 'Fecha_Inicio' in values and v < values['Fecha_Inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class PromocionCreate(PromocionBase):
    Usuario_ID: int
    # Producto_id: int  # Comentado por ahora

class PromocionUpdate(BaseModel):
    Nombre: Optional[str] = None
    Descripcion: Optional[str] = None
    Tipo: Optional[TipoEnum] = None
    Descuento: Optional[float] = Field(None, ge=0.0, le=100.0)
    Aplicacion_en: Optional[AplicacionEnum] = None
    Fecha_Inicio: Optional[datetime] = None
    Fecha_Fin: Optional[datetime] = None
    Estatus: Optional[bool] = None
    
    @validator('Fecha_Fin')
    def fecha_fin_despues_de_inicio(cls, v, values):
        if v and 'Fecha_Inicio' in values and values['Fecha_Inicio'] and v < values['Fecha_Inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class Promocion(PromocionBase):
    ID: int
    Usuario_ID: int
    # Producto_id: int  # Comentado por ahora
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class PromocionDetalle(Promocion):
    Usuario_Nombre: Optional[str] = None
    # Producto_Nombre: Optional[str] = None  # Comentado por ahora