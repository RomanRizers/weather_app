# Generated by Django 5.0.7 on 2024-07-20 00:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='city',
            old_name='lat',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='city',
            old_name='lng',
            new_name='longitude',
        ),
    ]