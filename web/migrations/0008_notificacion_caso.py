# Generated by Django 3.0.5 on 2020-05-22 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20200521_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='caso',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
