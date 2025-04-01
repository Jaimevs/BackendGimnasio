import models.promociones
import schemas.promociones
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

def get_promocion(db: Session, id: int):
    try:
        return db.query(models.promociones.Promocion).filter(models.promociones.Promocion.ID == id).one_or_none()
    except NoResultFound:
        return None

def get_promocions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.promociones.Promocion).offset(skip).limit(limit).all()

def create_promocion(db: Session, promocion: schemas.promociones.PromocionCreate):
    db_promocion = models.promociones.Promocion(
        Producto_id=promocion.Producto_id,
        Tipo=promocion.Tipo,
        Aplicacion_en=promocion.Aplicacion_en, 
        Fecha_Registro=promocion.Fecha_Registro,
        Fecha_Actualizacion=promocion.Fecha_Actualizacion,
        Estatus=promocion.Estatus
    )
    db.add(db_promocion)
    db.commit()
    db.refresh(db_promocion)
    return db_promocion

def update_promocion(db: Session, id: int, promocion: schemas.promociones.PromocionUpdate):
    db_promocion = db.query(models.promociones.Promocion).filter(models.promociones.Promocion.ID == id).one_or_none()
    if db_promocion:
        update_data = promocion.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_promocion, key, value)
        db.commit()
        db.refresh(db_promocion)
    return db_promocion

def delete_promocion(db: Session, id: int):
    db_promocion = db.query(models.promociones.Promocion).filter(models.promociones.Promocion.ID == id).one_or_none()
    if db_promocion:
        db.delete(db_promocion)
        db.commit()
    return db_promocion
