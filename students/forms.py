from django import forms

from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id',
            'school',
            'sex',
            'age',
            'address',
            'famsize',
            'Pstatus',
            'Medu',
            'Fedu',
            'Mjob',
            'Fjob',
            'reason',
            'guardian',
            'traveltime',
            'studytime',
            'failures',
            'schoolsup',
            'famsup',
            'paid',
            'activities',
            'nursery',
            'higher',
            'internet',
            'romantic',
            'famrel',
            'freetime',
            'goout',
            'Dalc',
            'Walc',
            'health',
            'absences',
            'G1',
            'G2',
            'final_grade',
            'subject',
            'G1_pct',
            'G2_pct',
            'final_grade_pct',
            'attendance_pct',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap form controls make Django's generated form fields look consistent.
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            field.widget.attrs.setdefault('placeholder', field.label)
