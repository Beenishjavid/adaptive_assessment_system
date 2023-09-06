# Adaptive Assessment System

An online assessment platform where instructors build quizzes, students take them under timed conditions, and administrators oversee users, organizations and reporting. It pairs a Django REST API with a React single-page app.

## What it does

**For students**
- Browse available and practice quizzes, or search by topic
- Take timed quizzes with automatic submission when time runs out
- Review scores and detailed results for every attempt

**For instructors**
- Create, edit, preview and delete quizzes
- Organize learners into groups
- See attempt history and per-quiz result analytics

**For administrators**
- Manage users and approve instructor accounts
- Manage organizations and system settings
- View platform-wide reports and charts

**Platform**
- JWT-based login with role-aware routing (admin, instructor, student)
- Sign-up plus forgot/reset-password flow
- Proctoring and notification modules on the backend

## Technology

| Layer | Tools |
|---|---|
| Frontend | React 18, React Router 6, React Query, Axios, Tailwind CSS, Chart.js / Recharts, React Hook Form |
| Backend | Python, Django 4.2, Django REST Framework, Simple JWT, django-cors-headers |
| Data | SQLite for local development, Microsoft SQL Server for deployment |
| Background jobs | Celery with Redis (optional) |

## Repository layout

```text
adaptive_assessment_system/
├── backend/
│   ├── apps/
│   │   ├── authentication/   # users, profiles, login, roles
│   │   ├── organizations/
│   │   ├── groups/
│   │   ├── quizzes/          # quizzes, questions, attempts
│   │   ├── results/
│   │   ├── proctoring/
│   │   └── notifications/
│   ├── smart_quiz_system/    # Django settings and root URLs
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── context/          # auth state
│       ├── pages/            # student, instructor and admin screens
│       └── services/         # API clients
├── database/                 # SQL Server schema scripts
└── LICENSE
```

## Running locally

You need **Python 3.11–3.13** and **Node.js 18+**.

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.demo .env                 # uses SQLite, no database server needed
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API runs at http://localhost:8000.

> On macOS and Linux, `mssql-django` and `pyodbc` need the Microsoft ODBC driver. If you only use SQLite you can skip those two packages.

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

The app opens at http://localhost:3000.

### Using SQL Server

Copy `.env.example` to `.env` (leave out `USE_SQLITE`) and fill in `DATABASE_HOST`, `DATABASE_NAME`, `DATABASE_USER` and `DATABASE_PASSWORD`. Schema scripts are in [database/](database/).

## API overview

All endpoints are under `/api/`.

| Prefix | Purpose |
|---|---|
| `/api/auth/` | Login, registration, token refresh, password reset |
| `/api/quizzes/` | Quiz CRUD, starting attempts, submitting answers, results |
| `/api/results/` | Student results and history |
| `/api/groups/` | Learner groups |
| `/api/organizations/` | Organization management |
| `/api/proctoring/` | Proctoring events |
| `/api/notifications/` | User notifications |
| `/api/admin/` | Administrator dashboards and management |

## Roadmap

- Adaptive question difficulty: move learners between easy, medium and hard questions based on their answers
- Automated end-to-end tests for the main student and instructor flows

## License

Released under the [MIT License](LICENSE).
