from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'subject',
        'sex',
        'age',
        'final_grade_pct',
        'attendance_pct',
    )
    list_filter = ('subject', 'sex', 'studytime')
    search_fields = ('student_id', 'school', 'subject')
