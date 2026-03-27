# News Project

Welcome to the News Project! This is a web application built using the Django framework. This guide will help you set up the project on your local machine, even if you are new to web development.

---

## Prerequisites

Before you begin, ensure you have the following installed on your computer:

- **Python 3.12 or higher**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **pip** (Python package installer): [Install pip](https://pip.pypa.io/en/stable/installing/)

---

## Getting Started

Follow these steps exactly to get the project running.

### 1. Clone the Project

Open your terminal or command prompt and run:

```bash
git clone https://github.com/AlexandraO0115/news_project.git
cd news_project
```

### 2. Create a Virtual Environment

A virtual environment keeps the project's tools separate from your other computer settings.

**Windows (PowerShell):**

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Requirements

Install all the necessary software libraries required for this project:

```bash
pip install -r requirements.txt
```

For development tools (formatting, linting):

```bash
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

The project needs a `.env` file to store secret information like your database password and security keys.

1. Look inside the `news_project` folder for a file named `.env.example`.
2. Create a copy of that file and rename the copy to exactly `.env`.

**Windows (Command Prompt):**

```cmd
copy news_project\.env.example news_project\.env
```

**macOS/Linux or PowerShell:**

```bash
cp news_project/.env.example news_project/.env
```

3. Open the new `.env` file in a text editor and fill in the following details:

#### Basic Settings

- `SECRET_KEY`: Enter a securely generated string (see instructions below).
- `DEBUG`: Set to `True` for development.
- `ALLOWED_HOSTS`: Set to `127.0.0.1,localhost`

#### Database Settings (Required if using MySQL)

- `DB_NAME`: The name of your database (e.g., `news_db`)
- `DB_USER`: Your database username (e.g., `root`)
- `DB_PASSWORD`: Your database password
- `DB_HOST`: The server address (usually `127.0.0.1`)
- `DB_PORT`: The connection port (usually `3306`)

_(If you are using the default SQLite, you can leave the Database settings blank.)_

#### Email Settings (Required for sending emails/notifications)

- `EMAIL_HOST`: The SMTP server address (e.g., `smtp.gmail.com`).
- `EMAIL_PORT`: The port (usually `587` for TLS).
- `EMAIL_USE_TLS`: Set to `True` to enable secure connection.
- `EMAIL_HOST_USER`: Your full email address.
- `EMAIL_HOST_PASSWORD`: Your email password or a service-specific **App Password**.

---

### Detailed Configuration Guides

#### Generating a Django Secret Key

Your Django `SECRET_KEY` is used for cryptographic signing and should be set to a unique, unpredictable value. **Never share your production secret key or commit it to version control.**

To generate a secure key for your local `.env` file, ensure your virtual environment is activated and run the following command in your terminal:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy only the string inside the quotes and paste it into your `.env` file as the value for `SECRET_KEY`.

#### Setting up the Email Configuration

To send emails from this application, you must configure the email variables in your `.env` file. If you are using a standard email provider like Gmail, Outlook, or Yahoo, you cannot use your regular account password. Instead, you must generate an **App Password**.

_Note: Your email account must have Two-Factor Authentication (2FA) / 2-Step Verification enabled to generate an app password._

**Gmail**

1. Go to your Google Account.
2. Select **Security** from the left navigation panel.
3. Under "How you sign in to Google," ensure **2-Step Verification** is turned on.
4. Search for **App passwords** in the search bar at the top of the account page.
5. Create a new app password (you can name it something like "Django App").
6. Click **Generate**.
7. Copy the 16-character code (without spaces) and paste it into your `.env` file as `EMAIL_HOST_PASSWORD`.

**Microsoft (Outlook / Hotmail)**

1. Go to your Microsoft Account Security page and sign in.
2. Click on **Advanced security options**.
3. Ensure **Two-step verification** is turned on.
4. Scroll down to the **App passwords** section and click **Create a new app password**.
5. Copy the generated password into your `.env` file as `EMAIL_HOST_PASSWORD`.

**Yahoo**

1. Go to your Yahoo Account Security page.
2. Scroll down to **Other ways to sign in** and click on **Generate and manage app passwords**.
3. Enter a custom name for the app (e.g., "Django Project") and click **Generate password**.
4. Copy the generated password into your `.env` file as `EMAIL_HOST_PASSWORD`.

---

### 5. Create and Setup the Database

Before the application can save data, the database itself must exist.

#### Option A: Using SQLite (Recommended for beginners)

If you are using the default SQLite settings, you do **not** need to create a database file manually. Django will create it for you in the next step.

#### Option B: Using MySQL

If you have configured your `.env` file to use MySQL, you must create the database first. Open your MySQL terminal or a tool like MySQL Workbench and run:

```sql
CREATE DATABASE news_db;
```

_(Make sure the name `news_db` matches the `DB_NAME` value you put in your `.env` file.)_

#### Apply Migrations

Once the database exists (or if using SQLite), run this command to create the necessary tables:

```bash
python manage.py migrate
```

### 6. Create an Admin User

To access the "behind-the-scenes" area of the website, you need an administrator account:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter a username, email, and password. (Note: The password will not show characters while you type—this is normal!)

### 7. Run the Server

You are ready to go! Start the development server:

```bash
python manage.py runserver
```

### 8. Running with Docker

This application includes a Dockerfile for easy deployment and local testing in an isolated environment.

#### 1. Update your .env for Docker

The Docker container is its own isolated network. To connect to a database running on your host machine:

- **Windows/Mac:** Change `DB_HOST=127.0.0.1` to `DB_HOST=host.docker.internal` in your `.env` file.
- **Linux:** Use your `docker0` IP address (usually `172.17.0.1`).

#### 2. Build the Docker Image

In your project root (where the Dockerfile is located), run:

```bash
docker build -t news-project-app .
```

#### 3. Start the Container

Since the project uses python-dotenv, the container will automatically load your variables from the .env file copied during the build:

```bash
docker run -p 8000:8000 news-project-app
```

#### 4. Database Setup (Migrations)

If this is your first time running the project or if you have new model changes, run the migrations inside the running container:

1. **Find the Container ID:**

    ```bash
    docker ps
    ```

2. **Run Migrations:**

    ```bash
    docker exec -it <CONTAINER_ID> python manage.py migrate
    ```

---

## Viewing the Project

- **The Website:** Open your browser and go to http://127.0.0.1:8000/
- **The Admin Panel:** Go to http://127.0.0.1:8000/admin/ and log in with the superuser account you created in step 6.

---

## Development Tools

If you plan on contributing to the code, you can use the tools installed from `requirements-dev.txt` to ensure your code follows standard conventions. (Note: Your code editor may respect the included `.editorconfig` file automatically).

### Python Code

- **Formatting:** We use [Black](https://black.readthedocs.io/). Run `black .` to automatically format your Python files.
- **Linting:** We use [Flake8](https://flake8.pycqa.org/). Run `flake8 .` to check for style errors and potential bugs.

### Django Templates & Frontend

- **HTML Templates:** We use [djlint](https://www.djlint.com/) for Django HTML templates. Run `djlint . --reformat` to format them, or `djlint . --lint` to check for issues.
- **CSS / JS:** You can format stylesheets and scripts using the included `cssbeautifier` and `jsbeautifier` CLI tools.

---

## Troubleshooting

- **Virtual Environment:** If you close your terminal, you must run the "Activate" command (Step 2) again before running the server.
- **Python Command:** If `python` doesn't work, try using `python3` instead.
- **Missing .env:** If you get a "Secret Key" error, double-check that your `.env` file is named correctly and located inside the `news_project` folder.

---

## API Documentation

The application exposes API endpoints under the `/api/` path.

- **Base API URL:** `/api/`
- **Subscribed Articles:** `/api/subscribed-articles/` - Returns articles based on the authenticated user's subscriptions.
