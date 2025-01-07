from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from django.utils.timezone import now, localdate
from datetime import date, datetime, timedelta
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from itertools import groupby
from operator import attrgetter
from PIL import Image
import base64
import numpy as np
from pyzbar import pyzbar
import json
import cv2
import logging
from io import BytesIO  # تم إضافة الاستيراد الصحيح هنا
from .models import (
    passenger, 
    Attendance, 
    Trip, 
    Booking, 
    Seat, 
    Route, 
    PaymentAccount, 
    Bus, 
    Category
)
from .forms import SignupForm
import qrcode
from django.http import HttpResponse

# إعداد اللوجر
logger = logging.getLogger(__name__)


from datetime import date
def schedule_list(request):
    trip_id = Trip.objects.all()
    return render(request, 'index.html', {'schedules': trip_id})


@login_required
def book_seat(request, schedule_id):
    trip = get_object_or_404(Trip, id=schedule_id)
    seats = Seat.objects.filter(bus=trip.bus).order_by('seat_number')
    payment_accounts = PaymentAccount.objects.values('id', 'account_name', 'account_number', 'additional_info')

    # جلب صورة الكراسي الخاصة بالحافلة
    bus = trip.bus
    seats_image = bus.seats_image.url if bus and bus.seats_image else None

    # تقسيم النص في حقل `route` إلى قائمة خطوط
    routes = trip.route.splitlines()  # كل خط موجود في سطر جديد

    if request.method == 'POST':
        try:
            student = passenger.objects.get(user=request.user)
        except passenger.DoesNotExist:
            messages.info(request, "لا يمكن العثور على بيانات الطالب المرتبطة بحسابك. يرجى التواصل مع الإدارة.")
            return redirect('register_student')

        selected_seats = request.POST.getlist('selected_seats')
        payment_method = request.POST.get('payment_method')
        trip_type = request.POST.get('trip_type')
        selected_route = request.POST.get('selected_route')

        # التحقق من اختيار الخط
        if not selected_route or selected_route not in routes:
            messages.error(request, "يرجى اختيار خط صحيح.")
            return render(request, 'booking_form.html', {
                'trip': trip,
                'seats': seats,
                'payment_accounts': payment_accounts,
                'seats_image': seats_image,
                'routes': routes,
            })

        # التحقق من حجز المقعد
        for seat_id in selected_seats:
            seat = Seat.objects.get(id=seat_id)
            if seat.is_reserved:
                messages.error(request, f"المقعد {seat.seat_number} محجوز بالفعل!")
                return render(request, 'booking_form.html', {
                    'trip': trip,
                    'seats': seats,
                    'payment_accounts': payment_accounts,
                    'seats_image': seats_image,
                    'routes': routes,
                })

        # إنشاء الحجز
        booking = Booking.objects.create(
            Trip=trip,
            passenger=student,
            user=request.user,
            payment_method=payment_method,
            trip_type=trip_type,
            selected_route=selected_route
        )
        booking.seats_reserved.set(selected_seats)
        Seat.objects.filter(id__in=selected_seats).update(is_reserved=True)

        return redirect('success_page')  # توجيه المستخدم إلى صفحة النجاح

    return render(request, 'booking_form.html', {
        'trip': trip,
        'seats': seats,
        'payment_accounts': payment_accounts,
        'seats_image': seats_image,
        'routes': routes,
    })

def register_student(request):
    universities = Category.objects.all()  # استخراج الجامعات المسجلة

    if request.method == 'POST':
        university_code = request.POST.get('university_code')
        name = request.POST.get('name')
        university_name = request.POST.get('university')  # اسم الجامعة من المستخدم

        # التحقق من صحة الجامعة المختارة
        try:
            university = Category.objects.get(name=university_name)
        except Category.DoesNotExist:
            messages.error(request, "الجامعة المختارة غير موجودة.")
            return redirect('register_student')

        # التحقق من أن الكود الجامعي غير مسجل مسبقًا
        if passenger.objects.filter(university_code=university_code).exists():
            messages.error(request, "الكود الجامعي موجود بالفعل.")
            return redirect('register_student')

        # إنشاء الطالب الجديد
        passenger.objects.create(
            university_code=university_code,
            name=name,
            category=university,  # تمرير الكائن بدلاً من النص
            subscription_duration=0  # القيمة الافتراضية
        )
        messages.success(request, "تم تسجيل الطالب بنجاح!")
        return redirect('register_student')  # إعادة التوجيه إلى نفس الصفحة

    return render(request, 'register_student.html', {'universities': universities})

