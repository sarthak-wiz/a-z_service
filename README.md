# A-Z Household Services Platform

A web application built with Flask that connects customers with household service professionals. The platform facilitates service bookings, professional verification, and service management.

## Features

### User Roles

- **Admin**: Manage services, approve professionals, and monitor platform activity
- **Service Professional**: Accept/reject service requests, manage service delivery
- **Customer**: Browse services, create service requests, and track service status

### Core Functionalities

- User authentication with role-based access control
- Service management (CRUD operations)
- Service request lifecycle management
- Professional verification system
- Dashboard for each user role

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone & Navigate**

```bash
git clone <repository-url>
cd A-Z Household Services
```

2.**Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3.**Install Dependencies**

```bash
pip install -r requirements.txt
```

4.**Environment Configuration**

Create `.env` file in the root directory:

```bash
SECRET_KEY=your_secret_key_here
FLASK_APP=app.py
FLASK_ENV=development
```

5.**Initialize Database**

```bash
python recreate_db.py
```

6.**Run Application**

```bash
flask run
```

Visit `http://localhost:5000` in your browser.

## Test Accounts

| Role         | Username  | Password    |
|-------------|-----------|-------------|
| Admin       | admin     | admin123    |
| Professional| pro1      | password123 |
| Customer    | customer1 | password123 |

## Core Features

- 🔐 Role-based authentication
- 📊 Service management
- 🔄 Request lifecycle tracking
- ✅ Professional verification
- 📱 Role-specific dashboards

## Tech Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite + SQLAlchemy
- **Frontend**: Bootstrap 4
- **Authentication**: Flask-Login

## Project Structure

household-services/
├── app/
│   ├── views/
│   ├── templates/
│   └── static/
├── requirements.txt
├── config.py
└── app.py

---
Made with ⚡ by Sarthak Jain | 23F3000839
