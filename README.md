# Bot administrativo de discord para Ingenieria de Software I - Catedra Leveroni

Bot para realizar funciones administrativas del servidor de Discord para  Ingenieria de Software I - Catedra Leveroni. El mismo se encarga de recibir un padron y verificar que el alumne haya respondido la encuesta inicial y que tenga bien su nombre en el servidor.

## Comandos administrativos

```
!recibir_rol {numero_padron}
```

Asigna el rol del cuatrimestre actual al alumno, verificando que haya respondido la encuesta. Marca que el mismo esta en discord

## Comandos de mantenimiento

```
!cambiar_rol_a_dar {nuevo_rol}
```

Modifica el rol a asignar a los alumnes


```
!cambiar_planilla_encuesta {nueva_planilla}
```

Modifica la planilla de encuestas respondidas

```
!cambiar_planilla_principal {nueva_planilla}
```

Modifica la planilla administrativa

## Ejecucion Local

1. Instalar las dependencias mediante ```pip install -r installs.txt``` (recomendado usar un ambiente virtual de python)

2. Tener como variable de entorno el token secreto del bot y la ruta del archivo para las credenciales de la cuenta de Google Services del bot

3. Ejecutar el script de Python con ```python3 main.py```


## Cosas a tener en cuenta

* El bot utiliza una cuenta de Google Services para acceder y modificar las planillas, para eso necesita acceso de editor. La cuenta es: bot-discord-sheets@bot-discord-is.iam.gserviceaccount.com