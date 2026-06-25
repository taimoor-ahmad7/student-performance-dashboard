from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('csv/', views.export_students_csv, name='export_students_csv'),
    path('pdf/', views.export_students_pdf, name='export_students_pdf'),
]
