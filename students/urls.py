from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    # /students/ shows the paginated table of student records.
    path('', views.StudentListView.as_view(), name='student_list'),
    path('compare/', views.compare_view, name='student_compare'),
    path('new/', views.StudentCreateView.as_view(), name='student_create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
]
