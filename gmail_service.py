# email_service.py
import os
import smtplib
import random
import string
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cargar variables de entorno
load_dotenv()

# Configuración de correo
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

def generate_verification_code(length=6):
    """Genera un código de verificación aleatorio"""
    return ''.join(random.choices(string.digits, k=length))

async def send_verification_email(to_email: str, token: str):
    """Envía un correo de verificación con código"""
    try:
        # Generar código de verificación
        verification_code = generate_verification_code()
        
        # Crear mensaje
        message = MIMEMultipart()
        message['From'] = EMAIL_FROM
        message['To'] = to_email
        message['Subject'] = 'Código de Verificación - GYM BULLS'
        
        # Contenido HTML
        html_content = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
              <h2 style="color: #333; text-align: center;">Bienvenido a GYM BULLS</h2>
              <p>Gracias por registrarte. Tu código de verificación es:</p>
              <div style="text-align: center; margin: 30px 0;">
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; font-size: 24px; letter-spacing: 5px; font-weight: bold;">
                  {verification_code}
                </div>
              </div>
              <p>Introduce este código en la aplicación para verificar tu cuenta.</p>
              <p>El código expirará en 24 horas.</p>
              <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px;">
                &copy; 2025 GYM BULLS. Todos los derechos reservados.
              </div>
            </div>
          </body>
        </html>
        """
        
        # Adjuntar contenido HTML al mensaje
        message.attach(MIMEText(html_content, 'html'))
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Activar encriptación
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        
        # Enviar correo
        server.send_message(message)
        server.quit()
        
        print(f"Correo enviado exitosamente a {to_email} con código {verification_code}")
        return {'success': True, 'verification_code': verification_code}
    
    except Exception as e:
        print(f'Error al enviar email: {e}')
        return {'success': False, 'error': str(e)}