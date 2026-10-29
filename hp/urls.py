from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('appointment/delete/<int:app_id>/', views.delete_appointment, name='delete_appointment'),
    path('appointment/status/<int:app_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('prescription/<int:app_id>/', views.prescription_view, name='prescription_view'), # <--- نسخه
]