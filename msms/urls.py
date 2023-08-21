"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('log-in/', views.log_in, name='log_in'),
    path('register/', views.register, name='register'),
    path('children/', views.view_children, name="view_children"),
    path('register-teacher/', views.register_teacher, name='register_teacher'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log-out/', views.log_out, name='log_out'),
    path('administrator-accounts/', views.view_admins, name="view_admins"),
    path('students/', views.view_students, name="view_students"),
    path('administrator-accounts/delete/<str:email>/', views.delete_admin, name="delete_admin"),
    path('', views.dashboard, name='home'),
    path('administrator-accounts/update/<str:email>/', views.update_admin, name="update_admin"),
    path('request-lesson/', views.request_lesson, name='request_lesson'),
    path('lesson-requests/', views.view_lesson_requests, name='view_lesson_requests'),
    path('lesson-requests/update/<int:id>/', views.update_lesson_request, name="update_lesson_request"),
    path('lesson-requests/delete/<int:id>/', views.delete_lesson_request, name="delete_lesson_request"),
    path('lesson-requests/book/<int:id>/', views.book_lesson, name="book_lesson"),
    path('lesson-bookings/', views.view_lesson_bookings, name="view_lesson_bookings"),
    path('lesson-bookings/delete/<int:id>/', views.delete_lesson_booking, name="delete_lesson_booking"),
    path('lesson-bookings/update/<int:id>/', views.update_lesson_booking, name="update_lesson_booking"),
    path('lesson-bookings/invoice/<int:id>/', views.view_invoice_for_lesson_booking, name="view_invoice_for_lesson_booking"),
    path('register-school-term/',views.register_school_term,name="register_school_term"),
    path('school-terms/update/<int:id>/', views.update_school_term, name="update_school_term"),
    path('school-terms/', views.view_school_terms, name="view_school_terms"),
    path('register-transfer/', views.register_transfer, name="register_transfer"),
    path('transactions/<str:email>/', views.view_transactions, name="view_transactions"),
    path('transactions/', views.view_all_transactions, name="view_all_transactions"),
    path('teachers/', views.view_teachers, name='view_teachers'),
    path('teachers/update/<str:email>/', views.update_teacher, name="update_teacher"),
    path('teachers/delete/<str:email>/', views.delete_teacher, name="delete_teacher"),
    path('lesson-bookings/repeat/<int:id>/', views.request_repeat_booking, name="request_repeat_booking"),
]
