from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = (
    ('patient', 'بیمار'),
    ('doctor', 'پزشک'),
    ('nurse', 'پرستار'),
    ('staff', 'اداری / پشتیبانی'),
)

APPOINTMENT_STATUS = (
    ('pending', 'در انتظار تایید'),
    ('confirmed', 'تایید شده'),
    ('canceled', 'لغو شده'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    national_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, default='عمومی')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    fee = models.PositiveIntegerField(default=100000)

    def __str__(self):
        return f"دکتر {self.user.get_full_name() or self.user.username} ({self.specialization})"

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    date = models.DateField()
    time_slot = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} با {self.doctor} - {self.date}"

# مدل جدید: نسخه پزشکی
class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    medicines = models.TextField(verbose_name="داروها")
    instructions = models.TextField(verbose_name="دستورات دارویی و توضیحات", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"نسخه {self.appointment.patient.username} - دکتر {self.appointment.doctor.user.username}"