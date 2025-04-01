from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jwt_config import valida_token
import crud.users, config.db
import models.users
import models.rols

# Ahora que ambos modelos están importados, crea las tablas
config.db.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class Portador(HTTPBearer):
    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        autorizacion = await super().__call__(request)
        dato = valida_token(autorizacion.credentials)
        
        # Verificar si existe el ID del usuario en el token
        if "ID" not in dato:
            raise HTTPException(status_code=401, detail="Token inválido o mal formado")
        
        # Obtener el usuario por ID
        user_id = dato["ID"]
        db_user = crud.users.get_user(db=db, id=user_id)
        
        if db_user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return autorizacion.credentials  # Devolvemos el token para uso en otros endpoints