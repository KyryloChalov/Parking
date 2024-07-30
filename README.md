# Imagine Parking App

## Overview

This project is a REST API backend for a parking management system. It provides various endpoints for user
authentication, managing user profiles, handling parking sessions, payments, and more. Additionally, it includes a
health checker endpoint to ensure the database's functionality.

## Main Features

### User Authentication and Management

- **User Authentication**: Users can securely sign up, log in, and log out using JSON Web Token (JWT) authentication.
  The access token is blacklisted for the duration of its existence upon logout.
- **User Registration**: New users can register accounts with unique credentials. The first user in the system is always
  the administrator.
- **User Profile Management**: Users can update their profiles, including username, email, and password. They can also
  view and edit information about themselves through different routes.
- **Role-Based Access Control**: Operations are filtered based on user roles, allowing only authorized users to perform
  certain actions such as updating profiles or changing user roles. There are three roles: regular user, moderator, and
  administrator.
- **Password Management**: Users can reset and change their passwords.

### Role-Based Access Control

- **Fine-Grained Access Control**: Operations throughout the platform are filtered based on user roles, ensuring that
  only authorized users can perform specific actions.
- **Administrator Privileges**: Administrators have the highest level of access, allowing them to manage users,
  sessions, and payments.
- **Users Roles**: Roles include regular user (client), operator, and administrator, each with different levels of
  access and
  permissions.

### Vehicle Management

- **Vehicle Blacklist Management**:
    - Admins can add vehicles to a blacklist, preventing them from accessing parking spaces.
    - Admins can view a list of blacklisted vehicles and their information.
    - Admins can update blacklist entries for blacklisted vehicles.
- **Vehicle Reminder System**:
    - Admins can send email reminders to vehicle owners about upcoming parking session expirations.
    - Reminders are based on a configurable number of days before the session ends.
- **Vehicle Information Export**:
    - Admins can export parking data (including parking sessions, payments, and vehicle information) to a CSV file for a
      specified date range.
    - The exported data can be used for further analysis or record-keeping purposes.
- **Vehicle Abonement Status**:
    - Admins can view a list of vehicles with active parking abonement.

### Parking Management

- **Session Management**: Operator can create, update, and close parking sessions.
- **Payment Processing**: Operator can process payments for parking sessions, including checking for existing payments
  and
  calculating fees based on session durations and abonement statuses.
- **Export Parking Data**: Administrators can export parking session data.
- **View Parking Session Details**: Users can view details about their parking sessions.

### Rate Management

- **Create, Update, and Delete Rates**: Administrators can manage parking rates.
- **Retrieve Rate Information**: Users can view rate details.

### Settings Management

- **Create, Update, and Delete Settings**: Administrators can manage system settings.
- **Retrieve Settings**: Users can view system settings.

### Health Checker

- **Database Health Check**: An endpoint is available to check the health of the database connection.

### Security and Performance

- **Token-Based Authentication**: Authentication tokens are used to securely authenticate users and protect sensitive
  operations.
- **Rate Limiting**: Operations are rate-limited to prevent abuse and ensure fair usage of resources.
- **CORS Middleware**: Cross-Origin Resource Sharing (CORS) middleware is implemented to allow controlled access to
  resources from different origins, enhancing security.

## Installation and Deployment

This section contains the description of the different ways you can install and/or deploy the Imagine Parking
application.

### Options:

