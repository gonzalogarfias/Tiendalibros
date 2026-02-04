# Tienda Libros
Proyecto de una tienda de libros en línea desarrollada por Equipo2PWA.

## Descripción
Una aplicación web para la gestión de una tienda de libros, que incluye funcionalidades de visualización de productos, proceso de pago y administración de inventario.

## Características
- Visualización de catálogo de libros con imágenes y descripciones
- Detalle de cada libro con información de stock
- Proceso de pago simulado
- Registro y acceso de usuarios
- Administración de libros (subida, edición y eliminación)
- Interfaz responsive para dispositivos móviles y de escritorio

## Instalación
1. Clona el repositorio en tu máquina local: `git clone https://github.com/Equipo2PWA/Tiendalibros.git`
2. Navega al directorio del proyecto: `cd Tiendalibros`
3. Instala las dependencias necesarias (ajusta el comando según tu entorno, por ejemplo para Python/Django: `pip install -r requirements.txt`)

## Uso 
1. una ves clonado el repositorio ingresa a los settings para poder configurar el archivo a tus bases de datos, el codigo tiene una funcion de envio de correos para lo cual es necesario crear una clave de aplicacion desde tu gmail importante tenter la verificacion de dos pasos activada

2. en la consola de comandos de el proyecto hacer los comandos `python manage.py makemigrations` y a continuacion `python manage.py migrate` para poder generar las migraciones a la base de datos y asi evitar algun error al ejecutar.

3. Inicia el servidor de desarrollo (ejemplo para Django: `python manage.py runserver`)

4. Abre tu navegador y accede a la dirección: `http://localhost:8000`

## Equipo
- Equipo2PWA
