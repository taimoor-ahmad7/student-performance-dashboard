import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from students.models import Student


@login_required
def reports_home(request):
    filters = {
        'q': request.GET.get('q', ''),
        'sex': request.GET.get('sex', ''),
        'subject': request.GET.get('subject', ''),
        'attendance_min': request.GET.get('attendance_min', ''),
        'attendance_max': request.GET.get('attendance_max', ''),
        'studytime': request.GET.get('studytime', ''),
    }

    return render(request, 'reports/reports.html', {'filters': filters})


@login_required
def export_students_csv(request):
    queryset = get_filtered_students(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'student_id',
        'subject',
        'sex',
        'final_grade_pct',
        'attendance_pct',
    ])

    for student in queryset:
        writer.writerow([
            student.student_id,
            student.subject,
            student.sex,
            student.final_grade_pct,
            student.attendance_pct,
        ])

    return response


@login_required
def export_students_pdf(request):
    queryset = get_filtered_students(request)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(letter),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph('Student Performance Report', styles['Title']),
        Spacer(1, 12),
    ]

    # ReportLab builds the PDF from a list of rows, starting with the table header.
    table_data = [['Student ID', 'Subject', 'Sex', 'Final Grade %', 'Attendance %']]

    for student in queryset:
        table_data.append([
            student.student_id,
            student.subject,
            student.sex,
            f'{student.final_grade_pct:.1f}',
            f'{student.attendance_pct:.1f}',
        ])

    if len(table_data) == 1:
        table_data.append(['No matching records', '', '', '', ''])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)
    document.build(elements)
    return response


def get_filtered_students(request):
    queryset = Student.objects.all()
    search_query = request.GET.get('q', '').strip()
    sex = request.GET.get('sex', '').strip()
    subject = request.GET.get('subject', '').strip()
    studytime = request.GET.get('studytime', '').strip()
    attendance_min = request.GET.get('attendance_min', '').strip()
    attendance_max = request.GET.get('attendance_max', '').strip()

    if search_query:
        # This mirrors the student list search fields so exports match the visible list.
        search_filter = (
            Q(school__icontains=search_query)
            | Q(subject__icontains=search_query)
            | Q(guardian__icontains=search_query)
            | Q(Mjob__icontains=search_query)
            | Q(Fjob__icontains=search_query)
            | Q(reason__icontains=search_query)
        )

        if search_query.isdigit():
            search_filter |= Q(student_id=int(search_query))

        queryset = queryset.filter(search_filter)

    if sex in ['F', 'M']:
        queryset = queryset.filter(sex=sex)

    if subject in ['Math', 'Portuguese']:
        queryset = queryset.filter(subject=subject)

    if studytime in ['1', '2', '3', '4']:
        queryset = queryset.filter(studytime=int(studytime))

    attendance_min_value = get_float_value(attendance_min)
    attendance_max_value = get_float_value(attendance_max)

    if attendance_min_value is not None:
        queryset = queryset.filter(attendance_pct__gte=attendance_min_value)

    if attendance_max_value is not None:
        queryset = queryset.filter(attendance_pct__lte=attendance_max_value)

    return queryset.order_by('student_id')


def get_float_value(value):
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        # Bad URL values should not crash report downloads.
        return None
