# SmartTrade Platform

SmartTrade is a Django-based web application that combines user management, subscription plans, real-time messaging, financial reporting, and a PQRS (Petitions, Complaints, Claims, and Suggestions) management system. The platform includes a WebSocket-powered advisory chat and a financial analytics module based on historical Ecopetrol stock market data.

---

# Overview

The project is organized into the following main modules:

- **backend/** – Django project configuration (settings, URLs, ASGI, WSGI).
- **usuarios/** – User management, authentication, subscription plans, financial reports, and PQRS.
- **chat/** – Real-time communication between Gold plan users and financial advisors.
- **pqrs/** – Independent PQRS management module.
- **static/** – CSS, JavaScript, images, and financial datasets.

---

# Project Structure

## Root Directory

- `requirements.txt` – Python project dependencies.
- `.gitignore` – Files and folders ignored by Git.
- `manage.py` – Django management script.

---

## Backend

### `backend/settings.py`

Main project configuration including:

- Installed applications (`usuarios`, `chat`, `pqrs`, `channels`, etc.).
- MySQL database configuration using **django-environ**.
- Environment variables loaded from `.env`.
- WhiteNoise configuration for static files.
- Django Channels configuration for WebSockets.
- Static files configuration.

---

### `backend/urls.py`

Main URL routing for:

- User module
- Chat module
- PQRS module
- Django administration panel
- Login page redirection

---

### `backend/asgi.py`

ASGI configuration used to support both HTTP requests and WebSocket communication through Django Channels.

---

### `backend/wsgi.py`

Standard WSGI entry point for production deployments.

---

# Applications

## Users Module (`usuarios`)

Responsible for authentication, user profiles, subscription plans, financial reports, and account management.

### Models

- **Plan** – Subscription plans (Basic, Premium, Gold).
- **Profile** – Stores additional user information and selected subscription plan.
- **PQRS** – User petitions, complaints, claims, and suggestions.

### Main Views

- Home page
- User login/logout
- User registration
- Subscription plans
- User profile
- Change subscription plan
- Change email
- PQRS submission
- Financial reports
- Landing page

### Financial Reports

The reporting module generates financial metrics using CSV datasets, including:

- Predicted stock prices
- Historical market information
- Technical indicators
- Market analysis

### Graph Module

`views_graph.py` generates financial charts using:

- Pandas
- Matplotlib
- Seaborn

Generated images are stored in:

```
usuarios/static/img/
```

---

## Chat Module (`chat`)

Real-time messaging system between Gold users and financial advisors.

### Models

- **Conversation**
- **AdvisorMessage**

### Features

- Gold user chat room
- Advisor dashboard
- Conversation history
- AJAX message retrieval
- Role-based access control

### WebSocket Consumer

`ChatAdvisorConsumer`

Handles:

- Client connections
- Message broadcasting
- Database persistence
- Real-time communication

Implemented using **Django Channels** and **WebSockets**.

---

## PQRS Module (`pqrs`)

Independent module for handling customer requests.

### Models

Stores:

- Name
- Email
- Message
- Submission date

### Views

- PQRS Form
- Success page

---

# Static Resources

The application includes:

- CSS styles
- JavaScript
- Images
- Historical stock market datasets
- Predicted market data

Main datasets:

- `predicciones_finales.csv`
- `Ecopetrol_unificado_limpio.csv`

---

# Main Technologies

### Backend

- Python
- Django
- Django ORM
- Django Channels
- WhiteNoise

### Database

- MySQL

### Frontend

- HTML5
- CSS3
- JavaScript

### Data Analysis

- Pandas
- Matplotlib
- Seaborn

---

# Dependencies

Main libraries used:

- Django 5.2.7
- Channels 4.3.1
- django-environ 0.12.0
- WhiteNoise 6.11.0
- mysqlclient 2.2.7
- pandas 2.3.3
- matplotlib 3.10.7
- seaborn 0.13.2

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/vanesita1524/smarttrade-platform.git
```

## 2. Navigate to the project directory

```bash
cd smarttrade-platform
```

## 3. Create a virtual environment

```bash
python -m venv venv
```

## 4. Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure environment variables

Create a `.env` file containing:

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

## 7. Run migrations

```bash
python manage.py migrate
```

## 8. Create an administrator

```bash
python manage.py createsuperuser
```

## 9. Start the development server

```bash
python manage.py runserver
```

---

# Important Notes

- Database credentials are not included in the repository.
- WebSocket communication uses Django Channels with `InMemoryChannelLayer` for development.
- Financial reports are generated from local CSV datasets.
- User permissions are managed through Django Groups, distinguishing regular users from financial advisors.

---

# Future Improvements

- Redis integration for production WebSocket support.
- Cloud deployment.
- Multi-stock prediction support.
- Portfolio management.
- Real-time notifications.
- Improved predictive models.

---

#User dashborad
<img width="780" height="569" alt="image" src="https://github.com/user-attachments/assets/8fec0b66-e2a1-4957-8381-dca7de30fc66" />
<img width="919" height="497" alt="image" src="https://github.com/user-attachments/assets/aba01868-53a6-40d3-901b-7ac4a262a544" />
<img width="324" height="393" alt="image" src="https://github.com/user-attachments/assets/3d0b4840-7988-4783-b372-1d4b1a4f2a84" />

---
#home page
<img width="1362" height="617" alt="image" src="https://github.com/user-attachments/assets/84ae65ce-bbc5-4b45-837a-38fdeb8e359b" />
<img width="1343" height="632" alt="image" src="https://github.com/user-attachments/assets/8697f385-b9fc-47ca-8229-a621393519b7" />
---
#plans
<img width="1092" height="623" alt="image" src="https://github.com/user-attachments/assets/969f2efc-8cbe-4938-a556-65176b116fe5" />
---
#PQRS
<img width="1036" height="626" alt="image" src="https://github.com/user-attachments/assets/07b7ecb8-dfef-4c90-bf45-a5bc1dc78146" />
<img width="639" height="387" alt="image" src="https://github.com/user-attachments/assets/44576e18-a91b-41d2-ac0a-3786a8c51491" />
---
#Reports
<img width="918" height="560" alt="image" src="https://github.com/user-attachments/assets/8b76dc91-ab80-4d7e-94a0-14d6d3c651a5" />
<img width="910" height="607" alt="image" src="https://github.com/user-attachments/assets/3795e430-4987-4804-96af-41648e9286cf" />

---
#chat
<img width="1365" height="483" alt="image" src="https://github.com/user-attachments/assets/0650e194-82f3-48e3-a3bb-5a0ec67abe9d" />
<img width="1362" height="362" alt="image" src="https://github.com/user-attachments/assets/8b626994-ab80-47e7-be0a-e70380ab327a" />






