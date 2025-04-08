from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from config.db import get_db, engine
from portadortoken import Portador
import crud.quejas
import schemas.quejas
import models.users
import models.quejas
import models.clases
from datetime import datetime

feedback_router = APIRouter()

# Crear las tablas si no existen
models.quejas.Base.metadata.create_all(bind=engine)

# Ruta para obtener una queja específica
@feedback_router.get('/quejas/{id}', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def read_queja(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la queja
    db_queja = crud.quejas.get_queja(db=db, id=id)
    if db_queja is None:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    # Verificar si el usuario es el autor de la queja, el entrenador evaluado o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if db_queja.Usuario_ID != user_id and db_queja.Entrenador_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta queja")
    
    return db_queja

# Ruta para crear una queja
@feedback_router.post('/quejas/', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def create_queja(queja: schemas.quejas.QuejaCreate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el entrenador exista y tenga rol de entrenador
    entrenador = db.query(models.users.User).filter(models.users.User.ID == queja.Entrenador_ID).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    
    # Verificar si tiene rol de entrenador
    is_entrenador = False
    for rol in entrenador.roles:
        if rol.Nombre == "entrenador":
            is_entrenador = True
            break
    
    if not is_entrenador:
        raise HTTPException(status_code=400, detail="El usuario seleccionado no es un entrenador")
    
    # Verificar que la clase exista y pertenezca al entrenador
    clase = db.query(models.clases.Clase).filter(models.clases.Clase.ID == queja.Clase_ID).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    if clase.Entrenador_ID != queja.Entrenador_ID:
        raise HTTPException(status_code=400, detail="La clase seleccionada no pertenece al entrenador indicado")
    
    # Verificar que la calificación esté entre 1 y 5
    if queja.Calificacion < 1 or queja.Calificacion > 5:
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5 estrellas")
    
    return crud.quejas.create_queja(db=db, queja=queja, usuario_id=user_id)

# Ruta para actualizar una queja
@feedback_router.put('/quejas/{id}', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def update_queja(id: int, queja: schemas.quejas.QuejaUpdate, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la queja
    db_queja = crud.quejas.get_queja(db=db, id=id)
    if db_queja is None:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    # Verificar si el usuario es el autor de la queja
    if db_queja.Usuario_ID != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes actualizar tus propias quejas")
    
    # Verificar que la calificación esté entre 1 y 5 si se proporciona
    if queja.Calificacion is not None and (queja.Calificacion < 1 or queja.Calificacion > 5):
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5 estrellas")
    
    return crud.quejas.update_queja(db=db, id=id, queja=queja)

# Ruta para eliminar una queja
@feedback_router.delete('/quejas/{id}', response_model=schemas.quejas.Queja, tags=['Feedback'], dependencies=[Depends(Portador())])
def delete_queja(id: int, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Obtener la queja
    db_queja = crud.quejas.get_queja(db=db, id=id)
    if db_queja is None:
        raise HTTPException(status_code=404, detail="Queja no encontrada")
    
    # Verificar si el usuario es el autor de la queja o un admin
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if db_queja.Usuario_ID != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propias quejas o ser administrador")
    
    return crud.quejas.delete_queja(db=db, id=id)

# Ruta para obtener mis quejas
@feedback_router.get('/mis-quejas/', response_model=List[schemas.quejas.Queja], tags=['Feedback'], dependencies=[Depends(Portador())])
def read_mis_quejas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token_data = Depends(Portador())):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return crud.quejas.get_quejas_by_usuario(db=db, usuario_id=user_id, skip=skip, limit=limit)


# Ruta para obtener estadísticas de quejas para administradores
@feedback_router.get('/admin/quejas/estadisticas/', tags=['Feedback Admin'], dependencies=[Depends(Portador())])
def get_estadisticas_quejas_admin(
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario tenga rol de administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden acceder a este recurso")
    
    # Obtener todas las quejas
    quejas = db.query(models.quejas.Queja).all()
    
    # Preparar estadísticas
    total_quejas = len(quejas)
    
    if total_quejas == 0:
        return {
            "total_quejas": 0,
            "promedio_calificacion": 0,
            "distribucion_calificaciones": {
                "5_estrellas": 0,
                "4_estrellas": 0,
                "3_estrellas": 0,
                "2_estrellas": 0,
                "1_estrella": 0
            },
            "top_entrenadores": [],
            "tendencia_calificaciones": []
        }
    
    # Calcular promedio de calificaciones
    suma_calificaciones = sum(queja.Calificacion for queja in quejas)
    promedio_calificacion = round(suma_calificaciones / total_quejas, 2)
    
    # Calcular distribución de calificaciones
    distribucion = {
        "5_estrellas": 0,
        "4_estrellas": 0,
        "3_estrellas": 0,
        "2_estrellas": 0,
        "1_estrella": 0
    }
    
    for queja in quejas:
        if queja.Calificacion == 5:
            distribucion["5_estrellas"] += 1
        elif queja.Calificacion == 4:
            distribucion["4_estrellas"] += 1
        elif queja.Calificacion == 3:
            distribucion["3_estrellas"] += 1
        elif queja.Calificacion == 2:
            distribucion["2_estrellas"] += 1
        elif queja.Calificacion == 1:
            distribucion["1_estrella"] += 1
    
    # Calcular porcentajes
    for key in distribucion:
        distribucion[key] = round((distribucion[key] / total_quejas) * 100, 2) if total_quejas > 0 else 0
    
    # Obtener top entrenadores por calificación
    # Agrupar quejas por entrenador
    entrenadores_data = {}
    
    for queja in quejas:
        if queja.Entrenador_ID not in entrenadores_data:
            entrenadores_data[queja.Entrenador_ID] = {
                "entrenador_id": queja.Entrenador_ID,
                "total_quejas": 0,
                "suma_calificaciones": 0
            }
        
        entrenadores_data[queja.Entrenador_ID]["total_quejas"] += 1
        entrenadores_data[queja.Entrenador_ID]["suma_calificaciones"] += queja.Calificacion
    
    # Calcular promedio para cada entrenador
    top_entrenadores = []
    for entrenador_id, data in entrenadores_data.items():
        if data["total_quejas"] > 0:
            promedio = round(data["suma_calificaciones"] / data["total_quejas"], 2)
            
            # Obtener información del entrenador
            entrenador = db.query(models.users.User).filter(models.users.User.ID == entrenador_id).first()
            entrenador_persona = db.query(models.persons.Person).filter(
                models.persons.Person.Usuario_ID == entrenador_id
            ).first()
            
            nombre_entrenador = entrenador.Nombre_Usuario if entrenador else "Desconocido"
            if entrenador_persona:
                nombre_entrenador = f"{entrenador_persona.Nombre} {entrenador_persona.Primer_Apellido}"
                if entrenador_persona.Segundo_Apellido:
                    nombre_entrenador += f" {entrenador_persona.Segundo_Apellido}"
            
            top_entrenadores.append({
                "entrenador_id": entrenador_id,
                "nombre": nombre_entrenador,
                "promedio_calificacion": promedio,
                "total_quejas": data["total_quejas"]
            })
    
    # Ordenar por promedio de calificación (descendente)
    top_entrenadores.sort(key=lambda x: x["promedio_calificacion"], reverse=True)
    
    # Tomar los 5 mejores
    top_entrenadores = top_entrenadores[:5]
    
    # Calcular tendencia de calificaciones por mes (últimos 6 meses)
    tendencia_calificaciones = []
    
    if quejas:
        # Obtener la fecha más reciente
        fecha_mas_reciente = max(queja.Fecha_Registro for queja in quejas)
        
        # Generar los últimos 6 meses desde la fecha más reciente
        meses = []
        for i in range(6):
            mes = fecha_mas_reciente.month - i
            anio = fecha_mas_reciente.year
            if mes <= 0:
                mes += 12
                anio -= 1
            meses.append((anio, mes))
        
        # Invertir para que esté en orden cronológico
        meses.reverse()
        
        # Calcular promedio por mes
        for anio, mes in meses:
            quejas_mes = [
                queja for queja in quejas 
                if queja.Fecha_Registro.year == anio and queja.Fecha_Registro.month == mes
            ]
            
            if quejas_mes:
                promedio_mes = round(sum(queja.Calificacion for queja in quejas_mes) / len(quejas_mes), 2)
            else:
                promedio_mes = 0
            
            tendencia_calificaciones.append({
                "anio": anio,
                "mes": mes,
                "periodo": f"{anio}-{mes:02d}",
                "promedio_calificacion": promedio_mes,
                "total_quejas": len(quejas_mes)
            })
    
    # Preparar estadísticas por entrenador
    estadisticas_por_entrenador = []
    for entrenador_id, data in entrenadores_data.items():
        if data["total_quejas"] > 0:
            # Obtener información del entrenador
            entrenador = db.query(models.users.User).filter(models.users.User.ID == entrenador_id).first()
            
            if not entrenador:
                continue
                
            entrenador_persona = db.query(models.persons.Person).filter(
                models.persons.Person.Usuario_ID == entrenador_id
            ).first()
            
            # Calcular nombre del entrenador
            nombre_entrenador = entrenador.Nombre_Usuario
            if entrenador_persona:
                nombre_entrenador = f"{entrenador_persona.Nombre} {entrenador_persona.Primer_Apellido}"
                if entrenador_persona.Segundo_Apellido:
                    nombre_entrenador += f" {entrenador_persona.Segundo_Apellido}"
            
            # Obtener todas las quejas del entrenador
            quejas_entrenador = [q for q in quejas if q.Entrenador_ID == entrenador_id]
            
            # Calcular distribución de calificaciones para este entrenador
            dist_entrenador = {
                "5_estrellas": 0,
                "4_estrellas": 0,
                "3_estrellas": 0,
                "2_estrellas": 0,
                "1_estrella": 0
            }
            
            for queja in quejas_entrenador:
                if queja.Calificacion == 5:
                    dist_entrenador["5_estrellas"] += 1
                elif queja.Calificacion == 4:
                    dist_entrenador["4_estrellas"] += 1
                elif queja.Calificacion == 3:
                    dist_entrenador["3_estrellas"] += 1
                elif queja.Calificacion == 2:
                    dist_entrenador["2_estrellas"] += 1
                elif queja.Calificacion == 1:
                    dist_entrenador["1_estrella"] += 1
            
            # Calcular porcentajes
            for key in dist_entrenador:
                dist_entrenador[key] = round((dist_entrenador[key] / len(quejas_entrenador)) * 100, 2) if quejas_entrenador else 0
            
            estadisticas_por_entrenador.append({
                "entrenador_id": entrenador_id,
                "nombre": nombre_entrenador,
                "promedio_calificacion": round(data["suma_calificaciones"] / data["total_quejas"], 2),
                "total_quejas": data["total_quejas"],
                "distribucion_calificaciones": dist_entrenador
            })
    
    # Ordenar por promedio de calificación (descendente)
    estadisticas_por_entrenador.sort(key=lambda x: x["promedio_calificacion"], reverse=True)
    
    # Preparar respuesta completa
    return {
        "total_quejas": total_quejas,
        "promedio_calificacion": promedio_calificacion,
        "distribucion_calificaciones": distribucion,
        "top_entrenadores": top_entrenadores,
        "tendencia_calificaciones": tendencia_calificaciones,
        "estadisticas_por_entrenador": estadisticas_por_entrenador
    }

# Ruta para obtener información detallada de un entrenador específico
@feedback_router.get('/admin/entrenador/{entrenador_id}/estadisticas/', tags=['Feedback Admin'], dependencies=[Depends(Portador())])
def get_estadisticas_entrenador(
    entrenador_id: int,
    db: Session = Depends(get_db),
    token_data = Depends(Portador())
):
    # Obtener el ID del usuario del token
    user_id = token_data.get("user_id") or token_data.get("ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar que el usuario tenga rol de administrador
    user = db.query(models.users.User).filter(models.users.User.ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    is_admin = False
    for rol in user.roles:
        if rol.Nombre == "admin":
            is_admin = True
            break
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden acceder a este recurso")
    
    # Verificar que el entrenador exista
    entrenador = db.query(models.users.User).filter(models.users.User.ID == entrenador_id).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    
    # Obtener información personal del entrenador
    entrenador_persona = db.query(models.persons.Person).filter(
        models.persons.Person.Usuario_ID == entrenador_id
    ).first()
    
    # Construir nombre completo del entrenador
    nombre_entrenador = entrenador.Nombre_Usuario
    if entrenador_persona:
        nombre_entrenador = f"{entrenador_persona.Nombre} {entrenador_persona.Primer_Apellido}"
        if entrenador_persona.Segundo_Apellido:
            nombre_entrenador += f" {entrenador_persona.Segundo_Apellido}"
    
    # Obtener todas las quejas del entrenador
    quejas = db.query(models.quejas.Queja).filter(models.quejas.Queja.Entrenador_ID == entrenador_id).all()
    
    # Preparar estadísticas
    total_quejas = len(quejas)
    
    if total_quejas == 0:
        return {
            "entrenador_id": entrenador_id,
            "nombre": nombre_entrenador,
            "total_quejas": 0,
            "promedio_calificacion": 0,
            "distribucion_calificaciones": {
                "5_estrellas": 0,
                "4_estrellas": 0,
                "3_estrellas": 0,
                "2_estrellas": 0,
                "1_estrella": 0
            },
            "tendencia_calificaciones": [],
            "ultimas_quejas": []
        }
    
    # Calcular promedio de calificaciones
    suma_calificaciones = sum(queja.Calificacion for queja in quejas)
    promedio_calificacion = round(suma_calificaciones / total_quejas, 2)
    
    # Calcular distribución de calificaciones
    distribucion = {
        "5_estrellas": 0,
        "4_estrellas": 0,
        "3_estrellas": 0,
        "2_estrellas": 0,
        "1_estrella": 0
    }
    
    for queja in quejas:
        if queja.Calificacion == 5:
            distribucion["5_estrellas"] += 1
        elif queja.Calificacion == 4:
            distribucion["4_estrellas"] += 1
        elif queja.Calificacion == 3:
            distribucion["3_estrellas"] += 1
        elif queja.Calificacion == 2:
            distribucion["2_estrellas"] += 1
        elif queja.Calificacion == 1:
            distribucion["1_estrella"] += 1
    
    # Calcular porcentajes
    for key in distribucion:
        distribucion[key] = round((distribucion[key] / total_quejas) * 100, 2)
    
    # Calcular tendencia de calificaciones por mes (últimos 6 meses)
    tendencia_calificaciones = []
    
    if quejas:
        # Obtener la fecha más reciente
        fecha_mas_reciente = max(queja.Fecha_Registro for queja in quejas)
        
        # Generar los últimos 6 meses desde la fecha más reciente
        meses = []
        for i in range(6):
            mes = fecha_mas_reciente.month - i
            anio = fecha_mas_reciente.year
            if mes <= 0:
                mes += 12
                anio -= 1
            meses.append((anio, mes))
        
        # Invertir para que esté en orden cronológico
        meses.reverse()
        
        # Calcular promedio por mes
        for anio, mes in meses:
            quejas_mes = [
                queja for queja in quejas 
                if queja.Fecha_Registro.year == anio and queja.Fecha_Registro.month == mes
            ]
            
            if quejas_mes:
                promedio_mes = round(sum(queja.Calificacion for queja in quejas_mes) / len(quejas_mes), 2)
            else:
                promedio_mes = 0
            
            tendencia_calificaciones.append({
                "anio": anio,
                "mes": mes,
                "periodo": f"{anio}-{mes:02d}",
                "promedio_calificacion": promedio_mes,
                "total_quejas": len(quejas_mes)
            })
    
    # Obtener las últimas 10 quejas con detalles
    ultimas_quejas = []
    
    # Ordenar quejas por fecha (más recientes primero)
    quejas_ordenadas = sorted(quejas, key=lambda q: q.Fecha_Registro, reverse=True)[:10]
    
    for queja in quejas_ordenadas:
        # Obtener información del usuario que hizo la queja
        usuario = db.query(models.users.User).filter(models.users.User.ID == queja.Usuario_ID).first()
        persona = db.query(models.persons.Person).filter(models.persons.Person.Usuario_ID == queja.Usuario_ID).first()
        
        # Obtener información de la clase
        clase = db.query(models.clases.Clase).filter(models.clases.Clase.ID == queja.Clase_ID).first()
        
        # Construir nombre del usuario
        nombre_usuario = usuario.Nombre_Usuario if usuario else "Desconocido"
        if persona:
            nombre_usuario = f"{persona.Nombre} {persona.Primer_Apellido}"
            if persona.Segundo_Apellido:
                nombre_usuario += f" {persona.Segundo_Apellido}"
        
        ultimas_quejas.append({
            "id": queja.ID,
            "calificacion": queja.Calificacion,
            "comentario": queja.Comentario,
            "fecha": queja.Fecha_Registro.isoformat(),
            "usuario_nombre": nombre_usuario,
            "clase_nombre": clase.Nombre if clase else "Desconocida"
        })
    
    # Preparar respuesta completa
    return {
        "entrenador_id": entrenador_id,
        "nombre": nombre_entrenador,
        "total_quejas": total_quejas,
        "promedio_calificacion": promedio_calificacion,
        "distribucion_calificaciones": distribucion,
        "tendencia_calificaciones": tendencia_calificaciones,
        "ultimas_quejas": ultimas_quejas
    }