1. **Installation by Cloning Git Repository**
2. **Installation by Downloading and running [Docker Image](https://hub.docker.com/r/imagineteam/parkingapp) from Docker
   Hub**
3. **Run Already Deployed Application in a browser**

Detailed instructions for each option follow:

### Installation by Cloning Git Repository

**Prerequisites:**

- Python 3.10 or higher
- Docker
- PostgreSQL (available in the Docker container or cloud-based)
- Redis (available in the Docker container or cloud-based)
- Mail account with SMTP server for sending emails

**Steps:**

1. **Create `.env` File and Set Parameters**
    - Use `env.example` as a reference.

2. **Set Up PostgreSQL and Redis**
    - You can choose either option:
        - Use Docker Compose:

          ```bash
          docker compose --env-file .env up -d
          ```

        - Use your preferred cloud-based service for PostgreSQL and Redis.

3. **Clone the Repository**

   ```bash
   git clone https://github.com/KyryloChalov/Parking.git
   ```


4. **Install Dependencies**

   ```bash
   poetry install --no-root
   ```

5. **Activate Virtual Environment**

   ```bash
   poetry shell
   ```

6. **Apply Alembic Migrations**

   ```bash
   alembic upgrade heads
   ```

7. **Run the Application**

   ```bash
   uvicorn main:app --host localhost --port 8000 --reload
   ```

8. **Open Application in Browser**

   ```bash
   http://localhost:8000/docs/
   ```

## Installation by Downloading Docker Image

[Link](https://hub.docker.com/r/imagineteam/parkingapp) to the image in the Docker hub repository

**Prerequisites:**

- Docker
- PostgreSQL (available in the Docker container or cloud-based)
- Redis (available in the Docker container or cloud-based)
- Mail account with SMTP server for sending emails

**Steps:**

1. **Create `.env` File and Set Parameters**
    - Use `env.example` as a reference.

2. **Download Docker Image**

   ```bash
   docker pull imagineteam/parkingapp
   ```

3. **Start Docker Image**

   ```bash
   docker compose up -d
   
   docker run --env-file .env imagineteam/parkingapp
   ```

4. **Open Application in Browser**

   ```bash
   http://localhost:8000/docs/
   ```

## Run Already Deployed Application

The parkingapp will be also deployed to the web and accessible through links below in the near future (in progress)

## Technologies Used

![Language](https://img.shields.io/badge/Language-Python_3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.25-blue.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![Redis](https://img.shields.io/badge/Cache-Redis-blue.svg)
![Tensorflow](https://img.shields.io/badge/ML-Tensorflow-blue.svg)
![OpenCV](https://img.shields.io/badge/ComputerVision-OpenCV-blue.svg)
![DockerHub](https://img.shields.io/badge/Deploy-DockerHub-blue.svg)

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard
  Python type hints.
- **SQLAlchemy**: A powerful SQL toolkit and Object-Relational Mapping (ORM) library for Python applications.
- **PostgreSQL**: Powering and storing data. Feature-rich, open-source relational database management system (RDBMS)
  chosen for its reliability, scalability, and advanced data integrity features—hosted on elephantsql.com for a secure
  and managed cloud experience.
- **Redis**: An in-memory data structure store used as a cache for rate limiting and storing user sessions.Upstash.com
  provides a user-friendly and scalable Redis cloud solution.
- **uvicorn**: A lightning-fast ASGI server implementation, using uvloop and httptools.
- **Jinja2**: A full-featured template engine for Python, used for generating HTML templates.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **FastAPI Limiter**: A rate limiting extension for FastAPI applications using Redis.
- **CORS Middleware**: Cross-Origin Resource Sharing middleware for enabling CORS in FastAPI applications.
- **Tensorflow**: Used for machine learning tasks, such as vehicle license plate recognition.
- **OpenCV**: Used for computer vision tasks, such as license plate segmentation and recognition

## Team:

**Meet the Team!**

We're a passionate group of developers dedicated to building a powerful and user-friendly photo application. Here's how
you can connect with each team member:

* **Kyrylo Chalov** ([github.com/KyryloChalov](https://github.com/KyryloChalov))
* **Oleksandr** ([github.com/1Oleksandr](https://github.com/1Oleksandr))
* **Jurij Procenko** ([github.com/JurijProcenko](https://github.com/JurijProcenko))
* **Oleksiy M** ([github.com/OleksiyM](https://github.com/OleksiyM))

**Feel free to check out their profiles to learn more about their contributions to the project!**
