from fastapi import FastAPI
from routes.google_auth import router as google_auth_router
from routes.person import person
from routes.rol import rol
from routes.user import user
from routes.usersrols import userrol
from routes.evaluacion_serv import evaluaciones_serv_router
from routes.promociones import promocion_router
from routes.opinion_cliente import opinion_cliente_router
from routes.membresias import membresia
from routes.servicios_clientes import servicio_cliente
from routes.ejercicios import ejercicio
from routes.entrenamientos import entrenamiento
from routes.clases import clase_router
from fastapi.middleware.cors import CORSMiddleware
from routes.reservaciones import reservacion_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Tu URL de desarrollo
        "https://localhost:5173",
        "http://localhost:3000",  # Otros puertos comunes
        "https://gym-customer.onrender.com"  # Añade tu dominio de producción
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

# TABLAS CON RELACIÓN 
app.include_router(user)
app.include_router(person)
app.include_router(rol)
app.include_router(userrol)
app.include_router(evaluaciones_serv_router)
app.include_router(promocion_router)
app.include_router(opinion_cliente_router)
app.include_router(membresia)
app.include_router(servicio_cliente)
app.include_router(ejercicio)
app.include_router(entrenamiento)
app.include_router(clase_router)
app.include_router(reservacion_router)
app.include_router(google_auth_router)
