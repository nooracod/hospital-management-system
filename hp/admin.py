from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, Department, Doctor, Appointment, Prescription

admin.site.site_header = "سامانه مدیریت کل بیمارستان"
admin.site.site_title = "پنل ادمین"
admin.site.index_title = "کنترل کامل سیستم و کاربران"

# ۱. مدیریت کامل پزشکان
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'specialization', 'department', 'fee')
    list_filter = ('specialization', 'department')
    search_fields = ('user__username', 'specialization')
    
    def get_doctor_name(self, obj):
        return f"دکتر {obj.user.get_full_name() or obj.user.username}"
    get_doctor_name.short_description = 'نام پزشک'

# ۲. مدیریت بیماران
class PatientProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'بیمار'
        verbose_name_plural = 'لیست و مدیریت بیماران'

@admin.register(PatientProxy)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name')
    def get_queryset(self, request):
        return super().get_queryset(request).filter(profile__role='patient')

# ۳. مدیریت پرستاران
class NurseProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'پرستار'
        verbose_name_plural = 'لیست و مدیریت پرستاران'

@admin.register(NurseProxy)
class NurseAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name')
    def get_queryset(self, request):
        return super().get_queryset(request).filter(profile__role='nurse')

# ۴. مدیریت نوبت‌ها
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time_slot', 'status')
    list_filter = ('status', 'date')

# ۵. مدیریت نسخه‌ها
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'created_at')

admin.site.register(Department)
admin.site.register(UserProfile)