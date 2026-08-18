import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import gspread
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Tener el archivo en el mismo directorio que este script o proporcionar la ruta completa al archivo de credenciales en la variable de entorno GOOGLE_CREDENTIALS
CREDENTIALS_FILE = "credentials.json"  # Cambiar a la ruta de tu archivo de credenciales

# Definir los nombres de las hojas de cálculo a utilizar inicialmente, luego se pueden cambiar con los comandos del bot 
SHEET_ENCUESTA_INICIAL = os.getenv('ENCUENSTA_INICIAL_SHEET_NAME')
SHEET_PLANILLA = os.getenv('PLANILLA_PRINCIPAL_SHEET_NAME')

# ID del servidor de Discord en el cual se tendra el privilegio para cambiar el rol y las planillas.
SERVER_ID = os.getenv('DISCORD_SERVER_ID')

# Conexión a Google Sheets
try:
   if "GOOGLE_CREDENTIALS" in os.environ:
      # Si la variable de entorno GOOGLE_CREDENTIALS está definida, usarla para la autenticación
      credentials_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
      gc = gspread.service_account_from_dict(credentials_dict)
   else:
      # Si no, usar el archivo de credenciales local
      gc = gspread.service_account(filename=CREDENTIALS_FILE)
   sheet_encuesta_inicial = gc.open(SHEET_ENCUESTA_INICIAL).sheet1
   sheet_planilla = gc.open(SHEET_PLANILLA).sheet1
   print("Conexión exitosa a Google Sheets.")
except Exception as e:
   print(f"Error al conectar con Google Sheets: {e}")

# Definir el rol actual que se asignará a los usuarios que cumplan con los criterios, se puede cambiar con el comando !cambiar_rol_a_dar. Importante que el rol exista en el servidor de Discord, sino el bot no va a poder asignarlo.
current_role = "2c2026"

# Configuración del bot de Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Funciones auxiliares
def convertir_a_minusculas_y_dividir_por_comas(nombre):
   """Convierte un nombre a minúsculas, elimina espacios al inicio y al final, y quita la coma si es necesario."""
   nombre_limpio = nombre.lower().strip()   
   if "," in nombre_limpio:
      partes = nombre_limpio.split(",")
      return partes[0].split() + partes[1].split()
   
   return nombre_limpio.split()

def lista_contiene_al_menos_2_elementos_de_la_otra(primer_lista, segunda_lista):
   return sum(1 for elem in segunda_lista if elem in primer_lista) >= 2

# Eventos y comandos del bot

# Evento que se ejecuta cuando el bot está listo
@bot.event
async def on_ready():
   print(f'Bot initialized as {bot.user.name} ({bot.user.id})')

# Funcion para recibir rol basado en el padrón y el nombre del usuario
@bot.command()
async def recibir_rol(ctx, padron: str):
   global sheet_encuesta_inicial
   padrones = sheet_encuesta_inicial.col_values(4)  # Suponiendo que el padrón está en la columna D (índice 4)
   if padron not in padrones:
      await ctx.send(f"{ctx.author.mention} Padron {padron} no está registrado en la encuesta inicial. Contesta la encuesta inicial para poder recibir el rol.")
      return
   global current_role
   role = discord.utils.get(ctx.guild.roles, name=current_role)
   if role:
      global sheet_planilla
      data = sheet_planilla.get_all_values()
      success = False
      for i, row in enumerate(data):
         if len(row) > 2 and row[1] == padron and lista_contiene_al_menos_2_elementos_de_la_otra(convertir_a_minusculas_y_dividir_por_comas(row[2]), convertir_a_minusculas_y_dividir_por_comas(ctx.author.display_name)):
            success = True
            sheet_planilla.update_cell(i + 1, 7, True) # Sumo 1 porque los indices de gspread arrancan en 1 y la columna 7 es la columna G (Esta en Discord)
            break
      if not success:
         await ctx.send(f"No se encontró el usuario {ctx.author.display_name} con padrón {padron} en la planilla.")
         return
      await ctx.author.add_roles(role)
      await ctx.send(f"{ctx.author.mention} Se te ha asignado el rol: {current_role}")
   else:
      await ctx.send(f"El rol {current_role} no existe en este servidor.")

# Comandos para cambiar el rol y las planillas, solo accesibles para usuarios con el rol "Docentes", servirian para cambiar el rol y las planillas si se quiere usar el bot en otro curso o año, sin necesidad de reiniciar el bot.

# Cambio de rol
@bot.command()
@commands.has_role("Docentes")
async def cambiar_rol_a_dar(ctx, new_role: str):
   if ctx.guild.id != int(SERVER_ID):
      await ctx.send("Este comando solo puede ser usado en el servidor autorizado.")
      return
   global current_role
   current_role = new_role
   await ctx.send(f"El rol actual ha sido cambiado a: {current_role}")

@cambiar_rol_a_dar.error
async def cambiar_rol_error(ctx, error):
   if isinstance(error, commands.MissingRole):
      await ctx.send("No tienes permiso para cambiar el rol.")
   else:
      await ctx.send("Ocurrió un error al intentar cambiar el rol.")



# Cambios de planillas, es importante que las planillas tengan la misma estructura que las planillas originales, sino el bot no va a funcionar correctamente. Tambien es importante darle acceso a la cuenta de servicio de Google Sheets a las nuevas planillas, sino el bot no va a poder acceder a ellas. La misma es: bot-discord-sheets@bot-discord-is.iam.gserviceaccount.com
@bot.command()
@commands.has_role("Docentes")
async def cambiar_planilla_encuesta(ctx, *, new_sheet_name: str):
   if ctx.guild.id != int(SERVER_ID):
      await ctx.send("Este comando solo puede ser usado en el servidor autorizado.")
      return
   global sheet_encuesta_inicial
   try:
      sheet_encuesta_inicial = gc.open(new_sheet_name).sheet1
      await ctx.send(f"Se ha cambiado la planilla de encuesta inicial a: {new_sheet_name}")
   except Exception as e:
      await ctx.send(f"No se pudo cambiar la planilla de encuesta inicial a: {new_sheet_name}. Error: {e}")

@cambiar_planilla_encuesta.error
async def cambiar_planilla_encuesta_error(ctx, error):
   if isinstance(error, commands.MissingRole):
      await ctx.send("No tienes permiso para cambiar la planilla de encuesta inicial.")
   else:
      await ctx.send("Ocurrió un error al intentar cambiar la planilla de encuesta inicial.")

@bot.command()
@commands.has_role("Docentes")
async def cambiar_planilla_principal(ctx, *, new_sheet_name: str):
   if ctx.guild.id != int(SERVER_ID):
      await ctx.send("Este comando solo puede ser usado en el servidor autorizado.")
      return
   global sheet_planilla
   try:
      sheet_planilla = gc.open(new_sheet_name).sheet1
      await ctx.send(f"Se ha cambiado la planilla principal a: {new_sheet_name}")
   except Exception as e:
      await ctx.send(f"No se pudo cambiar la planilla principal a: {new_sheet_name}. Error: {e}")

@cambiar_planilla_principal.error
async def cambiar_planilla_principal_error(ctx, error):
   if isinstance(error, commands.MissingRole):
      await ctx.send("No tienes permiso para cambiar la planilla principal.")
   else:
      await ctx.send("Ocurrió un error al intentar cambiar la planilla principal.")

# Iniciar el bot
bot.run(TOKEN)