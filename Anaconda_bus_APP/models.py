from django.db import models
from django.contrib.auth.models import User
import qrcode 
from django.core.files import File
from io import BytesIO
from datetime import timedelta, date
from datetime import date, timedelta
from io import BytesIO
import qrcode
from django.db import models
from datetime import date, timedelta
from io import BytesIO
import qrcode

class passenger(models.Model):
    DURATION_CHOICES = [
        (12, '12 رحلة'),
        (16, '16 رحلة'),
        (22, '22 رحلة'),
        (48, 'ترم دراسي - 48 رحلة'),
        (96, 'سنة دراسية - 96 رحلة'),
    ]
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='passenger', 
        verbose_name="المستخدم",
        null=True,  
        blank=True 
    )
    university_code = models.CharField(max_length=20, verbose_name="الكود الجامعي", null=True, blank=True , unique=True)
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف", null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="الجامعه")
    name = models.CharField(max_length=64, verbose_name="اسم الطالب")
    subscription_duration = models.IntegerField(choices=DURATION_CHOICES, verbose_name="مدة الاشتراك")
    subscription_start_date = models.DateField(verbose_name="تاريخ بداية الاشتراك", null=True, blank=True, editable=False)
    subscription_end_date = models.DateField(verbose_name="تاريخ نهاية الاشتراك", null=True, blank=True, editable=False)
    qr_code = models.BinaryField(null=True, blank=True)
    rides_used = models.IntegerField(default=0, verbose_name="عدد الرحلات المستخدمة")

    @property
    def total_rides(self):
        """إجمالي عدد الرحلات"""
        return self.subscription_duration

    @property
    def remaining_rides(self):
        """عدد الرحلات المتبقية"""
        remaining = self.total_rides - self.rides_used
        return max(remaining, 0)  # التأكد أن النتيجة لا تقل عن صفر

    def save(self, *args, **kwargs):
        if not self.subscription_start_date:
            self.subscription_start_date = date.today()

        # حساب تاريخ النهاية بناءً على المدة
        self.subscription_end_date = self.subscription_start_date + timedelta(days=30 * self.subscription_duration)

        # معالجة كود الـ QR
        qr_data = (
            f"Product ID: {self.id}, "
            f"Name: {self.name}, "
            f"University Code: {self.university_code}, "
            f"Category: {self.category.name}, "
            f"Start Date: {self.subscription_start_date}, "
            f"End Date: {self.subscription_end_date}"
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.qr_code = buffer.getvalue()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.id).zfill(4)} - {self.name}"
     

# --------------------
# models.py
from django.db import models
class Route(models.Model):
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.from_location} to {self.to_location} on {self.date}"
class Category(models.Model):
    name = models.CharField(max_length=64 ,verbose_name="اسم الجامعه")

    def __str__(self):
        return f"{self.name}"
from django.contrib.auth.models import User  
# استيراد نموذج المستخدم
from django.db import models
from django.contrib.auth.models import User

class Bus(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الباص")
    capacity = models.PositiveIntegerField(verbose_name="السعة الكلية")
    plate_number = models.CharField(max_length=50, verbose_name="رقم النمر")
    driver_number = models.CharField(max_length=50, verbose_name="رقم السائق",blank=True, null=True)
    bus_type = models.CharField(max_length=100, verbose_name="نوع الباص")
    location_url = models.URLField(blank=True, null=True)  # رابط الموقع
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="نشط")
    
    category = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE, 
        related_name='buses', 
        verbose_name="الجامعة",
        default='-----',
    )
    Bus_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buses',
        verbose_name="سائق الباص",
        null=True,  
        blank=True
    )
    seats_image = models.ImageField(
        upload_to='bus_seats/',  # تحديد مكان حفظ الصور
        blank=True,
        null=True,
        verbose_name="صورة الكراسي"
    )

    def available_seats(self):
        total_available_seats = self.seats.filter(is_reserved=False).count()
        return min(total_available_seats, self.capacity)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

from django.dispatch import receiver
from django.db.models.signals import post_save

from django.db import models
import datetime

# class Seat(models.Model):
#     bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
#     seat_number = models.IntegerField()
#     is_reserved = models.BooleanField(default=False)
#     trip_date = models.DateField(default=datetime.date.today, verbose_name="تاريخ الرحلة")  # تاريخ الرحلة

#     class Meta:
#         unique_together = ('bus', 'seat_number', 'trip_date')  # إضافة قيد فريد على الحقول

class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.IntegerField()
    is_reserved = models.BooleanField(default=False)
    trip_date = models.DateField(null=True)

    def __str__(self):
        return f"Seat {self.seat_number} on {self.bus.name}"

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bus, Seat
from dateutil.relativedelta import relativedelta  # لإضافة أشهر

