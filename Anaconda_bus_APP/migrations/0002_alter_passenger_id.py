# Generated by Django 5.0.7 on 2024-12-22 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Anaconda_bus_APP", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passenger",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
