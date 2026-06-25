from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from students.models import Student


class Command(BaseCommand):
    help = 'Load student records from students/data/student_data_merged.csv'

    def add_arguments(self, parser):
        # This optional argument lets you import a different CSV later if needed.
        parser.add_argument(
            '--csv',
            default='students/data/student_data_merged.csv',
            help='CSV file path, relative to the project root by default.',
        )

    def handle(self, *args, **options):
        csv_path = self.get_csv_path(options['csv'])

        if not csv_path.exists():
            raise CommandError(f'CSV file not found: {csv_path}')

        # Pandas reads the CSV into a DataFrame, which is like a table in memory.
        df = pd.read_csv(csv_path)
        self.validate_columns(df)

        # Re-loading a seed file should give the same database result every time.
        # We clear existing student rows first so unique student_id values do not clash.
        Student.objects.all().delete()

        bool_columns = [
            'schoolsup',
            'famsup',
            'paid',
            'activities',
            'nursery',
            'higher',
            'internet',
            'romantic',
        ]

        for column in bool_columns:
            # The CSV stores yes/no as text; Django BooleanField stores True/False.
            df[column] = df[column].map(self.yes_no_to_bool)

        students = [
            Student(
                student_id=row.student_id,
                school=row.school,
                sex=row.sex,
                age=row.age,
                address=row.address,
                famsize=row.famsize,
                Pstatus=row.Pstatus,
                Medu=row.Medu,
                Fedu=row.Fedu,
                Mjob=row.Mjob,
                Fjob=row.Fjob,
                reason=row.reason,
                guardian=row.guardian,
                traveltime=row.traveltime,
                studytime=row.studytime,
                failures=row.failures,
                schoolsup=row.schoolsup,
                famsup=row.famsup,
                paid=row.paid,
                activities=row.activities,
                nursery=row.nursery,
                higher=row.higher,
                internet=row.internet,
                romantic=row.romantic,
                famrel=row.famrel,
                freetime=row.freetime,
                goout=row.goout,
                Dalc=row.Dalc,
                Walc=row.Walc,
                health=row.health,
                absences=row.absences,
                G1=row.G1,
                G2=row.G2,
                final_grade=row.final_grade,
                subject=row.subject,
                G1_pct=row.G1_pct,
                G2_pct=row.G2_pct,
                final_grade_pct=row.final_grade_pct,
                attendance_pct=row.attendance_pct,
            )
            for row in df.itertuples(index=False)
        ]

        # bulk_create inserts all rows using fewer database queries than saving one by one.
        Student.objects.bulk_create(students, batch_size=500)

        self.stdout.write(
            self.style.SUCCESS(f'Loaded {len(students)} student records from {csv_path}')
        )

    def get_csv_path(self, csv_option):
        path = Path(csv_option)

        if path.is_absolute():
            return path

        return settings.BASE_DIR / path

    def validate_columns(self, df):
        expected_columns = [
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

        missing_columns = [column for column in expected_columns if column not in df.columns]

        if missing_columns:
            raise CommandError(
                'CSV is missing required columns: ' + ', '.join(missing_columns)
            )

    def yes_no_to_bool(self, value):
        normalized_value = str(value).strip().lower()

        if normalized_value == 'yes':
            return True

        if normalized_value == 'no':
            return False

        raise CommandError(f'Expected yes/no value, got: {value}')