@receiver(post_save, sender=Bus)
def create_seats(sender, instance, created, **kwargs):
    if created and instance.seats.count() == 0: 
        for seat_number in range(1, instance.capacity + 1):
            Seat.objects.create(bus=instance, seat_number=seat_number)

class destination(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الوجهه")

    def __str__(self):
        return self.name

class Trip(models.Model):
    TRIP_TYPE_CHOICES = [
        ('one_way', 'ذهاب'),
        ('return', 'عودة'),
        ('round_trip', 'ذهاب وعودة'),
    ]

    DRIVER_STATUS_CHOICES = [
        ('not_arrived', 'لم يصل بعد'),
        ('arrived', 'وصل'),
    ]
    
    route = models.TextField(
        verbose_name="الطريق", 
        default="", 
        help_text="أدخل كل خط في سطر جديد."
    )    
    trip_name = models.TextField(verbose_name="اسم الرحله", default="")  # إضافة حقل الطريق
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE , default=1)
    date = models.DateField(verbose_name="التاريخ",null=True, blank=True)
    start_time = models.TimeField(verbose_name="وقت الوصول ", default='00:00:00')
    trip_type = models.CharField(
        max_length=20,
        choices=TRIP_TYPE_CHOICES,
        default='round_trip',
        verbose_name="نوع الرحلة"
    )
    # driver_status = models.CharField(
    #     max_length=20,
    #     choices=DRIVER_STATUS_CHOICES,
    #     default='not_arrived',
    #     verbose_name="حالة السائق"
    # )
    start_destination = models.ForeignKey(
        destination,
        on_delete=models.CASCADE,
        related_name='start_schedules',
        verbose_name="البدايه",
    null=True,  
    blank=True    )
    end_destination = models.ForeignKey(
        destination,
        on_delete=models.CASCADE,
        related_name='end_schedules',
        verbose_name="النهايه",
    null=True, 
    blank=True    )
    one_way_price = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="سعر الذهاب فقط", default=1
    )
    return_price = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="سعر العودة فقط", default=1
    )
    round_trip_price = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="سعر الذهاب و العودة", default=1
    )
    is_active = models.BooleanField(default=True)  # لتحديد إذا كانت الرحلة نشطة
    next_trip_date = models.DateTimeField(null=True, blank=True)  # تاريخ الرحلة التالية
    is_old = models.BooleanField(default=False) 
    def __str__(self):
        # عرض اسم الرحلة (trip_name) إذا كان موجودًا، وإلا يتم عرض تفاصيل أخرى
        return f"{self.trip_name}" if self.trip_name else f"Trip from {self.start_destination} to {self.end_destination}"

from django.contrib.auth.models import User

from django.contrib.auth.models import User

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid 
class Booking(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('online', 'Online'),
        ('subscription' , 'subscription')
    ]  
    TRIP_TYPE_CHOICES = [
        ('one_way', 'ذهاب فقط'),
        ('return', 'عودة فقط'),
        ('round_trip', 'ذهاب وعودة'),
    ]
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
        ("prepaid", 'مدفوع مسبقًا'),  # إضافة الخيار الجديد

    ]
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    
    passenger = models.ForeignKey(
        passenger,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="الراكب",
        default=1,

    )
        
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name= 'حاله الدفع'
    )
    attendance_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_CHOICES,
        default='absent',
        verbose_name='حاله الحضور',
    )

    booking_date = models.DateTimeField(auto_now_add=True, null=True,verbose_name="تاريخ الحجز")
    Trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='bookings', default='',verbose_name="الرحله")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookings', default=1,verbose_name="المستخدم")
    selected_route = models.CharField(max_length=255, null=True, blank=True)
    seats_reserved = models.ManyToManyField(Seat, related_name='bookings',verbose_name="الكراسي المحجوزه")
    transfer_message = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_number = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True,    verbose_name="الرقم المحول منه")
    transaction_image = models.ImageField(upload_to='transactions/', blank=True, null=True)
    trip_type = models.CharField(
        max_length=20,
        choices=TRIP_TYPE_CHOICES,
        default='round_trip',
        verbose_name=_("Trip Type"),
    )

    serial_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="كود الرحلة"
    )

    def reserved_seats_list(self):
        return ", ".join([f"Seat {seat.seat_number}" for seat in self.seats_reserved.all()])
    reserved_seats_list.short_description = "الكراسي المحجوزة"
    def reserved_seats_count(self):
        return self.seats_reserved.count()
    reserved_seats_count.short_description = "عدد الكراسي المحجوزة"

    def passenger_phone(self):
        """Retrieve the passenger's phone number."""
        if self.passenger and self.passenger.phone_number:
            return self.passenger.phone_number
        return "No Phone"
    passenger_phone.short_description = "Passenger Phone"

    def save(self, *args, **kwargs):
        # ضغط صورة التحويل
        if self.transaction_image:
            img = Image.open(self.transaction_image)
            output = BytesIO()
            img = img.convert('RGB')
            img.thumbnail((800, 800))
            img.save(output, format='JPEG', quality=70)
            output.seek(0)
            self.transaction_image = ContentFile(output.read(), self.transaction_image.name)

        # إنشاء الكود التسلسلي إذا لم يكن موجودًا
        if not self.serial_code:
            self.serial_code = f"TRIP-{uuid.uuid4().hex[:8].upper()}"

        # استدعاء دالة الحفظ الأساسية
        super().save(*args, **kwargs)

    def __str__(self):
        passenger_phone = self.passenger.phone_number if self.passenger and self.passenger.phone_number else "No Phone"
        return f"Booking {self.id} - {self.user.username} - {self.trip_type} - Phone: {passenger_phone}"


