# Generated by Django 5.0.7 on 2024-12-22 08:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="اسم الطالب")),
                (
                    "user_id",
                    models.CharField(max_length=100, verbose_name="كود الطالب"),
                ),
                ("category", models.CharField(max_length=255, verbose_name="الجامعة")),
                (
                    "subscription_start_date",
                    models.DateField(verbose_name="تاريخ بداية الاشتراك"),
                ),
                (
                    "subscription_end_date",
                    models.DateField(verbose_name="تاريخ نهاية الاشتراك"),
                ),
                (
                    "attendance_date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="موافق يوم"
                    ),
                ),
                (
                    "attendance_status",
                    models.CharField(
                        choices=[
                            ("حضور", "حضور"),
                            ("انصراف", "انصراف"),
                            ("غياب", "غياب"),
                        ],
                        default="غياب",
                        max_length=10,
                        verbose_name="حالة الحضور",
                    ),
                ),
                (
                    "departure_status",
                    models.CharField(
                        choices=[
                            ("حضور", "حضور"),
                            ("انصراف", "انصراف"),
                            ("غياب", "غياب"),
                        ],
                        default="غياب",
                        max_length=10,
                        verbose_name="حالة الانصراف",
                    ),
                ),
                (
                    "ride_deducted",
                    models.BooleanField(default=False, verbose_name="تم خصم الرحلة"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64, verbose_name="اسم الجامعه")),
            ],
        ),
        migrations.CreateModel(
            name="destination",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="اسم الوجهه")),
            ],
        ),
        migrations.CreateModel(
            name="PaymentAccount",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "payment_option",
                    models.CharField(
                        choices=[
                            ("vf-cash", "VF Cash"),
                            ("instapay", "InstaPay"),
                            ("fawry", "Fawry"),
                        ],
                        max_length=20,
                    ),
                ),
                ("account_name", models.CharField(max_length=100)),
                ("account_number", models.CharField(max_length=50)),
                ("additional_info", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Route",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("from_location", models.CharField(max_length=100)),
                ("to_location", models.CharField(max_length=100)),
                ("date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Bus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="اسم الباص")),
                ("capacity", models.PositiveIntegerField(verbose_name="السعة الكلية")),
                (
                    "plate_number",
                    models.CharField(max_length=50, verbose_name="رقم النمر"),
                ),
                (
                    "bus_type",
                    models.CharField(max_length=100, verbose_name="نوع الباص"),
                ),
                ("location_url", models.URLField(blank=True, null=True)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=False, verbose_name="نشط")),
                (
                    "seats_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="bus_seats/",
                        verbose_name="صورة الكراسي",
                    ),
                ),
                (
                    "Bus_driver",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buses",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="سائق الباص",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        default="-----",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buses",
                        to="Anaconda_bus_APP.category",
                        verbose_name="الجامعة",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="passenger",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="كود الطالب"
                    ),
                ),
                (
                    "university_code",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="الكود الجامعي",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="رقم الهاتف"
                    ),
                ),
                ("name", models.CharField(max_length=64, verbose_name="اسم الطالب")),
                (
                    "subscription_duration",
                    models.IntegerField(
                        choices=[
                            (12, "12 رحلة"),
                            (16, "16 رحلة"),
                            (22, "22 رحلة"),
                            (48, "ترم دراسي - 48 رحلة"),
                            (96, "سنة دراسية - 96 رحلة"),
                        ],
                        verbose_name="مدة الاشتراك",
                    ),
                ),
                (
                    "subscription_start_date",
                    models.DateField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="تاريخ بداية الاشتراك",
                    ),
                ),
                (
                    "subscription_end_date",
                    models.DateField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="تاريخ نهاية الاشتراك",
                    ),
                ),
                ("qr_code", models.BinaryField(blank=True, null=True)),
                (
                    "rides_used",
                    models.IntegerField(
                        default=0, verbose_name="عدد الرحلات المستخدمة"
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Anaconda_bus_APP.category",
                        verbose_name="الجامعه",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="passenger",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="المستخدم",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="active",
                        max_length=20,
                        verbose_name="حاله الدفع",
                    ),
                ),
                (
                    "attendance_status",
                    models.CharField(
                        choices=[("present", "Present"), ("absent", "Absent")],
                        default="absent",
                        max_length=10,
                        verbose_name="حاله الحضور",
                    ),
                ),
                (
                    "booking_date",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="تاريخ الحجز"
                    ),
                ),
                ("transfer_message", models.TextField(blank=True, null=True)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[("cash", "Cash"), ("online", "Online")], max_length=50
                    ),
                ),
                (
                    "transaction_number",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "mobile_number",
                    models.CharField(
                        blank=True,
                        max_length=15,
                        null=True,
                        verbose_name="الرقم المحول منه",
                    ),
                ),
                (
                    "transaction_image",
                    models.ImageField(blank=True, null=True, upload_to="transactions/"),
                ),
                (
                    "trip_type",
                    models.CharField(
                        choices=[
                            ("one_way", "ذهاب فقط"),
                            ("return", "عودة فقط"),
                            ("round_trip", "ذهاب وعودة"),
                        ],
                        default="round_trip",
                        max_length=20,
                        verbose_name="Trip Type",
                    ),
                ),
                (
                    "serial_code",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        unique=True,
                        verbose_name="كود الرحلة",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_bookings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="المستخدم",
                    ),
                ),
                (
                    "passenger",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="Anaconda_bus_APP.passenger",
                        verbose_name="الراكب",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "payment_type",
                    models.CharField(
                        blank=True,
                        choices=[("cash", "نقداً"), ("online", "أونلاين")],
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "payment",
                    models.CharField(
                        choices=[
                            ("pending", "قيد المراجعة"),
                            ("completed", "مكتمل"),
                            ("failed", "فشل"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "booking",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment",
                        to="Anaconda_bus_APP.booking",
                        verbose_name="الحجز",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Seat",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("seat_number", models.IntegerField()),
                ("is_reserved", models.BooleanField(default=False)),
                ("trip_date", models.DateField(null=True)),
                (
                    "bus",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seats",
                        to="Anaconda_bus_APP.bus",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="booking",
            name="seats_reserved",
            field=models.ManyToManyField(
                related_name="bookings",
                to="Anaconda_bus_APP.seat",
                verbose_name="الكراسي المحجوزه",
            ),
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("route", models.TextField(default="", verbose_name="الطريق")),
                ("trip_name", models.TextField(default="", verbose_name="اسم الرحله")),
                (
                    "date",
                    models.DateField(blank=True, null=True, verbose_name="التاريخ"),
                ),
                (
                    "start_time",
                    models.TimeField(default="00:00:00", verbose_name="وقت البدايه"),
                ),
                (
                    "trip_type",
                    models.CharField(
                        choices=[
                            ("one_way", "ذهاب"),
                            ("return", "عودة"),
                            ("round_trip", "ذهاب وعودة"),
                        ],
                        default="round_trip",
                        max_length=20,
                        verbose_name="نوع الرحلة",
                    ),
                ),
                (
                    "one_way_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=1,
                        max_digits=6,
                        verbose_name="سعر الذهاب فقط",
                    ),
                ),
                (
                    "return_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=1,
                        max_digits=6,
                        verbose_name="سعر العودة فقط",
                    ),
                ),
                (
                    "round_trip_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=1,
                        max_digits=6,
                        verbose_name="سعر الذهاب و العودة",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("next_trip_date", models.DateTimeField(blank=True, null=True)),
                ("is_old", models.BooleanField(default=False)),
                (
                    "bus",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Anaconda_bus_APP.bus",
                    ),
                ),
                (
                    "end_destination",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="end_schedules",
                        to="Anaconda_bus_APP.destination",
                        verbose_name="النهايه",
                    ),
                ),
                (
                    "start_destination",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="start_schedules",
                        to="Anaconda_bus_APP.destination",
                        verbose_name="البدايه",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="booking",
            name="Trip",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bookings",
                to="Anaconda_bus_APP.trip",
                verbose_name="الرحله",
            ),
        ),
    ]
