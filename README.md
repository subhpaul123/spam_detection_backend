# Phonebook Spam Detection API - README

This document provides instructions on how to run the Phonebook Spam Detection API and a brief overview of the project.

## Table of Contents

1. Prerequisites
2. Setup Instructions
    * Creating and Activating the Virtual Environment
    * Installing Dependencies
    * Database Setup
    * Applying Migrations
    * Generating Your Own DJANGO_SECRET_KEY
    * Populating the Database (for testing)
    * Running the Development Server
3. Testing the API with Postman
    * Registration
    * Authentication (Login)
    * Logout
    * User Profile
    * Contacts
    * Spam Reporting
    * Spam Likelihood
    * Search
    * User Details
    * Database Population (Development Only)
    * Get All Spam Numbers
    * Get Spam Number by Number
4. Project Overview
    * Functionality
    * Technology Stack
    * Data Models
    * Authentication
    * Error Handling
5. Further Considerations (Beyond the Scope)

## 1. Prerequisites

* Python: Version 3.8 or higher is recommended.
* pip: Python package installer (should come with Python).
* PostgreSQL: You need to have PostgreSQL installed and running.

## 2. Setup Instructions

### Creating and Activating the Virtual Environment

It's highly recommended to use a virtual environment to isolate project dependencies.

```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### Installing Dependencies

Install the required Python packages from the `requirements.txt` file:

```
pip install -r requirements.txt
```

### Database Setup

1.  Ensure your PostgreSQL server is running.
2.  Create a database named `spam_db` (or the name specified in `phonebook_api/settings.py`).
3.  Update the database configuration in `phonebook_api/settings.py` to match your PostgreSQL setup (username, password, host, port).

Python

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'spam_db',
        'USER': 'your_postgres_username',
        'PASSWORD': 'your_postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Applying Migrations

Apply Django migrations to create the database tables:

```
python manage.py migrate
```

### Generating Your Own `DJANGO_SECRET_KEY`

It is strongly recommended that you generate your own unique and strong secret key. Here are a few ways to do this:

**Using Python in the Terminal (Recommended):**

1.  Open your terminal.
2.  Run:
    ```
    python -c "import secrets; print(secrets.token_urlsafe(50))"
    ```
    or
    ```
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
    ```
    depending on how you invoke Python 3.

3.  Copy the output and use it as the value for your `DJANGO_SECRET_KEY` environment variable.

**Using Django's Management Command (After Installing Requirements):**

1.  Navigate to the root of the project in your terminal.
2.  Run:
    ```
    python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    ```
    or
    ```
    python3 manage.py shell -c "..."
    ```
3.  Copy the output and use it for your `DJANGO_SECRET_KEY`.

After generating a secret key, follow the instructions above to set it as an environment variable before running the Django development server.

### Populating the Database (for Testing)

Run the following command:
```
python manage.py populate_data
```

To specify the number of users, contacts per user, and spam reports, use:
```
python manage.py populate_data --users=100 --contacts-per-user=20 --spam-reports=500
```

**Note:** This database population can also be triggered via the API endpoint `POST /api/populate-test-data/` when the Django `DEBUG` setting in `phonebook_api/settings.py` is set to `True` and you are logged in with a valid authentication token. To use the API endpoint:

1.  Ensure your Django development server is running.
2.  Make a `POST` request to `http://127.0.0.1:8000/api/populate-test-data/` using an HTTP client like Postman.
3.  Include your authentication token in the `Authorization` header.

This will execute the same `populate_data` management command. Remember that this API endpoint should ideally only be enabled in development environments for security reasons.

### Running the Development Server

Start the Django development server:
```
python manage.py runserver

```

The API will now be accessible at `http://127.0.0.1:8000/api/`.

## 3. Testing the API with Postman

You can easily test the API endpoints using Postman. A pre-configured Postman workspace with the necessary collections and example requests is available at the following link:

[Backend API Postman Workspace](https://www.postman.com/subhpaul10/workspace/backend/collection/28620322-80cdbcdb-c9ee-46e9-befb-27302da13e64?action=share&creator=28620322)

**How to use the Postman Workspace:**

1.  Open Postman on your local machine.
2.  Click on the "Import" button.
3.  Choose the "Import From Link" option.
4.  Paste the provided workspace link into the text field.
5.  Click "Import".

Once imported, you will find a collection (or collections) containing pre-defined requests for each of the API endpoints. These requests will include:

* The correct HTTP method (GET, POST, PUT, DELETE).
* The API endpoint URLs.
* Example request bodies (for POST and PUT requests).
* Placeholders for authentication tokens where required.

**Using the Collection:**

1.  **Start the Django development server** as described in the "Running the Development Server" section.
2.  **Register a new user** using the `/api/register/` request in Postman to obtain your first authentication token.
3.  **Log in** using the `/api/login/` request with the registered credentials to get a valid authentication token.
4.  For all subsequent requests to protected endpoints, you will need to **replace the `YOUR_AUTH_TOKEN` placeholder** in the `Authorization` header with the actual token you received during login.
5.  Explore the different requests in the collection and send them to test the various functionalities of the API.

This Postman workspace should significantly simplify the process of exploring and testing the API endpoints.

4\. Project Overview
--------------------

### Functionality

This project implements a REST API designed to be consumed by a mobile application for spam detection and phone number lookup. Key functionalities include:

-   User registration and secure authentication.
-   Management of personal contacts for each registered user.
-   A global database concept encompassing registered users and their contacts.
-   Ability for users to report phone numbers as spam.
-   Search functionality by name and phone number across the global database, with specific ordering and result presentation rules.
-   Display of user details with conditional email visibility.
-   Calculation of spam likelihood for phone numbers.

### Technology Stack

-   Python: The primary programming language.
-   Django: A high-level Python web framework used for building the API.
-   Django REST Framework: A powerful toolkit for building Web APIs with Django.
-   PostgreSQL: The relational database used for data persistence.
-   Django ORM: Django's Object-Relational Mapper for interacting with the database.

### Data Models

-   `User`: Stores user information (name/username, phone number, email, password). The `phone_number` is unique.
-   `Contact`: Represents a personal contact belonging to a `User`, storing the contact's name and phone number.
-   `SpamReport`: Records instances of phone numbers being reported as spam by `Users`.

### Authentication

The API uses token-based authentication. Upon successful login, a unique token is generated and returned to the client. This token must be included in the `Authorization` header of subsequent requests to access protected endpoints.

### Error Handling

The API follows standard HTTP status codes to indicate the outcome of requests. Error responses are typically returned in JSON format with informative messages. Specific error handling is implemented for scenarios like invalid input, authentication failures, and duplicate spam reports.

```
Remember to replace the placeholder values (like `your_postgres_username`, `your_postgres_password`) with your actual information.
```