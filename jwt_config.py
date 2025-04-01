from jwt import encode, decode

def solicita_token(dato: dict, roles: list = None) -> dict:
    # Si roles es None, inicializar como lista vacía
    if roles is None:
        roles = []
    
    # Añadir roles al payload
    payload = dato.copy()
    payload["roles"] = roles
    
    # Generar token
    token: str = encode(payload=payload, key='mi_clave', algorithm='HS256')
    
    # Crear respuesta con token y datos adicionales
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": dato.get("ID", 0),
        "username": dato.get("Nombre_Usuario", ""),
        "email": dato.get("Correo_Electronico", ""),
        "roles": roles
    }

def valida_token(token: str) -> dict:
    dato: dict = decode(token, key='mi_clave', algorithms=['HS256'])
    return dato

# Alias para compatibilidad
decode_token = valida_token