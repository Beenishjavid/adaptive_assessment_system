# Adaptive Assessment System

A modern web-based assessment platform for organizations that need to evaluate students, learners, and employees through adaptive online testing.

## Overview

The Adaptive Assessment System is designed to deliver a more intelligent assessment experience. Questions are not static for every user. Instead, the system adapts based on learner performance:

- Correct answer: difficulty increases from easy to medium to hard
- Incorrect answer: difficulty decreases from hard to medium to easy
- Progress and scores are tracked in real time throughout the assessment

This makes the platform suitable for academic testing, employee evaluation, and training programs.

## Key Features

### Adaptive Testing Engine

- Dynamic difficulty progression
- Question-level difficulty tagging
- Score tracking during the assessment
- Submission and result flow for learners
- Difficulty-based question filtering and management

### Administrator Dashboard

- Create, update, and manage questions
- Set difficulty for each question
- Review assessment content and results
- Manage quiz/question bank efficiently

### Student Portal

- Assessment flow with adaptive progression
- Clear progress indicators
- Score display after each response cycle
- Smooth submission process
- Role-based access and navigation

### Frontend and State Management

- React.js frontend
- Tailwind CSS styling
- Redux Toolkit state management
- Centralized assessment state for active questions and responses

## Tech Stack

### Frontend

- React.js
- JavaScript
- Tailwind CSS
- Redux Toolkit
- React Redux
- React Router

### Backend

- Python
- Django
- Django REST Framework
- SQL database support

## Project Structure

```text
adaptive_assesement/
├── backend/
│   ├── apps/
│   │   ├── authentication/
│   │   ├── groups/
│   │   ├── notifications/
│   │   ├── organizations/
│   │   ├── proctoring/
│   │   ├── quizzes/
│   │   └── results/
│   ├── smart_quiz_system/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── e2e/
│   ├── tests/
│   └── playwright.config.js
├── database/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Backend Notes

The backend includes Django models and APIs for quiz and question management. Questions now support a `difficulty` field with the following values:

- `easy`
- `medium`
- `hard`

The default value is `medium`.

Relevant endpoints include:

- GET /api/quizzes/api/questions/
- GET /api/quizzes/api/admin/questions/
- POST /api/quizzes/api/admin/questions/
- PUT /api/quizzes/api/admin/questions/
- DELETE /api/quizzes/api/admin/questions/

These endpoints allow administrators to filter questions by difficulty and manage the assessment question bank.

## Frontend Notes

The frontend includes:

- Redux store and assessment slice for managing state
- adaptive student assessment page
- admin dashboard for question creation and review
- Tailwind-based styling for a clean, responsive interface

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- A database compatible with Django such as PostgreSQL or SQL Server

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Application URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## E2E Testing

A basic Playwright setup has been added under the `e2e` folder to cover the main flows:

- admin question creation
- student assessment flow

Run it with:

```bash
cd frontend
npm run e2e
```

## Development Summary

This project was refactored from a general quiz platform into a dedicated Adaptive Assessment System with:

- adaptive question difficulty logic
- Django question management APIs
- Redux Toolkit state management
- adaptive student assessment experience
- admin dashboard for question management
- updated documentation and repo branding
