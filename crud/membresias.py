import models.membresias
#import models.miembros
import schemas.membresias
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import func, desc
from math import ceil

def get_membresia(db: Session, id: int):
    return db.query(models.membresias.Membresia).filter(models.membresias.Membresia.ID == id).first()

def get_membresias_count_by_type(db: Session):
    result = db.query(
        models.membresias.Membresia.Tipo,
        func.count(models.membresias.Membresia.Tipo).label('count')
    ).join(models.miembros.Miembro, models.miembros.Miembro.Membresia_ID == models.membresias.Membresia.ID).group_by(models.membresias.Membresia.Tipo).all()

    result_dict = {tipo: count for tipo, count in result}
    
    return result_dict

def get_membresia_by_id(db: Session, codigo: str):
    return db.query(models.membresias.Membresia).filter(models.membresias.Membresia.Codigo == codigo).first()

def get_membresias(db: Session, skip: int = 0, limit: int = 10):
    # total_membresias = db.query(func.count(models.membresias.Membresia.ID)).scalar()
    
    # total_pages = ceil(total_membresias / limit)
    
    db_membresias = db.query(models.membresias.Membresia).order_by(desc(models.membresias.Membresia.ID)).offset(skip).limit(limit).all()

    # return {
    #     "total_membresias": total_membresias,
    #     "total_pages": total_pages,
    #     "current_page": (skip // limit) + 1,
    #     "membresias": db_membresias
    # }
    return db_membresias

def create_membresias(db: Session, nom: schemas.membresias.MembresiaCreate):
    db_user = models.membresias.Membresia(
                                      Codigo=nom.Codigo,
                                      Tipo=nom.Tipo,
                                      Tipo_Servicios=nom.Tipo_Servicios, 
                                      Tipo_Plan=nom.Tipo_Plan,
                                      Nivel=nom.Nivel,  
                                      Fecha_Inicio=nom.Fecha_Inicio,
                                      Estatus=nom.Estatus, 
                                      Fecha_Registro=nom.Fecha_Registro, 
                                      Fecha_Actualizacion=nom.Fecha_Actualizacion )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_membresias(db: Session, id: int, person: schemas.membresias.MembresiaUpdate):
    db_user = db.query(models.membresias.Membresia).filter(models.membresias.Membresia.ID == id).first()
    if db_user:
        for var, value in vars(person).items():
            setattr(db_user, var, value) if value else None
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_membresias(db: Session, id: int):
    db_user = db.query(models.membresias.Membresia).filter(models.membresias.Membresia.ID == id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user