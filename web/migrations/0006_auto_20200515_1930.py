# Generated by Django 3.0.5 on 2020-05-15 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20200513_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingrediente_receta',
            name='cantidad',
            field=models.FloatField(max_length=30),
        ),
    ]