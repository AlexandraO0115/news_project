# News Application - Capstone Project

A Django-based news application designed to manage articles, user authentication, and subscriptions. This project includes a RESTful API for accessing content programmatically.

## Features

- **User Authentication:** Custom user model handling registration, login, and logout.
- **Article Management:** Backend support for news articles (via the `news` app).
- **REST API:** Endpoints built with Django REST Framework, including Token and Session authentication.
- **Subscription System:** Logic to filter articles based on subscriptions (via `SubscribedArticleViewSet`).
- **MySQL Database:** Integration for robust data storage.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python** (3.8 or higher recommended)
- **MySQL Server**
- **pip** (Python package installer)

## Installation & Setup

1.  **Clone the Repository**
    Clone this project to your local machine.

2.  **Create a Virtual Environment**
    It is recommended to run this project in a virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

    For development tools (formatting, linting):

    ```bash
    pip install -r requirements-dev.txt
    ```

4.  **Configure Environment Variables**
    This project uses `python-dotenv` to manage sensitive settings. Create a file named `.env` in the root directory (alongside `manage.py`) and add the following keys:

    ```ini
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=localhost
    DB_PORT=3306
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_email_app_password
    ```

5.  **Database Setup**
    - Create a MySQL database matching the `DB_NAME` in your `.env` file.
    - Run migrations to set up the schema:
        ```bash
        python manage.py migrate
        ```

6.  **Create a Superuser**
    To access the Django Admin interface:

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Server**
    Start the development server:
    ```bash
    python manage.py runserver
    ```

## API Documentation

The application exposes API endpoints under the `/api/` path.

- **Base API URL:** `/api/`
- **Subscribed Articles:** `/api/subscribed-articles/` - Returns articles based on the authenticated user's subscriptions.
