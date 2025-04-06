from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jwt_config import valida_token
import crud.users, config.db
import models.users
import models.rols
import jwt

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
        try:
            # Obtener la autorización
            autorizacion = await super().__call__(request)
            print(f"Token recibido: {autorizacion.credentials[:15]}...")
            
            # Verificar el formato básico del token
            parts = autorizacion.credentials.split('.')
            if len(parts) != 3:
                print(f"Token malformado: tiene {len(parts)} partes en lugar de 3")
                raise HTTPException(
                    status_code=401, 
                    detail="Formato de token JWT inválido"
                )
            
            # Validar el token
            dato = valida_token(autorizacion.credentials)
            print(f"Token validado, ID de usuario: {dato.get('ID')}")
            
            # Verificar si existe el ID del usuario en el token
            if "ID" not in dato:
                print("Token no contiene ID")
                raise HTTPException(status_code=401, detail="Token inválido o mal formado")
            
            # Obtener el usuario por ID
            user_id = dato["ID"]
            db_user = crud.users.get_user(db=db, id=user_id)
            
            if db_user is None:
                print(f"Usuario con ID {user_id} no encontrado en la base de datos")
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            # Verificar los roles del usuario
            roles = dato.get("roles", [])
            print(f"Roles del usuario: {roles}")
                
            return dato  # Devolver el dato decodificado, no el token
        except jwt.exceptions.DecodeError as e:
            print(f"Error al decodificar el token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Error al decodificar el token: {str(e)}"
            )
        except jwt.exceptions.ExpiredSignatureError:
            print("Token expirado")
            raise HTTPException(
                status_code=401,
                detail="El token ha expirado"
            )
        except jwt.exceptions.InvalidTokenError as e:
            print(f"Token inválido: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Token inválido: {str(e)}"
            )
        except Exception as e:
            print(f"Error inesperado en validación del token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Error de autenticación: {str(e)}"
            )