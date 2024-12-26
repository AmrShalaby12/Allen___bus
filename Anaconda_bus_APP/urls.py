from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import signup
from .views import user_profile, generate_qr
from .views import show_bus_location

urlpatterns = [
    path('stop-live-location/<int:bus_id>/', views.stop_live_location, name='stop_live_location'),
    path('bus/<int:bus_id>/location/', show_bus_location, name='show_bus_location'),

    path('admin/bus-report/', views.bus_report_view, name='bus_report'),
    path('mark-attendance/<int:booking_id>/', views.mark_attendance, name='mark_attendance'),
    path('end-trip/<int:trip_id>/', views.end_trip, name='end_trip'),
    path('success/', views.success_page, name='success_page'),
    path('check-trip-code/', views.check_trip_code, name='check_trip_code'),
    path('update-bus-location/<int:bus_id>/', views.update_bus_location, name='update_bus_location'),
    path('user-data/', user_profile, name='user_data'),
    path('update-live-location/<int:bus_id>/', views.update_live_location, name='update_live_location'),
    path('my-buses/', views.my_buses, name='my_buses'),  # مسار صفحة الباص
    path('register_student/', views.signup, name='register_student'),
    # path('update_status/<int:schedule_id>/', views.update_driver_status, name='update_driver_status'),
    path('search/', views.search_routes, name='search_routes'),
    path('', views.index, name='index'),  # الصفحة الرئيسية
    path('book/<int:schedule_id>/', views.book_seat, name='book_seat'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('book/<int:schedule_id>/', views.book_seat, name='book_seat'),
    path('', views.login_view, name="login"),
    # path("logout", views.logout_view, name="logout"),
    path('signup/', signup, name='signup'),
    path('sucess_form/', signup, name='sucess_form'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # path('scan_qr/', views.scan_qr, name='scan_qr'),
    path('attendance/', views.attendance_view, name='attendance'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
