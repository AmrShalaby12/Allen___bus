from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, passenger
from django.utils.translation import gettext_lazy as _
from io import BytesIO
import qrcode
import base64
from django.utils.translation import gettext_lazy as _


from django.contrib import admin
from django.utils.safestring import mark_safe
import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont

class PassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'subscription_start_date','subscription_end_date','phone_number', 'university_code','total_rides', 'remaining_rides','subscription_duration')
    search_fields = ('name','university_code',)
    list_filter = ('category', 'subscription_start_date', 'subscription_end_date','subscription_duration')
    readonly_fields = ( 'subscription_start_date', 'subscription_end_date')

    def formatted_id(self, obj):
        return str(obj.id).zfill(4)
    formatted_id.short_description = 'ID'

    def generate_qr_code(self, data, text):
        # توليد QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # توليد صورة QR
        qr_img = qr.make_image(fill='black', back_color='red')
        
        # إعداد النص لعرضه أسفل QR كود
        font = ImageFont.load_default()  # يمكنك تحميل خط معين إذا أردت
        
        text_height = 50  # تحديد ارتفاع المساحة المخصصة للنص
        img_width, img_height = qr_img.size
        
        # توليد صورة جديدة بحجم أكبر لاستيعاب النص
        total_height = img_height + text_height
        combined_img = Image.new('RGB', (img_width, total_height), 'white')
        combined_img.paste(qr_img, (0, 0))
        
        # إضافة النص أسفل QR كود
        draw = ImageDraw.Draw(combined_img)
        draw.text((60, img_height + 5), text, font=font, fill='black')  # النص يظهر أسفل QR كود

        # تحويل الصورة النهائية إلى Base64
        buffer = BytesIO()
        combined_img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_str

    def qr_code_tag(self, obj):
        # إعداد البيانات لتوليد QR كود
        qr_data = f"Product ID: {obj.id}, Name: {obj.name}, Category: {obj.category.name}, Start Date: {obj.subscription_start_date}, End Date: {obj.subscription_end_date}"
        item_text = f" student ID: {obj.id}  copyright  shalapyDIV    farahMO uiux     "

        # توليد QR كود مع النص
        qr_code_base64 = self.generate_qr_code(qr_data, item_text)

        # عرض QR كود مع النص في الـ Admin
        if qr_code_base64:
            return mark_safe(f'<img src="data:image/png;base64,{qr_code_base64}" width="150" height="170" />')
        return None
    qr_code_tag.short_description = 'عرض QR Code'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']



from django.utils.html import mark_safe
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Attendance, passenger


from .models import passenger
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.utils import timezone
from datetime import date, timedelta

from django.contrib import admin
from .models import Bus, Trip, Booking

from django.contrib import admin
from .models import Bus, Category


from django.contrib import admin
from .models import Trip,destination

@admin.register(destination)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
@admin.action(description=_("تجديد الرحلات المختارة لمدة يوم / أسبوع / شهر"))
def renew_selected_trips(modeladmin, request, queryset):
    """
    تجديد الرحلات بناءً على الخيار الذي يختاره المستخدم.
    """
    # اطلب من المستخدم إدخال نوع التجديد
    period = request.POST.get('period', 'day')  # القيمة الافتراضية يوم
    days = 0
    weeks = 0
    months = 0

    if period == 'day':
        days = 1
    elif period == 'week':
        weeks = 1
    elif period == 'month':
        months = 1

    for trip in queryset:
        try:
            trip.renew_trip(days=days, weeks=weeks, months=months)
        except ValueError as e:
            modeladmin.message_user(request, f"فشل تجديد الرحلة {trip.id}: {e}")

    modeladmin.message_user(request, _("تم تجديد الرحلات بنجاح."))
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

# دالة تجديد الرحلات
# def renew_selected_trips(modeladmin, request, queryset):
#     # تحديث حالة جميع المقاعد في الرحلات المختارة إلى غير محجوزة
#     for trip in queryset:
#         seats = Seat.objects.filter(bus=trip.bus)  # الحصول على المقاعد المرتبطة بالرحلة
#         seats.update(is_reserved=False)  # إعادة المقاعد إلى حالة غير محجوزة
#         messages.success(request, f"تم تجديد الرحلة '{trip.trip_name}' وإعادة جميع المقاعد إلى الحالة الأصلية.")
from django.utils.timezone import now, timedelta
from django.utils.timezone import now, timedelta

