# Student Performance Dashboard

A full-stack web application for analyzing, visualizing, and generating insights from student academic data. Built with Python and Django as part of the Software Construction & Development course.

## Features

- **User Authentication** — Register, login, logout, profile management
- **Student Management** — Add, update, delete, and view student records (CRUD)
- **Search & Filtering** — Search by name/ID, filter by gender, subject, attendance, and study time
- **Student Comparison** — Compare 2–4 students side by side with highlights and chart
- **Dashboard** — Summary cards (total, average, pass rate, top student)
- **Visualizations** — Bar, Pie, Line, Histogram, and Scatter charts via Chart.js
- **Insight Generation** — Automated plain-English insights using Pandas
- **Reports** — Export filtered data as CSV or PDF

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.14, Django 6.0 |
| Database | SQLite |
| Data Processing | Pandas 3.0, NumPy 2.5 |
| Frontend | HTML5, Bootstrap 5, JavaScript |
| Visualization | Chart.js |
| PDF Export | ReportLab 5.0 |

## Dataset

The app uses the UCI Student Performance dataset — 1,044 records combining Mathematics (395) and Portuguese (649) student data.

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/taimoor-ahmad7/student-performance-dashboard.git
cd student-performance-dashboard

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install django pandas numpy reportlab pillow

# 4. Apply migrations
python manage.py migrate

# 5. Load student data
python manage.py load_students

# 6. Create admin user (optional)
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Open your browser and go to: `http://127.0.0.1:8000/`

## Project Structure

```
student-performance-dashboard/
├── core/               # Django project settings and URL routing
├── accounts/           # User registration, login, logout, profile
├── students/           # Student model, CRUD, search, filter, comparison
│   ├── data/           # student_data_merged.csv dataset
│   └── management/     # load_students management command
├── dashboard/          # Summary cards, charts, insight generation
├── reports/            # CSV and PDF export
└── templates/          # HTML templates (Bootstrap 5)
```

## Pages & URLs

| Page | URL |
|------|-----|
| Home | `/` |
| Register | `/accounts/register/` |
| Login | `/accounts/login/` |
| Student List | `/students/` |
| Student Comparison | `/students/compare/` |
| Dashboard | `/dashboard/` |
| Reports | `/reports/` |
