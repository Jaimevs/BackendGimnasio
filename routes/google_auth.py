# routes/google_auth.py (Improved Version)
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import config.db
from crud import users
import schemas.users
import models.users
from jwt_config import solicita_token
from datetime import datetime
import httpx
import json
import os
import logging
import traceback
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Google OAuth configurations
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")
FRONTEND_CALLBACK_URL = os.getenv("FRONTEND_CALLBACK_URL", "http://gym-customer.onrender.com/login/oauth")

# Google API endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

router = APIRouter(tags=["Authentication"])

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/auth/google")
async def login_google():
    """
    Inicia el flujo de autenticación con Google OAuth
    """
    # Log the start of Google OAuth flow
    logger.info("Starting Google OAuth authentication flow")
    logger.debug(f"Client ID: {GOOGLE_CLIENT_ID[:5]}...")
    logger.debug(f"Redirect URI: {GOOGLE_REDIRECT_URI}")
    
    # Definir los scopes requeridos
    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    # Construir la URL de autorización de Google
    authorize_url = f"{GOOGLE_AUTH_URL}?client_id={GOOGLE_CLIENT_ID}&redirect_uri={quote_plus(GOOGLE_REDIRECT_URI)}&response_type=code&scope={quote_plus(' '.join(scopes))}&access_type=offline&prompt=consent"
    
    logger.info(f"Generated authorization URL: {authorize_url[:100]}...")
    return RedirectResponse(url=authorize_url)

@router.get("/auth/callback")
async def auth_google_callback(code: str, db: Session = Depends(get_db)):
    """
    Callback para procesar la respuesta de Google OAuth
    """
    try:
        # Validate input
        if not code:
            logger.error("No authorization code received")
            return RedirectResponse(url=f"{FRONTEND_URL}/login/oauth?error=no_code")
        
        logger.info(f"Received authorization code: {code[:10]}...")
        
        # Obtener token de acceso
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Detailed token request logging
                logger.debug("Attempting to retrieve access token")
                token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
                
                # Check response status
                if token_response.status_code != 200:
                    logger.error(f"Token retrieval failed: {token_response.status_code}")
                    logger.error(f"Response content: {token_response.text}")
                    return RedirectResponse(url=f"{FRONTEND_URL}/login/oauth?error=token_retrieval_failed")
                
                tokens = token_response.json()
                logger.info("Successfully retrieved access token")
                
                # Obtenemos la información del usuario de Google
                headers = {"Authorization": f"Bearer {tokens['access_token']}"}
                user_info_response = await client.get(GOOGLE_USER_INFO_URL, headers=headers)
                
                if user_info_response.status_code != 200:
                    logger.error(f"User info retrieval failed: {user_info_response.status_code}")
                    logger.error(f"Response content: {user_info_response.text}")
                    return RedirectResponse(url=f"{FRONTEND_URL}/login/oauth?error=user_info_failed")
                
                user_info = user_info_response.json()
                logger.info("Successfully retrieved user information")
            
            except Exception as token_error:
                logger.error(f"Token request error: {token_error}")
                logger.error(traceback.format_exc())
                return RedirectResponse(url=f"{FRONTEND_URL}/login/oauth?error=token_request_failed")
        
        # Extraer datos relevantes de Google
        google_id = user_info["sub"]
        email = user_info["email"]
        name = user_info.get("name", "")
        picture = user_info.get("picture", "")
        
        logger.info(f"Processing user: {email}")
        
        # Verificar si el usuario ya existe en la base de datos
        user = users.get_user_by_email(db, email=email)
        
        if not user:
            logger.info(f"Creating new user for email: {email}")
            # Crear un nuevo usuario si no existe
            current_time = datetime.now()
            username = name.replace(" ", "_").lower() if name else email.split("@")[0]
            
            # Comprobar si el nombre de usuario ya existe
            existing_user = users.get_user_by_usuario(db, usuario=username)
            if existing_user:
                # Añadir un identificador único si ya existe
                username = f"{username}_{google_id[-6:]}"
            
            # Crear nuevo usuario con datos de Google
            user_data = schemas.users.UserCreate(
                Nombre_Usuario=username,
                Correo_Electronico=email,
                Contrasena="",  # Se generará un hash aleatorio en create_user_google
                Numero_Telefonico_Movil="",
                Estatus=schemas.users.EstatusUsuario.ACTIVO,
                Google_ID=google_id,
                Foto_Perfil=picture,
                Fecha_Registro=current_time,
                Fecha_Actualizacion=current_time
            )
            
            # Crear usuario en la base de datos
            user = users.create_user_google(db=db, user=user_data)
            
            # Asignar rol de usuario por defecto
            role = users.get_role_by_name(db, "usuario")
            if role:
                users.assign_role_to_user(db, user_id=user.ID, role_id=role.ID)
            
            logger.info(f"New user created: {username}")
        else:
            logger.info(f"Existing user found: {user.Nombre_Usuario}")
        
        # Obtener los roles del usuario
        roles_names = [rol.Nombre for rol in user.roles] if user.roles else ["usuario"]
        
        # Generar token JWT con el mismo formato que el login normal
        token_data = {
            "ID": user.ID,
            "Nombre_Usuario": user.Nombre_Usuario,
            "Correo_Electronico": user.Correo_Electronico
        }
        
        # Usar la misma función solicita_token para generar el token igual que el login normal
        token_response = solicita_token(token_data, roles=roles_names)
        
        # Obtener el token de access_token
        token = token_response["access_token"]
        
        # Verificar que el token sea un string
        if not isinstance(token, str):
            logger.error(f"Token is not a string: {type(token)}")
            raise ValueError(f"El token no es un string: {type(token)}")
        
        # Preparar respuesta con el formato completo para uso en frontend
        response_data = {
            "ID": user.ID,
            "Nombre_Usuario": user.Nombre_Usuario,
            "Correo_Electronico": user.Correo_Electronico,
            "roles": roles_names,
            "token": {
                "access_token": token,
                "token_type": "bearer",
                "user_id": user.ID,
                "username": user.Nombre_Usuario,
                "email": user.Correo_Electronico,
                "roles": roles_names
            }
        }
        
        # Codificar datos para pasarlos en URL
        encoded_data = quote_plus(json.dumps(response_data))
        
        logger.info("Successfully generated JWT token")
        
        # Redirigir al frontend con el token y datos adicionales
        redirect_url = f"{FRONTEND_CALLBACK_URL}?data={encoded_data}"
        logger.info(f"Redirecting to: {redirect_url[:100]}...")
        return RedirectResponse(url=redirect_url)
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        logger.error(traceback.format_exc())
        redirect_url = f"{FRONTEND_URL}/login/oauth?error=authentication_failed"
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        logger.error(f"Error procesando callback de Google: {e}")
        logger.error(traceback.format_exc())
        redirect_url = f"{FRONTEND_URL}/login/oauth?error=server_error"
        return RedirectResponse(url=redirect_url)