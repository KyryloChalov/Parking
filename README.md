# Imagine Parking app

## Overview

This project is a REST API backend for ______. It provides various endpoints for
user authentication, managing user profiles, _____, as
well as a health checker endpoint to ensure the database's functionality.

## Main Features

### User Authentication and Management

- **User Authentication**: Users can securely sign up, log in, and log out using JSON Web Token (JWT) authentication.
  The access token is blacklisted for the duration of its existence upon logout.
- **User Registration**: New users can register accounts with unique credentials. The first user in the system is always
  the administrator.
- **User Profile Management**: Users can update their profiles, including username, email, and password. They can also
  view and edit information about themselves through different routes.
- **Role-Based Access Control**: Operations are filtered based on user roles, allowing only authorized users to perform
  certain actions such as updating profiles or changing user roles. There are three roles: a regular user, a moderator,
  and an administrator.

### Role-Based Access Control

- **Fine-Grained Access Control**: Operations throughout the platform are filtered based on user roles, ensuring that
  only authorized users can perform specific actions.
- **Administrator Privileges**: _________
- **Users Roles**: ________

### Health Checker

- **Database Health Check**: An endpoint is available to check the health of the database connection.

### Security and Performance

- **Token-Based Authentication**: Authentication tokens are used to securely authenticate users and protect sensitive
  operations.
- **Rate Limiting**: Operations are rate-limited to prevent abuse and ensure fair usage of resources.
- **CORS Middleware**: Cross-Origin Resource Sharing (CORS) middleware is implemented to allow controlled access to
  resources from different origins, enhancing security.

## Installation and Deployment

This section contains the description of the different ways you can install and/or deploy the Image application.

**Options:**

1. **Installation by Cloning Git Repository**
2. **Installation by Downloading and running [Docker Image](https://hub.docker.com/r/imagineteam/parkingapp) from
   dockerhub**
3. **Run Already Deployed Application in a browser**

Detailed instructions for each option follow:

## Installation by Cloning Git Repository

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
   You can choose either option:
    - Use Docker Compose:

      ```bash
      docker compose --env-file .env up -d
      ```

      (You can modify `docker-compose.yml` to set additional variables.)

    - Use your preferred cloud-based service for PostgreSQL and Redis.

3. **Clone the Repository**


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
   docker run --env-file .env imagineteam/parkingapp
   ```

4. **Open Application in Browser**

   ```bash
   http://localhost:8000/docs/
   ```

## Run Already Deployed Application

The parkingapp is also deployed to the web and accessible through links below

**Deployed from Main Branch on GitHub (Automated Deployment using CI/CD)**

- Index Page:
  ```
  https://________koyeb.app
  ```

- Swagger Documentation:
  ```
  https://________koyeb.app/docs
  ```

**Deployed Pre-built Docker Image (Backup Link)**

  ```
  https://_______oleksiy.koyeb.app/docs
  ```

## Technologies Used

![Language](https://img.shields.io/badge/Language-Python_3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.25-blue.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![Redis](https://img.shields.io/badge/Cache-Redis-blue.svg)
![Tensorflow](https://img.shields.io/badge/ML-Tensorflow-blue.svg)
![OpenCV](https://img.shields.io/badge/ComputerVision-OpenCV-blue.svg)
![Koyeb](https://img.shields.io/badge/Deploy-Koyeb-blue.svg)
![DockeHub](https://img.shields.io/badge/Deploy-DockeHub-blue.svg)

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
- **Tensorflow**: ________
- **OpenCV**: ________

## Team:

**Meet the Team!**

We're a passionate group of developers dedicated to building a powerful and user-friendly photo application. Here's how
you can connect with each team member:

* **Kyrylo Chalov** ([github.com/KyryloChalov](https://github.com/KyryloChalov))
* **Oleksandr** ([github.com/1Oleksandr](https://github.com/1Oleksandr))
* **Jurij Procenko** ([github.com/JurijProcenko](https://github.com/JurijProcenko))
* **Oleksiy M** ([github.com/OleksiyM](https://github.com/OleksiyM))

**Feel free to check out their profiles to learn more about their contributions to the project!**
