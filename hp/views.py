from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import UserProfile, Doctor, Appointment, Prescription

def home(request):
    return render(request, 'hp/index.html')

def register_view(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        role = request.POST.get('role')
        phone = request.POST.get('phone')

        if User.objects.filter(username=u_name).exists():
            return render(request, 'hp/register.html', {'error': 'این نام کاربری قبلا ثبت شده است.'})

        user = User.objects.create_user(username=u_name, password=p_word)
        UserProfile.objects.create(user=user, role=role, phone_number=phone)

        if role == 'doctor':
            spec_select = request.POST.get('specialization_select')
            spec_custom = request.POST.get('specialization_custom')
            final_spec = spec_custom if spec_select == 'custom' and spec_custom else spec_select
            Doctor.objects.create(user=user, specialization=final_spec or 'عمومی')

        login(request, user)
        return redirect('dashboard')

    return render(request, 'hp/register.html')

def login_view(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'hp/login.html', {'error': 'نام کاربری یا رمز عبور اشتباه است.'})
    return render(request, 'hp/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'staff'}
    )
    
    context = {'profile': profile}

    if profile.role == 'patient':
        context['appointments'] = Appointment.objects.filter(patient=request.user)

    elif profile.role == 'doctor':
        try:
            doctor_obj = Doctor.objects.get(user=request.user)
            context['appointments'] = Appointment.objects.filter(doctor=doctor_obj)
        except Doctor.DoesNotExist:
            context['appointments'] = []

    elif profile.role == 'nurse':
        context['appointments'] = Appointment.objects.filter(status='confirmed')

    else:
        # پرسنل اداری / ادمین - دریافت اطلاعات همه نقش‌ها
        context['appointments'] = Appointment.objects.all()
        context['doctors'] = Doctor.objects.all()
        context['patients'] = UserProfile.objects.filter(role='patient')
        context['nurses'] = UserProfile.objects.filter(role='nurse')  # <--- اضافه شدن لیست پرستاران

    return render(request, 'hp/dashboard.html', context)
def book_appointment(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        doc_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        doctor = Doctor.objects.get(id=doc_id)
        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=date,
            time_slot=time_slot,
            status='pending'
        )
        return redirect('dashboard')

    doctors = Doctor.objects.all()
    return render(request, 'hp/book_appointment.html', {'doctors': doctors})

def delete_appointment(request, app_id):
    if not request.user.is_authenticated:
        return redirect('login')
    appointment = get_object_or_404(Appointment, id=app_id)
    profile = getattr(request.user, 'profile', None)
    if appointment.patient == request.user or (profile and profile.role in ['staff', 'doctor']):
        appointment.delete()
    return redirect('dashboard')

def update_appointment_status(request, app_id, status):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role in ['staff', 'doctor']:
        appointment = get_object_or_404(Appointment, id=app_id)
        appointment.status = status
        appointment.save()
    return redirect('dashboard')

# ویوی نوشتن و مشاهده نسخه
# بانک اطلاعاتی داروها بر اساس تخصص پزشک
SUGGESTED_MEDICINES = {
    'عمومی': [
        {'name': 'قرص آزیترومایسین 500', 'usage': 'روزی یک عدد بعد از غذا'},
        {'name': 'شربت دیفن هیدرامین', 'usage': 'هر 8 ساعت یک قاشق غذاخوری'},
        {'name': 'قرص استامینوفن 500', 'usage': 'هر 6 ساعت در صورت درد و تب'},
        {'name': 'قرص سرماخوردگی بزرگسالان', 'usage': 'هر 8 ساعت یک عدد'},
    ],
    'قلب و عروق': [
        {'name': 'قرص آسپیرین 80 (Aspirin)', 'usage': 'روزی یک عدد بعد از غذا'},
        {'name': 'قرص آتورواستاتین 20', 'usage': 'هر شب یک عدد قبل از خواب'},
        {'name': 'قرص لوزارتان 25', 'usage': 'روزی یک عدد صبح‌ها'},
        {'name': 'قرص متورال 50', 'usage': 'هر 12 ساعت نصف قرص'},
    ],
    'پوست و مو': [
        {'name': 'کرم کلوتریمازول', 'usage': 'روزی 2 بار موضعی روی محل'},
        {'name': 'کپسول زینک پلاس', 'usage': 'روزی یک عدد همراه غذا'},
        {'name': 'پماد هیدروکورتیزون 1%', 'usage': 'صبح و شب لایه نازک روی موضع'},
        {'name': 'شامپو کتوکونازول 2%', 'usage': 'هفته‌ای 2 بار در حمام 5 دقیقه بماند'},
    ],
    'اطفال': [
        {'name': 'قطره استامینوفن', 'usage': 'هر 6 ساعت دو برابر وزن کودک (به قطره)'},
        {'name': 'شربت کوآموکسی کلو ۲۴۸', 'usage': 'هر 12 ساعت 5 سی‌سی'},
        {'name': 'پودر کیدی لاکت', 'usage': 'روزی یک ساشه در ماست یا آبمیوه حل شود'},
    ],
    'اعصاب و روان': [
        {'name': 'قرص سرترالین 50', 'usage': 'صبح‌ها یک عدد بعد از صبحانه'},
        {'name': 'قرص آلپرازولام 0.5', 'usage': 'قبل از خواب یک عدد'},
        {'name': 'قرص پروپرانولول 20', 'usage': 'هر 12 ساعت یک عدد'},
    ],
    'ارتوپدی': [
        {'name': 'قرص دیکلوفناک 50', 'usage': 'هر 12 ساعت یک عدد بعد غذا'},
        {'name': 'کپسول پیروکسیکام', 'usage': 'روزی یک عدد'},
        {'name': 'قرص کلسیم دی', 'usage': 'روزی یک عدد همراه با آب زیاد'},
    ],
    'زنان و زایمان': [
        {'name': 'کپسول فمی لاکت', 'usage': 'روزی یک عدد همراه با غذا'},
        {'name': 'قرص اسید فولیک 1', 'usage': 'روزی یک عدد'},
        {'name': 'قرص فروس فولات (آهن)', 'usage': 'هر شب قبل از خواب'},
    ]
}

def prescription_view(request, app_id):
    if not request.user.is_authenticated:
        return redirect('login')

    appointment = get_object_or_404(Appointment, id=app_id)
    profile = getattr(request.user, 'profile', None)
    prescription = getattr(appointment, 'prescription', None)

    if request.method == 'POST' and profile and profile.role == 'doctor':
        meds = request.POST.get('medicines')
        inst = request.POST.get('instructions')
        
        if prescription:
            prescription.medicines = meds
            prescription.instructions = inst
            prescription.save()
        else:
            Prescription.objects.create(
                appointment=appointment,
                medicines=meds,
                instructions=inst
            )
        return redirect('dashboard')

    # دریافت لیست پیش‌فرض بر اساس تخصص پزشک
    doc_spec = appointment.doctor.specialization
    suggested_list = SUGGESTED_MEDICINES.get(doc_spec, SUGGESTED_MEDICINES['عمومی'])

    context = {
        'appointment': appointment,
        'prescription': prescription,
        'user_role': profile.role if profile else 'patient',
        'suggested_list': suggested_list
    }
    return render(request, 'hp/prescription_detail.html', context)

def delete_user(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile = getattr(request.user, 'profile', None)
    # فقط پرسنل اداری اجازه حذف کاربر را دارند
    if profile and profile.role == 'staff':
        user_to_delete = get_object_or_404(User, id=user_id)
        user_to_delete.delete()
        
    return redirect('dashboard')