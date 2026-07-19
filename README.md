# SmartHire – Job Application Tracker & Resume Keyword Matcher

SmartHire is a premium, feature-rich HR-Tech SaaS application designed to help job seekers track their active job applications and evaluate resume relevancy against job descriptions using automated AI keyword extraction.

---

## 🚀 Features

- **Personal Dashboard**: View key pipeline metrics and manage applications on a spacious full-width tracker interface.
- **Visual Analytics Center**: A dedicated reports page displaying pipeline distribution doughnut charts (powered by Chart.js) and custom status cards.
- **MongoDB CRUD**: Direct, high-performance NoSQL operations (using `pymongo` cursors) to manage tracked applications.
- **AI Resume Matching**: Upload text resumes to automatically check match scores using regular expressions (`re` module) to extract and compare skills.
- **Multithreaded Follow-up Scheduler**: Spin up background worker threads to scan and alert upcoming follow-up deadlines without blocking the user response.
- **Django REST Framework APIs**: Secured JSON API endpoints for mobile or external developer integrations.
- **Horizontal Navigation Layout**: A modern top navigation menu expanding the workspace to 100% viewport width.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 5.0+, Django REST Framework (DRF)
- **Database**: MongoDB (via `pymongo` for application data), SQLite (for user session authentication)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript (ES6)

---

## ⚙️ Step-by-Step Local Setup Guide

Follow these steps to run SmartHire on your local machine:

### Step 1: Install Required Software
Ensure you have the following installed:
1. **Python (v3.12+)**: Download from [python.org](https://www.python.org/downloads/).
2. **MongoDB Community Server**: Download from [mongodb.com](https://www.mongodb.com/try/download/community) (Make sure it runs as a service on port `27017`).
3. **MongoDB Compass (Visual GUI)**: Download from [mongodb.com/products/tools/compass](https://www.mongodb.com/products/tools/compass) to inspect your NoSQL data.

### Step 2: Open Terminal & Navigate to Project Directory
Open your Command Prompt or PowerShell and go to the project directory:
```bash
cd C:\Users\Khushi\.gemini\antigravity\scratch\smarthire
```

### Step 3: Activate the Virtual Environment
Activate the pre-configured virtual environment:
```powershell
# In Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### Step 4: Run SQLite Database Migrations
Initialize Django's user session storage system:
```bash
python manage.py migrate
```

### Step 5: Start the Development Server
Run the local server:
```bash
python manage.py runserver
```
Your server will start running at **http://127.0.0.1:8000/**. Open **http://127.0.0.1:8000/analytics/** to view graphical pipeline distribution reports.

---

## 📂 REST API Endpoints (Django REST Framework)

All API requests are scoped to the authenticated user. Pass credentials or run requests within an active session.

- **List & Create Applications**:
  - `GET /api/applications/` - List all applications owned by the user.
  - `POST /api/applications/` - Create a new application document.
- **Retrieve, Update, Delete & Analyze**:
  - `GET /api/applications/<app_id>/` - Retrieve a specific application by its ID.
  - `PUT /api/applications/<app_id>/` - Update fields of an application.
  - `DELETE /api/applications/<app_id>/` - Permanently remove an application.
  - `POST /api/applications/<app_id>/analyze/` - Upload and parse a resume file against this application.

---

## 🎥 Demo Preview Section

Below is a placeholder for the user walkthrough visualization:

![SmartHire Walkthrough](https://raw.githubusercontent.com/placeholder-images/smarthire-demo.gif)
