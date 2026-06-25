from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('charts/average-grade-by-subject/', views.average_grade_by_subject_json, name='average_grade_by_subject_json'),
    path('charts/gender-distribution/', views.gender_distribution_json, name='gender_distribution_json'),
    path('charts/average-grade-by-studytime/', views.average_grade_by_studytime_json, name='average_grade_by_studytime_json'),
    path('charts/final-grade-histogram/', views.final_grade_histogram_json, name='final_grade_histogram_json'),
    path('charts/attendance-grade-scatter/', views.attendance_grade_scatter_json, name='attendance_grade_scatter_json'),
]