@login_required
def user_bookings(request):
    """
    عرض الحجوزات للمستخدم الحالي، مع التحديث التلقائي للحجوزات المنتهية.
    """

    # تحديث حالة الحجوزات بناءً على تاريخ الرحلة (تلقائي)
    Booking.objects.filter(
        user=request.user,
        Trip__date__lt=timezone.now().date(),  # الرحلات التي انتهى تاريخها
        status="active"  # الحجوزات النشطة
    ).update(status="completed")

    # جلب جميع الحجوزات الخاصة بالمستخدم
    bookings = Booking.objects.filter(user=request.user).select_related('Trip').order_by('-Trip__date')

    # تصفية الحجوزات حسب نوع الرحلة (إذا تم تحديدها)
    trip_type = request.GET.get('trip_type')
    if trip_type:
        bookings = bookings.filter(trip_type=trip_type)

    # تصفية الحجوزات حسب تاريخ الرحلة (إذا تم تحديده)
    trip_date = request.GET.get('trip_date')
    if trip_date:
        try:
            selected_date = datetime.strptime(trip_date, "%Y-%m-%d").date()
            bookings = bookings.filter(Trip__date=selected_date)
        except ValueError:
            # إذا كان التاريخ غير صحيح، يمكن تجاوز الفلتر أو إظهار رسالة خطأ.
            pass

    # تقسيم الحجوزات إلى نشطة ومنتهية
    active_bookings = bookings.filter(status="active")
    completed_bookings = bookings.filter(status="completed")

    # إرسال البيانات إلى القالب
    context = {
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'trip_type': trip_type,  # إرسال نوع الرحلة المحدد (إذا تم)
        'trip_date': trip_date,  # إرسال تاريخ الرحلة المحدد (إذا تم)
    }

    return render(request, 'user_bookings.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'completed':
        messages.error(request, "لا يمكن إلغاء الحجز بعد إتمام المعاملة.")
        return redirect('user_bookings')

    booking.status = 'cancelled'
    booking.save()
    booking.seats_reserved.update(is_reserved=False)

    messages.success(request, "تم إلغاء الحجز وإعادة المقاعد إلى حالتها.")
    return redirect('user_bookings')

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == 'completed':
        messages.error(request, "لا يمكن إلغاء الحجز بعد إتمام المعاملة.")
        return redirect('user_bookings')

    # إلغاء الحجز وتحديث حالة المقاعد
    booking.status = 'cancelled'
    booking.save()

    # إرجاع المقاعد إلى حالتها الفارغة
    booking.seats_reserved.update(is_reserved=False)

    messages.success(request, "تم إلغاء الحجز وإعادة المقاعد إلى حالتها.")
    return redirect('user_bookings')

def search_routes(request):
    if request.method == "GET":
        from_location = request.GET.get('from_location')
        to_location = request.GET.get('to_location')
        date = request.GET.get('date')

        
        routes = Route.objects.filter(
            from_location__icontains=from_location,
            to_location__icontains=to_location,
            date=date
        )

        return render(request, 'search_results.html', {'routes': routes})

def index(request):
    # استلام معايير البحث من الطلب
    selected_category = request.GET.get('Category', None)
    selected_date = request.GET.get('date', None)
    trip_type = request.GET.get('trip_type', None)
    start_time = request.GET.get('start_time', None)
    route = request.GET.get('route', None)

    # استعلام مبدئي لجلب الجداول (الرحلات النشطة فقط)
    schedules = Trip.objects.select_related('bus', 'bus__category').filter(
        bus__is_active=True, 
        is_active=True, 
        date__gte=now().date()  # الرحلات بتاريخ اليوم أو بعده فقط
    )

   
    buses_with_locations = Bus.objects.filter(location_url__isnull=False, is_active=True)

    # استعلام لجلب بيانات القوائم المنسدلة
    all_universities = Category.objects.all()
    all_trip_types = [
        ('one_way', 'ذهاب فقط'),
        ('return', 'عودة فقط'),
        ('round_trip', 'ذهاب وعودة'),
    ]
    all_start_times = Trip.objects.filter(is_active=True, date__gte=now().date()).values_list('start_time', flat=True).distinct()
    formatted_start_times = [time.strftime('%I:%M %p') for time in all_start_times]

    all_routes = Trip.objects.filter(is_active=True, date__gte=now().date()).values_list('route', flat=True).distinct()

    # معالجة الفلاتر
    filters = {}
    if selected_category:
        filters['bus__category__id'] = selected_category
    if selected_date:
        try:
            # التأكد من أن التاريخ صالح
            filters['date'] = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("تنسيق التاريخ غير صحيح. يجب إدخال التاريخ بتنسيق YYYY-MM-DD.")

    if trip_type:
        filters['trip_type'] = trip_type
    if start_time:
        try:
            # تحويل الوقت من صيغة 12 ساعة إلى كائن وقت
            start_time_obj = datetime.strptime(start_time, '%I:%M %p').time()
            filters['start_time__hour'] = start_time_obj.hour
            filters['start_time__minute'] = start_time_obj.minute
        except ValueError:
            raise ValidationError("التنسيق غير صحيح. يجب إدخال الوقت بتنسيق HH:MM AM/PM.")
    if route:
        filters['route__icontains'] = route

    # تطبيق الفلاتر على الرحلات
    schedules = schedules.filter(**filters)

    # تمرير البيانات إلى القالب
    return render(request, 'index.html', {
        'schedules': schedules,
        'buses_with_locations': buses_with_locations,
        'all_universities': all_universities,
        'all_trip_types': all_trip_types,
        'all_start_times': formatted_start_times,  # القيم المنسقة
        'all_routes': all_routes,
        'selected_Category': selected_category,
        'selected_date': selected_date,
        'trip_type': trip_type,
        'start_time': start_time,
        'route': route,
    })


@csrf_exempt
def update_live_location(request, bus_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            # تحديث موقع الباص في قاعدة البيانات
            bus = Bus.objects.get(id=bus_id)
            bus.latitude = latitude
            bus.longitude = longitude
            bus.location_url = f"https://www.google.com/maps?q={latitude},{longitude}"

            bus.save()

            return JsonResponse({'message': 'تم تحديث الموقع بنجاح!'})
        except Bus.DoesNotExist:
            return JsonResponse({'error': 'الباص غير موجود.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'طلب غير صالح.'}, status=400)

from django.shortcuts import render

def bus_live_location(request, bus_id):
    try:
        # جلب بيانات الباص
        bus = Bus.objects.get(id=bus_id)
        return render(request, 'bus_live_location.html', {'bus': bus})
    except Bus.DoesNotExist:
        return render(request, 'error.html', {'message': 'الباص غير موجود.'})

from django.http import JsonResponse

def stop_live_location(request, bus_id):
    if request.method == 'POST':
        # قم بحذف الموقع المرتبط بـ bus_id
        try:
            # استبدل هذا الكود حسب بنية بياناتك
            bus = Bus.objects.get(id=bus_id)
            bus.latitude = None
            bus.longitude = None
            bus.location_url = None
            bus.save()
            return JsonResponse({'message': 'تم إيقاف مشاركة الموقع بنجاح.'})
        except Bus.DoesNotExist:
            return JsonResponse({'error': 'المركبة غير موجودة.'}, status=404)
    return JsonResponse({'error': 'طريقة الطلب غير مدعومة.'}, status=400)

def bus_status(request):
    schedules = Trip.objects.all()

    # إضافة السياق
    context = {
        'schedules': schedules,
    }
    return render(request, 'bus_status.html', context)
from django.shortcuts import render, get_object_or_404
from .models import Bus

def show_bus_location(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    if not bus.latitude or not bus.longitude:
        return render(request, 'bus_location.html', {
            'error': 'لم يتم العثور على إحداثيات لهذه الحافلة.',
            'bus_name': bus.name,
        })

    return render(request, 'bus_location.html', {
        'latitude': str(bus.latitude).replace(',', '.'),
        'longitude': str(bus.longitude).replace(',', '.'),
        'bus_name': bus.name,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_live_location(request, bus_id):
    try:
        bus = get_object_or_404(Bus, id=bus_id)
        return JsonResponse({
            'latitude': bus.latitude,
            'longitude': bus.longitude,
        })
    except Bus.DoesNotExist:
        return JsonResponse({'error': 'الباص غير موجود.'}, status=404)

# def update_driver_status(request,  trip_id):
#     trip = get_object_or_404(trip, id= trip_id)

#     if request.method == "POST":
#         new_status = request.POST.get("driver_status")
#         if new_status in dict(trip.DRIVER_STATUS_CHOICES):
#             trip.driver_status = new_status
#             trip.save()
#             messages.success(request, "تم تحديث حالة السائق بنجاح.")
#         else:
#             messages.error(request, "حالة غير صالحة.")
#         return redirect('update_driver_status',  trip_id=trip.id)

#     return render(request, 'update_driver_status.html', {'trip': trip})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "Anaconda_bus_APP/index.html", {"message": "Invalid credentials."})
    return render(request, "Anaconda_bus_APP/login.html")
def logout_view(request):
    logout(request)
    return render(request, "Anaconda_bus_APP/login.html", {"message": "Logged out."})

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # تسجيل الدخول تلقائيًا بعد التسجيل
            return redirect('index')  # إعادة التوجيه إلى الصفحة الرئيسية
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def booking_list(request):
    items = passenger.objects.all()
    for item in items:
        if item.qr_code:
            # إذا كان qr_code بيانات ثنائية، تحويلها إلى Base64
            if isinstance(item.qr_code, bytes):
                item.qr_code_base64 = base64.b64encode(item.qr_code).decode('utf-8')
            else:
                # إذا كان qr_code سلسلة Base64، استخدمه كما هو
                item.qr_code_base64 = item.qr_code
        else:
            item.qr_code_base64 = None
    return render(request, 'user_data.html', {'items': items})


@login_required
def my_buses(request):
    # جلب جميع الباصات المرتبطة بالمستخدم
    buses = Bus.objects.filter(Bus_driver=request.user)
    today = localdate()  # الحصول على تاريخ اليوم

    # إعداد البيانات لكل باص
    buses_data = []
    for bus in buses:
        # جلب الرحلات النشطة المرتبطة بهذا الباص
        schedules = Trip.objects.filter(bus=bus, is_active=True)

        # تجميع الحجوزات حسب الخطوط والمناطق لكل باص
        bookings_by_route_and_area = {}
        for schedule in schedules:
            route = schedule.route  # اسم الخط الكامل
            areas = [area.strip() for area in route.split('\n')]  # تقسيم الخط إلى مناطق
            for area in areas:
                if area not in bookings_by_route_and_area:
                    bookings_by_route_and_area[area] = []
                bookings = schedule.bookings.filter(selected_route=area)

                # إضافة عدد الحجوزات المكتملة لهذا اليوم لكل حجز
                for booking in bookings:
                    booking.completed_bookings_today = booking.passenger.bookings.filter(
                        booking_date__date=today,
                        status='completed'
                    ).count()

                bookings_by_route_and_area[area].extend(bookings)

        # إضافة البيانات الخاصة بالباص إلى القائمة
        buses_data.append({
            'bus': bus,
            'bookings_by_route_and_area': bookings_by_route_and_area,
        })

    return render(request, 'my_buses.html', {
        'buses_data': buses_data,  # البيانات المرتبة حسب الباص
    })

def update_bus_location(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    if request.method == 'POST':
        location_url = request.POST.get('location_url')
        if location_url:
            bus.location_url = location_url
            bus.save()
            messages.success(request, "تم تحديث رابط الموقع بنجاح.")
        else:
            messages.error(request, "يجب إدخال رابط صالح.")
    return redirect('bus_status')

from django.shortcuts import render


def bus_status(request):
    buses = Bus.objects.all()
    return render(request, 'bus_status.html', {'buses': buses})


def attendance_view(request):
    if request.method == 'POST':
        attendance_data = request.POST.get('attendance_data', None)
        attendance_status = request.POST.get('attendance_status', None)

        if attendance_data:
            try:
                data = json.loads(attendance_data)
                existing_record = Attendance.objects.filter(
                    user_id=data['id'], attendance_date=date.today()
                ).first()

                student = passenger.objects.filter(id=data['id']).first()

                if not student:
                    messages.error(request, "Student not found!")
                    return render(request, 'scan_qr.html')

                if existing_record:
                    # تحقق إذا كان الحضور أو الانصراف مسجل مسبقًا
                    if attendance_status == 'حضور':
                        if existing_record.attendance_status == 'حضور':
                            messages.error(request, f"{data['name']} has already been marked as present today!")
                        else:
                            existing_record.attendance_status = 'حضور'
                            existing_record.save()
                            messages.success(request, f"{data['name']} marked as present successfully!")

                    elif attendance_status == 'انصراف':
                        if existing_record.departure_status == 'انصراف':
                            messages.error(request, f"{data['name']} has already been marked as departed today!")
                        else:
                            existing_record.departure_status = 'انصراف'
                            existing_record.save()
                            messages.success(request, f"{data['name']} marked as departed successfully!")

                    # خصم رحلة إذا لم يتم الخصم مسبقًا
                    if not existing_record.ride_deducted:
                        if student.remaining_rides > 0:
                            student.rides_used += 1
                            student.save()
                            existing_record.ride_deducted = True
                            existing_record.save()
                        else:
                            messages.error(request, f"{data['name']} has no remaining rides!")
                else:
                    # إذا لم يكن هناك سجل، قم بإنشائه وخصم الرحلة
                    ride_deducted = False
                    if student.remaining_rides > 0:
                        student.rides_used += 1
                        student.save()
                        ride_deducted = True
                    else:
                        messages.error(request, f"{data['name']} has no remaining rides!")

                    Attendance.objects.create(
                        user_id=data['id'],
                        name=data['name'],
                        category=data['category'],
                        subscription_start_date=data['subscription_start_date'],
                        subscription_end_date=data['subscription_end_date'],
                        attendance_status='حضور' if attendance_status == 'حضور' else 'غياب',
                        departure_status='انصراف' if attendance_status == 'انصراف' else 'غياب',
                        attendance_date=date.today(),
                        ride_deducted=ride_deducted,
                    )
                    messages.success(request, f"{data['name']} Attendance ({attendance_status}) recorded successfully!")

            except Exception as e:
                messages.error(request, f"Error: {e}")
    
    return render(request, 'scan_qr.html')

def attendance_reset_view(request):
    today = timezone.now().date()
    last_recorded_date = Attendance.objects.latest('attendance_date').attendance_date if Attendance.objects.exists() else None
    
    if not last_recorded_date or last_recorded_date < today:
        for item in passenger.objects.all():
            Attendance.objects.create(
                user_id=item.id,
                name=item.name,
                category=item.category.name,
                subscription_start_date=item.subscription_start_date,
                subscription_end_date=item.subscription_end_date,
                attendance_status='غياب',
                attendance_date=today
            )
    return render(request, 'attendance_page.html', {'attendance_list': Attendance.objects.filter(attendance_date=today)})



def get_qr_code_as_base64(item):
    if item.qr_code:
        return base64.b64encode(item.qr_code).decode('utf-8')
    return None

@login_required
def user_profile(request):
    try:
        current_passenger = passenger.objects.get(user=request.user)
    except passenger.DoesNotExist:
        current_passenger = None

    return render(request, 'user_data.html', {'items': [current_passenger] if current_passenger else []})


def generate_qr(request, item_id):
    item = get_object_or_404(passenger, id=item_id)
    qr_data = f"Student Code: {item.student_code}\nStudent Name: {item.student_name}\nUniversity: {item.university}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer, content_type="image/png")



@csrf_exempt
def end_trip(request, trip_id):
    if request.method == "POST":
        try:
            logger.info(f"Received request to end trip with ID: {trip_id}")

            # جلب الرحلة
            trip = get_object_or_404(Trip, id=trip_id)
            logger.info(f"Trip found: {trip}")

            # تحديث التاريخ
            trip.date += timedelta(days=1)
            trip.save()
            logger.info(f"Trip date updated to: {trip.date}")

            # إعادة تعيين حالة المقاعد
            seats = trip.bus.seats.all()
            seats.update(is_reserved=False)
            logger.info(f"Seats reset for bus: {trip.bus.name}")

            # تحديث الحجوزات المرتبطة
            bookings = Booking.objects.filter(Trip=trip)
            bookings.update(status="completed")
            logger.info(f"Bookings updated to 'completed' for trip: {trip.id}")

            return JsonResponse({"message": "تم إنهاء الرحلة وتحديثها لليوم التالي بنجاح."})
        except Http404:
            logger.error(f"Trip with ID {trip_id} not found.")
            return JsonResponse({"error": "الرحلة غير موجودة."}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error ending trip: {e}")
            return JsonResponse({"error": f"حدث خطأ غير متوقع: {e}"}, status=500)
    return JsonResponse({"error": "طريقة الطلب غير صحيحة."}, status=400)



def update_rides(request):
    item_id = request.POST.get('item_id')
    try:
        subscription = passenger.objects.get(id=item_id)
        if subscription.remaining_rides > 0:
            subscription.remaining_rides -= 1
            subscription.save()
            return JsonResponse({'success': 'Ride updated successfully'})
        else:
            return JsonResponse({'error': 'No remaining rides'}, status=400)
    except passenger.DoesNotExist:
        return JsonResponse({'error': 'Subscription not found'}, status=404)




@login_required
def check_trip_code(request):
    bookings = None
    student_bookings = None

    if request.method == 'POST':
        trip_code = request.POST.get('trip_code', None)
        university_code = request.POST.get('university_code', None)
        mark_paid = request.POST.get('mark_paid', None)  # للتحقق إذا تم اختيار "حجز كمدفوع مسبقًا"
        mark_attendance = request.POST.get('mark_attendance', None)  # للتحقق من زر تسجيل الحضور
        today = date.today()  # الحصول على تاريخ اليوم الحالي

        # البحث باستخدام كود الرحلة
        if trip_code:
            bookings = Booking.objects.filter(serial_code=trip_code, Trip__date=today)  # تصفية حجوزات اليوم الحالي
            if bookings.exists():
                messages.success(request, f"تم العثور على {bookings.count()} حجز مرتبط بكود الرحلة.")
            else:
                messages.error(request, "كود الرحلة غير صحيح أو لا توجد حجوزات لليوم الحالي. يرجى التحقق.")

        # البحث باستخدام كود الجامعة
        elif university_code:
            student = passenger.objects.filter(university_code=university_code).first()
            
            if student:
                # تصفية حجوزات اليوم الحالي فقط
                student_bookings = Booking.objects.filter(
                    passenger=student,
                    # status="active",  # الحجز يجب أن يكون نشطًا فقط
                    Trip__date=today
                ).select_related('passenger', 'payment')  # تحسين الأداء باستخدام select_related

                if student_bookings.exists():
                    if mark_paid:  # إذا تم اختيار الزر "حجز كمدفوع مسبقًا"
                        for booking in student_bookings:
                            if booking.attendance_status != "present":  # فقط الحجوزات التي لم تسجل حضورًا مسبقًا
                                booking.status = "prepaid"  # تحديث حالة الدفع كمدفوعة مسبقًا
                                booking.attendance_status = "present"  # تسجيل الحضور كحاضر
                                booking.save()  # حفظ التغييرات
                        messages.success(request, "تم تسجيل الحجز كمدفوع مسبقًا بنجاح.")

                    elif mark_attendance:  # إذا تم اختيار زر تسجيل الحضور
                        for booking in student_bookings:
                            if booking.attendance_status != "present":  # فقط الحجوزات التي لم تسجل حضورًا مسبقًا
                                booking.attendance_status = "present"  # تسجيل الحضور كحاضر
                                booking.status = "completed"  # تحديث الحالة إلى مكتملة
                                booking.save()  # حفظ التغييرات
                        messages.success(request, "تم تسجيل حضور الطالب للرحلة بنجاح.")
                else:
                    messages.info(request, "لا توجد رحلات محجوزة حالياً لهذا الطالب لليوم الحالي لم يتم تسجيل الحضور لها.")
            else:
                messages.error(request, "كود الجامعة غير صحيح. يرجى التحقق.")

    return render(request, 'check_trip_code.html', {
        'bookings': bookings,
        'student_bookings': student_bookings,
    })

@login_required
def mark_attendance(request, booking_id):
    try:
        # جلب الحجز
        booking = Booking.objects.get(id=booking_id)

        # التحقق من نوع الزر المضغوط
        mark_paid = request.POST.get('mark_paid', None)  # إذا كان الزر "حجز كمدفوع مسبقًا"
        mark_attendance = request.POST.get('mark_attendance', None)  # إذا كان الزر "تسجيل الحضور"

        if mark_paid:  # إذا كان المستخدم ضغط على "حجز كمدفوع مسبقًا"
            if booking.status == 'completed':  # التأكد أن الحجز ليس مكتملًا
                messages.warning(request, "هذا الحجز مكتمل بالفعل.")
                return redirect('check_trip_code')

            if booking.attendance_status == 'prepaid':  # التأكد أن الحجز ليس مدفوعًا مسبقًا
                messages.info(request, "تم تسجيل هذا الحجز كمدفوع مسبقًا بالفعل.")
                return redirect('check_trip_code')

            # تحديث حالة الدفع كمدفوع مسبقًا
            booking.attendance_status = 'present'
            booking.status = 'prepaid'
            booking.save()
            messages.success(request, f"تم تسجيل الحجز كمدفوع مسبقًا: {booking.serial_code}.")
            return redirect('check_trip_code')

        elif mark_attendance:  # إذا كان المستخدم ضغط على "تسجيل الحضور"
            if booking.status != 'active':  # التحقق أن الحجز نشط
                messages.warning(request, "هذا الحجز غير صالح لتسجيل الحضور.")
                return redirect('check_trip_code')

            if booking.attendance_status == 'present':  # التحقق من عدم تسجيل الحضور مسبقًا
                messages.info(request, "تم تسجيل الحضور مسبقًا لهذه الرحلة.")
                return redirect('check_trip_code')

            passenger_instance = booking.passenger  # جلب بيانات الراكب المرتبطة بالحجز

        with transaction.atomic():
            # إذا كانت الرحلات المتبقية <= 0
            if passenger_instance.remaining_rides <= 0:
                # تحديث حالة الحجز
                booking.attendance_status = 'present'
                booking.status = 'completed'

                # تسجيل رسالة نجاح
                messages.success(request, "تم تسجيل الحضور بنجاح. تم اعتبار الطالب مشتركًا ب الأيام.")
            else:
                # خصم رحلة واحدة من الرحلات المتبقية
                passenger_instance.remaining_rides -= 1
                passenger_instance.rides_used += 1

                # تحديث حالة الحجز
                booking.attendance_status = 'present'
                booking.status = 'completed'

                # تسجيل رسالة نجاح
                messages.success(request, "تم تسجيل الحضور بنجاح.")

            # حفظ التعديلات
            passenger_instance.save()  # تحديث بيانات الراكب
            booking.save()  # تحديث بيانات الحجز

            messages.success(request, f"تم تسجيل حضور الطالب للرحلة: {booking.serial_code}")
            return redirect('check_trip_code')

        # إذا لم يتم اختيار أي زر
        messages.error(request, "يرجى اختيار زر صالح.")
        return redirect('check_trip_code')

    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء معالجة الطلب: {str(e)}")
        return redirect('check_trip_code')

def success_page(request):
    return render(request, 'success.html')

def bus_report_view(request):
    # جلب الرحلات الحالية (المجددة والجديدة)
    trips = Trip.objects.filter(is_active=True)

    # جلب الرحلات السابقة (التي انتهت)
    past_trips = Trip.objects.filter(is_active=False)

    # تجهيز بيانات الرحلات الحالية
    report_data = []
    for trip in trips:
        bus = trip.bus
        total_capacity_value = bus.capacity if bus.capacity else 0
        total_reservations_count = Booking.objects.filter(Trip=trip).count()
        remaining_seats_value = total_capacity_value - total_reservations_count

        # حساب نسبة الإشغال
        if total_capacity_value > 0:
            occupancy_rate = (total_reservations_count / total_capacity_value) * 100
        else:
            occupancy_rate = 0

        # تحديد حالة تشغيل الحافلة
        if occupancy_rate < 50:
            bus_status = "ضعيف"
        elif 50 <= occupancy_rate <= 75:
            bus_status = "متوسط"
        else:
            bus_status = "جيد"

        report_data.append({
            "trip_name": trip.trip_name,
            "route": trip.route,
            "trip_date": trip.date,
            "trip_time": trip.start_time,
            "bus_name": bus.name,
            "university_name": bus.category.name if bus.category else "غير محدد",
            "driver_name": bus.Bus_driver.username if bus.Bus_driver else "لا يوجد سائق",
            "total_capacity": total_capacity_value,
            "total_reservations": total_reservations_count,
            "remaining_seats": remaining_seats_value,
            "occupancy_rate": round(occupancy_rate, 2),  # نسبة الإشغال
            "bus_status": bus_status,  # حالة الباص
        })

    # تجهيز بيانات الرحلات السابقة
    past_trip_data = []
    for trip in past_trips:
        bus = trip.bus
        total_capacity_value = bus.capacity
        total_reservations_count = Booking.objects.filter(Trip=trip).count()

        # حساب نسبة الإشغال
        if total_capacity_value > 0:
            occupancy_rate = (total_reservations_count / total_capacity_value) * 100
        else:
            occupancy_rate = 0

        # تحديد حالة تشغيل الحافلة
        if occupancy_rate < 50:
            bus_status = "ضعيف"
        elif 50 <= occupancy_rate <= 75:
            bus_status = "متوسط"
        else:
            bus_status = "جيد"

        past_trip_data.append({
            "trip_name": trip.trip_name,
            "route": trip.route,
            "trip_date": trip.date,
            "trip_time": trip.start_time,
            "bus_name": bus.name,
            "university_name": bus.category.name if bus.category else "غير محدد",
            "driver_name": bus.Bus_driver.username if bus.Bus_driver else "لا يوجد سائق",
            "total_reservations": total_reservations_count,
            "occupancy_rate": round(occupancy_rate, 2),  # نسبة الإشغال
            "bus_status": bus_status,  # حالة الباص
        })

    context = {
        "title": "تقرير الحافلات والرحلات",
        "report_data": report_data,  # بيانات الرحلات الحالية
        "past_trip_data": past_trip_data,  # بيانات الرحلات السابقة
    }
    return render(request, 'admin/bus_report.html', context)


def mark_attendance_university_code(request):
    if request.method == 'POST':
        university_code = request.POST.get('university_code', None)  # كود الجامعة
        serial_code = request.POST.get('serial_code', None)  # كود الحجز (serial_code)

        if university_code and serial_code:
            # البحث عن الطالب باستخدام كود الجامعة
            student = passenger.objects.filter(university_code=university_code).first()
            if student:
                # البحث عن الحجز باستخدام serial_code
                booking = Booking.objects.filter(
                    passenger=student,
                    serial_code=serial_code,  # الحجز بناءً على كود الحجز الفريد
                    attendance_status="absent"  # الحجوزات التي لم يتم تسجيل حضورها
                ).first()

                if booking:
                    # تسجيل الحضور للحجز
                    booking.attendance_status = "present"
                    booking.status = "active"
                    booking.save()

                    # تحديث بيانات الطالب
                    if student.remaining_rides > 0:
                        student.rides_used += 1
                        student.save()

                    messages.success(request, f"تم تسجيل الحضور بنجاح للرحلة بكود الحجز: {serial_code}")
                else:
                    messages.info(request, "لا يوجد حجز مرتبط بكود الرحلة المدخل أو الحجز مسجل حضور مسبقًا.")
            else:
                messages.error(request, "كود الجامعة غير صحيح.")
        else:
            messages.error(request, "يرجى إدخال كود الجامعة وكود الحجز.")

    return render(request, 'check_university_code.html')
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

def update_payment_status(request, booking_id):
    if request.method == "POST":
        try:
            if request.headers.get('Content-Type') == 'application/json':
                # معالجة البيانات كـ JSON
                data = json.loads(request.body)
                status = data.get('status')
            else:
                # معالجة البيانات كـ Form Data
                status = request.POST.get('status')

            if not status or status not in ['completed', 'prepaid']:
                return JsonResponse({"success": False, "error": "حالة غير صالحة."})

            booking = get_object_or_404(Booking, id=booking_id)
            booking.status = status
            booking.save()

            return JsonResponse({"success": True, "message": f"تم تحديث حالة الدفع إلى {status}"})

        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "الحجز غير موجود."})

    return JsonResponse({"success": False, "error": "طلب غير صالح."})
