from django.db import models


class Student(models.Model):
    """One row from students/data/student_data_merged.csv."""

    # Basic student and school information.
    student_id = models.PositiveIntegerField(unique=True)
    school = models.CharField(max_length=10)
    sex = models.CharField(max_length=1)
    age = models.PositiveIntegerField()
    address = models.CharField(max_length=1)
    famsize = models.CharField(max_length=5)
    Pstatus = models.CharField(max_length=1)

    # Parent education/job and household context fields from the dataset.
    Medu = models.PositiveIntegerField()
    Fedu = models.PositiveIntegerField()
    Mjob = models.CharField(max_length=30)
    Fjob = models.CharField(max_length=30)
    reason = models.CharField(max_length=30)
    guardian = models.CharField(max_length=30)

    # Study habits and previous academic history.
    traveltime = models.PositiveIntegerField()
    studytime = models.PositiveIntegerField(db_index=True)
    failures = models.PositiveIntegerField()

    # The CSV stores these as "yes" / "no"; the import command will convert them.
    schoolsup = models.BooleanField()
    famsup = models.BooleanField()
    paid = models.BooleanField()
    activities = models.BooleanField()
    nursery = models.BooleanField()
    higher = models.BooleanField()
    internet = models.BooleanField()
    romantic = models.BooleanField()

    # Lifestyle and wellbeing survey scores.
    famrel = models.PositiveIntegerField()
    freetime = models.PositiveIntegerField()
    goout = models.PositiveIntegerField()
    Dalc = models.PositiveIntegerField()
    Walc = models.PositiveIntegerField()
    health = models.PositiveIntegerField()
    absences = models.PositiveIntegerField()

    # Raw period grades use the original 0-20 scale from the dataset.
    G1 = models.PositiveIntegerField()
    G2 = models.PositiveIntegerField()
    final_grade = models.PositiveIntegerField()

    # Subject and normalized percentages are the main dashboard/filter fields.
    subject = models.CharField(max_length=20, db_index=True)
    G1_pct = models.FloatField()
    G2_pct = models.FloatField()
    final_grade_pct = models.FloatField(db_index=True)
    attendance_pct = models.FloatField(db_index=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f'{self.student_id} - {self.subject}'
