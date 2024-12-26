from django import forms
from .models import Booking  # استبدل Booking باسم نموذج الحجز الخاص بك

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking  # استبدل Booking بالنموذج المناسب للحجز
        fields = ['seats_reserved', 'payment_method', 'transfer_message', 'trip_type']  # أضف الحقول المناسبة هنا
        labels = {
            'seats_reserved': 'Seat Number',
            'payment_method': 'Payment Method',
            'transfer_message': 'Transfer Confirmation Message',
        }
        widgets = {
            'seats_reserved': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transfer_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),


        }
from django import forms
from django.contrib.auth.models import User
from .models import passenger, Category  # استيراد الفئات اللازمة
from datetime import timedelta
class SignupForm(forms.ModelForm):
    university_id = forms.CharField(max_length=100, label="كود الجامعة")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="الجامعة")
    phone_number = forms.CharField(max_length=20, label="رقم الهاتف")  # إضافة حقل رقم الهاتف

    class Meta:
        model = User
        fields = ['username', 'password', 'university_id', 'phone_number']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # تعيين كلمة المرور
        university_id = self.cleaned_data['university_id']
        phone_number = self.cleaned_data['phone_number']  # جلب رقم الهاتف

        if commit:
            user.save()
            # إنشاء عنصر جديد في passenger وربطه بالمستخدم
            passenger.objects.create(
                user=user,
                name=user.username,  # استخدم اسم المستخدم كاسم الطالب
                university_code=university_id,
                phone_number=phone_number,  # إضافة رقم الهاتف
                subscription_duration=0,  # مدة الاشتراك الافتراضية
                category=self.cleaned_data['category'],
            )
        return user

#
# class SignupForm(forms.ModelForm):
#     university_code = forms.CharField(max_length=20, label="الكود الجامعي")
#     category = forms.ModelChoiceField(queryset=Category.objects.all(), label="الجامعة")
#     student_name = forms.CharField(max_length=64, label="اسم الطالب")

#     class Meta:
#         model = User
#         fields = ['username', 'password']
#         widgets = {
#             'password': forms.PasswordInput(),
#         }

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password'])  # تعيين كلمة المرور

#         if commit:
#             user.save()
#             # إنشاء عنصر جديد في passenger وربطه بالمستخدم
#             passenger.objects.create(
#                 user=user,
#                 university_code=self.cleaned_data['university_code'],
#                 category=self.cleaned_data['category'],
#                 name=self.cleaned_data['student_name']
#             )
#         return user
