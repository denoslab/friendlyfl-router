# Generated by Django 4.2.3 on 2023-07-09 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendlyfl', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
