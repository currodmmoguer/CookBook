# CookBook

Proyecto para el Ciclo Formativo de Grado Superior de Desarrolo de Aplicaciones Multiplataformas.

Consiste en una red social cuyo fin es compartir recetas culinarias.

### Pre-requisitos 📋
Tener instalado python3 y pip en la máquina.

También las instrucciones de instalación están dirigidas para una máquina _Linux._

## Instalación

**1 Instalar requerimientos:**

pip install -r requeriments.txt

**2 Crear base de datos (SQlite3):**

python manage.py makemigrations web

python manage.py migrate web

La base de datos se llama db.sqlite3, se puede cambiar en el archivo settings.py en el apartado "DATABASES".

## Construido con 🛠️
* [Django](https://www.djangoproject.com/) - Framework web usado
* HTML y CSS3 - Maquetado de plantillas
* Javascript - Funcionalidades en plantillas y uso de AJAX
* [Bootstrap 4](https://getbootstrap.com/) - Framework para diseñar web responsiva
* [JQuery](https://jquery.com/) - Librería de Javascript para la manipulación de elementos del DOM
* [Chart JS](https://www.chartjs.org/) - Librería de Javascript para creación de gráficos
* [Cropper JS](https://fengyuanchen.github.io/cropperjs/) - Librería de Javascript para editar imágenes
* SQLite3 - Base de datos
