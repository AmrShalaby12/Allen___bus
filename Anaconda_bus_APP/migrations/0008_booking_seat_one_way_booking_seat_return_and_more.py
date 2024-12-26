# Generated by Django 5.0.7 on 2024-12-23 14:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Anaconda_bus_APP", "0007_bus_driver_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="seat_one_way",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="one_way_bookings",
                to="Anaconda_bus_APP.seat",
                verbose_name="مقعد الذهاب",
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="seat_return",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="return_bookings",
                to="Anaconda_bus_APP.seat",
                verbose_name="مقعد العودة",
            ),
        ),
        migrations.AlterField(
            model_name="trip",
            name="start_time",
            field=models.TimeField(default="00:00:00", verbose_name="وقت الوصول "),
        ),
    ]