from datetime import timedelta

# def renew_selected_trips(modeladmin, request, queryset):
#     """
#     إجراء لتجديد الرحلات المحددة عن طريق إضافة يوم إلى تاريخ الرحلة وجعل حجوزاتها غير نشطة.
#     """
#     for trip in queryset:
#         # تحديث حالة الحجوزات المرتبطة إلى "غير نشطة"
#         trip.bookings.filter(status="active").update(status="inactive")
        
#         # إضافة يوم واحد إلى تاريخ الرحلة الحالي
#         trip.date += timedelta(days=1)
        
#         # إعادة تنشيط الرحلة
#         trip.is_active = True  
#         trip.save()
        
#         # تحديث حالة المقاعد المرتبطة بالرحلة
#         seats = Seat.objects.filter(bus=trip.bus)
#         seats.update(is_reserved=False)

#     # رسالة تأكيد للمسؤول
#     modeladmin.message_user(request, "تم تجديد الرحلات وإضافة يوم إلى تاريخ الرحلة.")

from datetime import timedelta
from .models import Booking, Seat, Trip

def renew_trips_by_days(modeladmin, request, queryset, days_to_add):
    """
    إجراء عام لتجديد الرحلات بناءً على عدد الأيام المضاف.
    """
    for trip in queryset:
        # تحديث حالة الحجوزات المرتبطة بالرحلة الحالية
        trip.bookings.filter(status="active").update(status="inactive")

        # تحديث المقاعد للحافلة المرتبطة
        seats = Seat.objects.filter(bus=trip.bus)
        seats.update(is_reserved=False)

        # تعيين الرحلة الحالية كـ "قديمة" وغير نشطة
        trip.is_active = False
        trip.is_old = True
        trip.save()

        # إنشاء نسخة جديدة للرحلة مع التاريخ الجديد
        Trip.objects.create(
            trip_name=trip.trip_name,
            route=trip.route,
            date=trip.date + timedelta(days=days_to_add),
            start_time=trip.start_time,
            bus=trip.bus,
            is_active=True,  # الرحلة الجديدة تصبح نشطة
            is_old=False,    # الرحلة الجديدة ليست قديمة
        )

    # رسالة نجاح
    modeladmin.message_user(
        request,
        f"تم تجديد الرحلات وإضافة {days_to_add} يوم{'اً' if days_to_add == 1 else ''} إلى تاريخها."
    )

# تعريف الإجراءات الفردية
def renew_trips_one_day(modeladmin, request, queryset):
    renew_trips_by_days(modeladmin, request, queryset, days_to_add=1)

renew_trips_one_day.short_description = "تجديد الرحلات المختارة - إضافة يوم واحد"

def renew_trips_two_days(modeladmin, request, queryset):
    renew_trips_by_days(modeladmin, request, queryset, days_to_add=2)

renew_trips_two_days.short_description = "تجديد الرحلات المختارة - إضافة يومين"

def renew_trips_one_week(modeladmin, request, queryset):
    renew_trips_by_days(modeladmin, request, queryset, days_to_add=7)

renew_trips_one_week.short_description = "تجديد الرحلات المختارة - إضافة أسبوع"

def renew_trips_one_month(modeladmin, request, queryset):
    renew_trips_by_days(modeladmin, request, queryset, days_to_add=30)

renew_trips_one_month.short_description = "تجديد الرحلات المختارة - إضافة شهر"

from django.utils.timezone import now
from django.contrib import admin
from django import forms
from .models import Trip

class TripAdminForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = '__all__'

    # تخصيص حقل route ليكون واجهة نصية متعددة الأسطر
    route = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        help_text="أدخل كل خط في سطر جديد."
    )

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_name', 'route', 'date', 'start_time', 'bus', 'is_active', 'is_old')
    list_filter = ('is_active', 'is_old', 'date')
    search_fields = ('trip_name', 'bus__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # عرض الرحلات غير القديمة فقط بشكل افتراضي
        return qs.filter(is_old=False)

    # الإجراءات (Actions) لتجديد الرحلات
    actions = [
        renew_trips_one_day,
        renew_trips_two_days,
        renew_trips_one_week,
        renew_trips_one_month,
    ]

from django.contrib import admin
from .models import Booking

from django.contrib import admin
from .models import Booking

from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'Trip', 'get_selected_route', 'reserved_seats_list',
        'reserved_seats_count', 'payment_method', 'transaction_number', 
        'mobile_number', 'passenger_phone', 'status', 
        'attendance_status', 'serial_code', 
    )
    search_fields = (
        'transaction_number', 'mobile_number', 'user__username', 
        'schedule__bus__bus_number', 'attendance_status'
    )
    list_filter = ('Trip','selected_route','payment_method', 'status', 'attendance_status')
    fields = (
        'user', 'Trip', 'seats_reserved', 'payment_method', 
        'transaction_number', 'mobile_number', 'transaction_image', 
        'status', 'attendance_status'
    )
    actions = ['cancel_booking']
    def get_selected_route(self, obj):
            return obj.selected_route or "-"  # عرض القيمة أو عرض "-" إذا كانت فارغة
    get_selected_route.short_description = "Selected Route"
    def cancel_booking(self, request, queryset):
        for booking in queryset:
            if booking.status == 'completed':
                self.message_user(
                    request, 
                    f"لا يمكن إلغاء الحجز {booking.id} لأنه مكتمل.", 
                    level="error"
                )
                continue
            # إلغاء الحجز وإرجاع المقاعد
            booking.status = 'cancelled'
            booking.seats_reserved.update(is_reserved=False)
            booking.save()

        self.message_user(request, "تم إلغاء الحجوزات المحددة وإعادة المقاعد إلى حالتها.")
    cancel_booking.short_description = "إلغاء الحجوزات وإعادة المقاعد"

admin.site.register(Booking, BookingAdmin)

from django.contrib import admin
from .models import Seat

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('bus', 'seat_number', 'is_reserved','trip_date')
    list_filter = (
        'bus', 
        'seat_number', 

    ) 

admin.site.register(passenger, PassengerAdmin)
admin.site.register(Category, CategoryAdmin)


# 
from django.contrib import admin
from .models import PaymentAccount

@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = ('payment_option', 'account_name')  # عرض الحقول الأساسية فقط
    search_fields = ('payment_option', 'account_name')  # الحقول القابلة للبحث
    list_filter = ('payment_option',)  # إضافة فلترة حسب طريقة الدفع

# User id
# Name
# Category
# Subscription start date
# Subscription end date
# Attendance date
# Attendance status
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Bus, Booking
@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'bus_type', 'capacity', 'Bus_driver', 'is_active')
    list_filter = ('category', 'bus_type', 'is_active')  # إضافة الفلاتر
    search_fields = ('name', 'plate_number', 'owner__username')

    def get_urls(self):
        # الروابط الافتراضية
        urls = super().get_urls()

        # رابط مخصص لعرض التقرير
        custom_urls = [
            path('bus-report/', self.admin_site.admin_view(self.bus_report_view), name='bus_report'),
        ]
        return custom_urls + urls

    def bus_report_view(self, request):
        buses = Bus.objects.all()
        report_data = []

        selected_category = request.GET.get('category', None)
        selected_bus_type = request.GET.get('bus_type', None)
        selected_trip_date = request.GET.get('trip_date', None)

        if selected_category:
            buses = buses.filter(category__id=selected_category)
        if selected_bus_type:
            buses = buses.filter(bus_type=selected_bus_type)

        for bus in buses:
            seats = Seat.objects.filter(bus=bus)
            if selected_trip_date:
                seats = seats.filter(trip_date=selected_trip_date)

            total_reservations = seats.filter(is_reserved=True).count()
            total_capacity = bus.capacity
            driver_name = bus.Bus_driver.username if bus.Bus_driver else "لا يوجد سائق"

            report_data.append({
                "bus_name": bus.name,
                "university_name": bus.category.name,
                "driver_name": driver_name,
                "total_capacity": total_capacity,
                "total_reservations": total_reservations,
                "remaining_seats": total_capacity - total_reservations,
            })

        context = {
            "title": "تقرير الحافلات",
            "report_data": report_data,
            "categories": Category.objects.all(),
            "bus_types": Bus.objects.values_list('bus_type', flat=True).distinct(),
            "trip_dates": Seat.objects.values_list('trip_date', flat=True).distinct(),
        }

        return render(request, "admin/bus_report.html", context)
