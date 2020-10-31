# CookBook

Instalación

1 Instalar requerimientos:

pip install -r requeriments.txt

2 Crear base de datos (SQlite3):

python manage.py makemigrations web

python manage.py migrate web

La base de datos se llama db.sqlite3, se puede cambiar en el archivo settings.py en el apartado "DATABASES".
