# Generated by Django 3.0.5 on 2020-09-29 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_auto_20200918_0335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='caso',
            field=models.IntegerField(blank=True, max_length=255, null=True),
        ),
    ]