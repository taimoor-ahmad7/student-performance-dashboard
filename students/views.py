from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import StudentForm
from .models import Student


def get_float_value(value):
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 25

    allowed_sort_fields = {
        'final_grade_pct': 'final_grade_pct',
        '-final_grade_pct': '-final_grade_pct',
        'attendance_pct': 'attendance_pct',
        '-attendance_pct': '-attendance_pct',
    }

    def get_queryset(self):
        queryset = Student.objects.all()

        search_query = self.request.GET.get('q', '').strip()
        sex = self.request.GET.get('sex', '').strip()
        subject = self.request.GET.get('subject', '').strip()
        studytime = self.request.GET.get('studytime', '').strip()
        attendance_min = self.request.GET.get('attendance_min', '').strip()
        attendance_max = self.request.GET.get('attendance_max', '').strip()
        sort = self.request.GET.get('sort', '').strip()

        if search_query:
            # There is no student name column, so the search covers the ID and useful text fields.
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

        attendance_min_value = self.get_float_value(attendance_min)
        attendance_max_value = self.get_float_value(attendance_max)

        if attendance_min_value is not None:
            queryset = queryset.filter(attendance_pct__gte=attendance_min_value)

        if attendance_max_value is not None:
            queryset = queryset.filter(attendance_pct__lte=attendance_max_value)

        if sort in self.allowed_sort_fields:
            queryset = queryset.order_by(self.allowed_sort_fields[sort], 'student_id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()

        # Pagination links should keep the current search/filter/sort values.
        query_params.pop('page', None)

        context['filters'] = {
            'q': self.request.GET.get('q', ''),
            'sex': self.request.GET.get('sex', ''),
            'subject': self.request.GET.get('subject', ''),
            'attendance_min': self.request.GET.get('attendance_min', ''),
            'attendance_max': self.request.GET.get('attendance_max', ''),
            'studytime': self.request.GET.get('studytime', ''),
            'sort': self.request.GET.get('sort', ''),
        }
        context['querystring'] = query_params.urlencode()
        return context

    def get_float_value(self, value):
        # Invalid filter values are ignored instead of showing a server error.
        return get_float_value(value)


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        # A success message appears on the next page after the record is saved.
        messages.success(self.request, 'Student record created successfully.')
        return super().form_valid(form)


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'

    def get_success_url(self):
        # After editing, send the user back to the updated student's detail page.
        return reverse_lazy('students:student_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Student record updated successfully.')
        return super().form_valid(form)


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')
    context_object_name = 'student'

    def form_valid(self, form):
        messages.success(self.request, 'Student record deleted successfully.')
        return super().form_valid(form)


@login_required
def compare_view(request):
    selected_student_ids = parse_student_ids(request.GET.get('ids', ''))[:4]
    selected_students = get_selected_students(selected_student_ids)
    student_search = request.GET.get('student_search', '').strip()
    candidate_students = get_candidate_students(student_search, selected_students)
    comparison_rows = build_comparison_rows(selected_students)
    chart_data = {
        'labels': [str(student.student_id) for student in selected_students],
        'final_grade_pct': [student.final_grade_pct for student in selected_students],
        'attendance_pct': [student.attendance_pct for student in selected_students],
    }

    return render(
        request,
        'students/compare.html',
        {
            'student_search': student_search,
            'selected_student_ids': selected_student_ids,
            'selected_students': selected_students,
            'candidate_students': candidate_students,
            'comparison_rows': comparison_rows,
            'chart_data': chart_data,
        },
    )


def parse_student_ids(raw_ids):
    student_ids = []

    for raw_id in raw_ids.split(','):
        raw_id = raw_id.strip()

        if raw_id.isdigit():
            student_ids.append(int(raw_id))

    # dict.fromkeys keeps the original order while removing duplicates.
    return list(dict.fromkeys(student_ids))


def get_selected_students(student_ids):
    students_by_id = {
        student.student_id: student
        for student in Student.objects.filter(student_id__in=student_ids)
    }
    return [
        students_by_id[student_id]
        for student_id in student_ids
        if student_id in students_by_id
    ]


def get_candidate_students(search_query, selected_students):
    queryset = Student.objects.all()

    if search_query:
        search_filter = Q(school__icontains=search_query)

        if search_query.isdigit():
            search_filter |= Q(student_id=int(search_query))

        queryset = queryset.filter(search_filter)

    candidate_students = list(queryset.order_by('student_id')[:50])
    candidates_by_id = {student.student_id: student for student in candidate_students}

    for student in selected_students:
        candidates_by_id.setdefault(student.student_id, student)

    return sorted(candidates_by_id.values(), key=lambda student: student.student_id)


def build_comparison_rows(students):
    fields = [
        {'label': 'Student ID', 'attribute': 'student_id'},
        {'label': 'School', 'attribute': 'school'},
        {'label': 'Sex', 'attribute': 'sex'},
        {'label': 'Age', 'attribute': 'age'},
        {'label': 'Subject', 'attribute': 'subject'},
        {'label': 'Study Time', 'attribute': 'studytime', 'higher_is_better': True},
        {'label': 'Failures', 'attribute': 'failures', 'higher_is_better': False},
        {'label': 'Absences', 'attribute': 'absences', 'higher_is_better': False},
        {'label': 'G1', 'attribute': 'G1', 'higher_is_better': True},
        {'label': 'G2', 'attribute': 'G2', 'higher_is_better': True},
        {'label': 'Final Grade', 'attribute': 'final_grade', 'higher_is_better': True},
        {'label': 'Final Grade %', 'attribute': 'final_grade_pct', 'higher_is_better': True, 'is_percent': True},
        {'label': 'Attendance %', 'attribute': 'attendance_pct', 'higher_is_better': True, 'is_percent': True},
    ]

    rows = []

    for field in fields:
        raw_values = [getattr(student, field['attribute']) for student in students]
        best_value = None
        worst_value = None

        if 'higher_is_better' in field and len(raw_values) > 1:
            best_value = max(raw_values) if field['higher_is_better'] else min(raw_values)
            worst_value = min(raw_values) if field['higher_is_better'] else max(raw_values)

            if best_value == worst_value:
                best_value = None
                worst_value = None

        cells = []

        for value in raw_values:
            cells.append({
                'value': format_comparison_value(value, field.get('is_percent', False)),
                'is_best': best_value is not None and value == best_value,
                'is_worst': worst_value is not None and value == worst_value,
            })

        rows.append({
            'label': field['label'],
            'cells': cells,
        })

    return rows


def format_comparison_value(value, is_percent=False):
    if is_percent:
        return f'{value:.1f}%'

    return value