from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date

from django.db import models
from django.utils import timezone
from datetime import timedelta

class Attendance(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم الطالب')
    user_id = models.CharField(max_length=100, verbose_name='كود الطالب')
    category = models.CharField(max_length=255, verbose_name='الجامعة')
    subscription_start_date = models.DateField(verbose_name='تاريخ بداية الاشتراك')
    subscription_end_date = models.DateField(verbose_name='تاريخ نهاية الاشتراك')
    attendance_date = models.DateField(default=timezone.now, verbose_name='موافق يوم')
    ATTENDANCE_CHOICES = [
        ('حضور', 'حضور'),
        ('انصراف', 'انصراف'),
        ('غياب', 'غياب'),
    ]
#رحله الذاهب رحله العوده حضور
# جدول الاشتراكات
# cancle date >> boking
# date مينفعش تتكرر
    attendance_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_CHOICES,
        default='غياب',
        verbose_name='حالة الحضور',
    )
    departure_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_CHOICES,
        default='غياب',
        verbose_name='حالة الانصراف',
    )
    ride_deducted = models.BooleanField(default=False, verbose_name='تم خصم الرحلة')  # جديد

    def __str__(self):
        return f"{self.name} - {self.attendance_status} / {self.departure_status} - {self.attendance_date}"

    @classmethod
    def mark_attendance(cls, user_id, status, is_departure=False):
        """تسجيل الحضور أو الانصراف وخصم رحلة واحدة فقط في اليوم"""
        today = timezone.now().date()
        attendance_record, created = cls.objects.get_or_create(
            user_id=user_id,
            attendance_date=today,
            defaults={
                'attendance_status': 'غياب',
                'departure_status': 'غياب',
                'ride_deducted': False,  
            }
        )

        if not is_departure and status == 'حضور':
            attendance_record.attendance_status = status
        elif is_departure and status == 'انصراف':
            attendance_record.departure_status = status

        if not attendance_record.ride_deducted:
            student = passenger.objects.filter(user__id=user_id).first()  
            if student and student.remaining_rides > 0:
                student.rides_used += 1  
                student.save()
                attendance_record.ride_deducted = True

        attendance_record.save()
        return attendance_record

from django.db import models
from django.utils.translation import gettext_lazy as _

from datetime import timedelta, date
def default_display_date():
    return date.today() + timedelta(days=1)











from django.db import models

class PaymentAccount(models.Model):
    PAYMENT_OPTIONS = [
        ('vf-cash', 'VF Cash'),
        ('instapay', 'InstaPay'),
        ('fawry', 'Fawry'),
    ]

    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTIONS)
    account_name = models.CharField(max_length=100)  # اسم الحساب أو الجهة
    account_number = models.CharField(max_length=50)  # رقم الحساب للتحويل
    additional_info = models.TextField(blank=True, null=True)  # معلومات إضافية، مثل الفرع أو الملاحظات

    def __str__(self):
        return f"{self.get_payment_option_display()} - {self.account_name}"

class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'نقداً'),
        ('online', 'أونلاين'),
    ]
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
    ]
    booking = models.OneToOneField(
        'Booking',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="الحجز",
        null=True,  # السماح بالقيم الفارغة
        blank=True 
    )
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES,         null=True,  # السماح بالقيم الفارغة
        blank=True )
    payment = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,        null=True,  # السماح بالقيم الفارغة
        blank=True )

from django.db import models
from datetime import date

# class AttendanceRecord(models.Model):
#     student = models.ForeignKey('passenger', on_delete=models.CASCADE, related_name="attendance_records", verbose_name="الطالب")
#     date = models.DateField(default=date.today, verbose_name="تاريخ")
#     attendance_type = models.CharField(
#         max_length=10,
#         choices=[('arrival', 'حضور'), ('departure', 'انصراف')],
#         verbose_name="نوع التسجيل"
#     )

#     class Meta:
#         unique_together = ('student', 'date', 'attendance_type')  # كل تسجيل حضور/انصراف فريد ليوم معين

#     def __str__(self):
#         return f"{self.student.name} - {self.date} - {self.get_attendance_type_display()}"
