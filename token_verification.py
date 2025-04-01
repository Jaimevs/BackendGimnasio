# token_verification.py
import os
import json
import time
import uuid
from datetime import datetime, timedelta

# Archivo para almacenar los registros pendientes
PENDING_REGISTRATIONS_FILE = "pending_registrations.json"
# Tiempo de expiración (24 horas)
EXPIRATION_TIME = 24 * 60 * 60  # en segundos

def store_pending_registration(user_data: dict, verification_code: str):
    """
    Almacena los datos del usuario pendiente de verificación junto con su código
    """
    # Generar un token único
    token = str(uuid.uuid4())
    
    # Crear estructura para almacenar
    pending_data = {
        "user_data": user_data,
        "verification_code": verification_code,
        "created_at": time.time(),
        "expires_at": time.time() + EXPIRATION_TIME
    }
    
    # Cargar registros existentes
    pending_registrations = {}
    if os.path.exists(PENDING_REGISTRATIONS_FILE):
        try:
            with open(PENDING_REGISTRATIONS_FILE, "r") as f:
                pending_registrations = json.load(f)
        except json.JSONDecodeError:
            pending_registrations = {}
    
    # Añadir nuevo registro
    pending_registrations[token] = pending_data
    
    # Guardar actualización
    with open(PENDING_REGISTRATIONS_FILE, "w") as f:
        json.dump(pending_registrations, f)
    
    return token

def verify_code(email: str, code: str):
    """
    Verifica si el código proporcionado es válido para el correo electrónico
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return None
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return None
    
    # Buscar registro por email y código
    for token, data in pending_registrations.items():
        user_data = data.get("user_data", {})
        if (user_data.get("Correo_Electronico") == email and 
            data.get("verification_code") == code and 
            data.get("expires_at", 0) > time.time()):
            return user_data
    
    return None

def get_pending_registration(token: str):
    """
    Obtiene los datos de un registro pendiente por token
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return None
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return None
    
    # Verificar si el token existe y no ha expirado
    if token in pending_registrations:
        data = pending_registrations[token]
        if data.get("expires_at", 0) > time.time():
            return data.get("user_data")
    
    return None

def remove_pending_registration(token: str):
    """
    Elimina un registro pendiente después de la verificación
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return False
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return False
    
    # Eliminar registro si existe
    if token in pending_registrations:
        del pending_registrations[token]
        
        # Guardar actualización
        with open(PENDING_REGISTRATIONS_FILE, "w") as f:
            json.dump(pending_registrations, f)
        
        return True
    
    return False

def verify_code(email: str, code: str):
    """
    Verifica si el código proporcionado es válido para el correo electrónico
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return None
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return None
    
    # Buscar registro por email y código
    for token, data in pending_registrations.items():
        user_data = data.get("user_data", {})
        if (user_data.get("Correo_Electronico") == email and 
            data.get("verification_code") == code and 
            data.get("expires_at", 0) > time.time()):
            return user_data
    
    return None