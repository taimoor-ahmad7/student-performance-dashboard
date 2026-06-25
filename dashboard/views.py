import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from students.models import Student


def get_students_dataframe():
    # Django ORM reads the database rows; Pandas then makes averages/grouping easy.
    students = Student.objects.values(
        'student_id',
        'sex',
        'studytime',
        'subject',
        'final_grade_pct',
        'attendance_pct',
    )
    return pd.DataFrame.from_records(students)


@login_required
def dashboard_home(request):
    df = get_students_dataframe()

    if df.empty:
        summary = {
            'total_students': 0,
            'average_final_grade': 0,
            'average_attendance': 0,
            'top_student': None,
            'pass_rate': 0,
        }
    else:
        top_student_row = df.sort_values('final_grade_pct', ascending=False).iloc[0]
        pass_rate = (df['final_grade_pct'] >= 50).mean() * 100

        summary = {
            'total_students': len(df),
            'average_final_grade': df['final_grade_pct'].mean(),
            'average_attendance': df['attendance_pct'].mean(),
            'top_student': {
                'student_id': int(top_student_row['student_id']),
                'final_grade_pct': top_student_row['final_grade_pct'],
            },
            'pass_rate': pass_rate,
        }

    return render(
        request,
        'dashboard/dashboard.html',
        {
            'summary': summary,
            'insights': generate_insights(df),
        },
    )


def generate_insights(df):
    if df.empty:
        return ['No student records are available for insight generation yet.']

    subject_averages = df.groupby('subject')['final_grade_pct'].mean().sort_values(ascending=False)
    best_subject = subject_averages.index[0]
    worst_subject = subject_averages.index[-1]
    best_subject_average = subject_averages.iloc[0]
    worst_subject_average = subject_averages.iloc[-1]

    low_attendance_average = df[df['attendance_pct'] < 75]['final_grade_pct'].mean()
    high_attendance_average = df[df['attendance_pct'] >= 75]['final_grade_pct'].mean()
    attendance_gap = high_attendance_average - low_attendance_average

    top_students = df.sort_values('final_grade_pct', ascending=False).head(3)
    top_student_list = ', '.join(
        f"{int(row.student_id)} ({row.final_grade_pct:.1f}%)"
        for row in top_students.itertuples(index=False)
    )

    pass_rate = (df['final_grade_pct'] >= 50).mean() * 100
    gender_averages = df.groupby('sex')['final_grade_pct'].mean()
    female_average = gender_averages.get('F', 0)
    male_average = gender_averages.get('M', 0)

    # Each sentence is plain English so it can be shown directly in the dashboard.
    return [
        f'{best_subject} is the best-performing subject with an average grade of {best_subject_average:.1f}%.',
        f'{worst_subject} is the lowest-performing subject with an average grade of {worst_subject_average:.1f}%.',
        f'Students with attendance below 75% score an average of {attendance_gap:.1f}% lower than those above 75%.',
        f'Top students this term: {top_student_list}.',
        f'{pass_rate:.1f}% of students passed (grade >= 50%).',
        f'Female students average {female_average:.1f}% vs male students {male_average:.1f}%.',
    ]


@login_required
def average_grade_by_subject_json(request):
    df = get_students_dataframe()

    if df.empty:
        labels = []
        values = []
    else:
        grouped = df.groupby('subject')['final_grade_pct'].mean().round(2)
        labels = grouped.index.tolist()
        values = grouped.tolist()

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def gender_distribution_json(request):
    df = get_students_dataframe()

    if df.empty:
        labels = []
        values = []
    else:
        counts = df['sex'].value_counts().sort_index()
        labels = counts.index.tolist()
        values = counts.tolist()

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def average_grade_by_studytime_json(request):
    df = get_students_dataframe()

    if df.empty:
        labels = []
        values = []
    else:
        grouped = df.groupby('studytime')['final_grade_pct'].mean().round(2)
        labels = [str(label) for label in grouped.index.tolist()]
        values = grouped.tolist()

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def final_grade_histogram_json(request):
    df = get_students_dataframe()
    labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']

    if df.empty:
        values = [0 for _ in labels]
    else:
        # Each range includes whole-number percentage bands such as 11-20 and 91-100.
        values = [
            int(((df['final_grade_pct'] >= start) & (df['final_grade_pct'] <= end)).sum())
            for start, end in [
                (0, 10),
                (11, 20),
                (21, 30),
                (31, 40),
                (41, 50),
                (51, 60),
                (61, 70),
                (71, 80),
                (81, 90),
                (91, 100),
            ]
        ]

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def attendance_grade_scatter_json(request):
    df = get_students_dataframe()

    if df.empty:
        points = []
    else:
        # A 200-point sample keeps the browser chart fast while still showing the pattern.
        sample = df.sample(n=min(200, len(df)), random_state=42)
        points = [
            {'x': row.attendance_pct, 'y': row.final_grade_pct}
            for row in sample.itertuples(index=False)
        ]

    return JsonResponse({'points': points})
