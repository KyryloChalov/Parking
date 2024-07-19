# Imagine photo app

## Overview

This project is a REST API backend for an image sharing platform. It provides various endpoints for
user authentication, managing user profiles, uploading and managing photos, adding comments and ratings to photos, as
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

### Photo Management

- **Upload Photos**: Users can upload images with descriptions to the platform, which are stored and managed securely.
  They can add up to 5 tags to a photo.
- **View All Photos**: All users can view a list of all uploaded photos on the platform.
- **View Photo Details**: Users can view detailed information about each photo, including its title, description, upload
  date, and unique link.
- **Delete Own Photos**: Users can delete their own photos from the platform.
- **Edit Photo Descriptions**: Users can edit the description of a photo.
- **Photo Transformations**: Users can perform basic operations on photos enabled by the Cloudinary service. They can
  create a link to the transformed image to view the photo in the form of a URL and a QR code. The created links are
  stored on the server.
- **Administrator Privileges**: Administrators can do all CRUD operations with users photos.

### Comments

- **Add Comments**: Users can add comments to photos, sharing their thoughts or feedback.
- **View Comments**: All users can view comments on each photo.

### Ratings

- **Rate Photos**: Users can rate a photo from 1 to 5 stars. The rating is calculated as the average of the ratings of
  all users. Users can rate a photo only once and cannot rate their own photos.
- **View Average Ratings**: All users can see the average rating for each photo, helping them discover popular or
  high-quality content.
- **Moderator and Administrator Privileges**: Moderators and administrators can view and delete user ratings.

### Role-Based Access Control

- **Fine-Grained Access Control**: Operations throughout the platform are filtered based on user roles, ensuring that
  only authorized users can perform specific actions.
- **Administrator Privileges**: Administrators have elevated privileges, enabling them to manage users, photos,
  comments, and ratings effectively. They can also make users inactive (ban). Inactive users cannot enter the
  application.
- **Moderator Roles**: Moderators have limited administrative privileges, allowing them to perform certain
  administrative tasks such as managing comments or ratings.

### Search and Filtering

- **Photo Search**: Users can search for photos by keyword or tag. After searching, users can filter the results by
  rating or date of addition.
- **Moderator and Administrator Privileges**: Moderators and administrators can search and filter by users who have
  added photos.

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
2. **Installation by Downloading and running [Docker Image](https://hub.docker.com/r/imagineteam/imageapp) from
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
- Cloudinary account for storing and editing photos

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

[Link](https://hub.docker.com/r/imagineteam/imageapp) to the image in the Docker hub repository

**Prerequisites:**

- Docker
- PostgreSQL (available in the Docker container or cloud-based)
- Redis (available in the Docker container or cloud-based)
- Mail account with SMTP server for sending emails
- Cloudinary account for storing and editing photos

**Steps:**

1. **Create `.env` File and Set Parameters**
    - Use `env.example` as a reference.

2. **Download Docker Image**

   ```bash
   docker pull imagineteam/imageapp
   ```

3. **Start Docker Image**

   ```bash
   docker run --env-file .env imagineteam/imageapp
   ```

4. **Open Application in Browser**

   ```bash
   http://localhost:8000/docs/
   ```

## Run Already Deployed Application

The ImageApp is also deployed to the web and accessible through links below

**Deployed from Main Branch on GitHub (Automated Deployment using CI/CD)**

- Index Page:
  ```
  https://imagine-kyrylo.koyeb.app
  ```

- Swagger Documentation:
  ```
  https://imagine-kyrylo.koyeb.app/docs
  ```

**Deployed Pre-built Docker Image (Backup Link)**

  ```
  https://image-app-oleksiy.koyeb.app/docs
  ```

## Technologies Used

![Language](https://img.shields.io/badge/Language-Python_3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.25-blue.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![Redis](https://img.shields.io/badge/Cache-Redis-blue.svg)
![Cloudinaty](https://img.shields.io/badge/Photo_Storage-Cloudinary-blue.svg)
![Redis](https://img.shields.io/badge/Deploy-Koyeb-blue.svg)

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard
  Python type hints.
- **SQLAlchemy**: A powerful SQL toolkit and Object-Relational Mapping (ORM) library for Python applications.
- **PostgreSQL**: Powering and storing data. Feature-rich, open-source relational database management system (RDBMS)
  chosen for its reliability, scalability, and advanced data integrity features—hosted on elephantsql.com for a secure
  and managed cloud experience.
- **Redis**: An in-memory data structure store used as a cache for rate limiting and storing user sessions.Upstash.com
  provides a user-friendly and scalable Redis cloud solution.
- **Cloudinary**: A cloud-based image and video management solution for uploading, storing, managing, and delivering
  images and videos for websites and apps.
- **uvicorn**: A lightning-fast ASGI server implementation, using uvloop and httptools.
- **Jinja2**: A full-featured template engine for Python, used for generating HTML templates.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **FastAPI Limiter**: A rate limiting extension for FastAPI applications using Redis.
- **CORS Middleware**: Cross-Origin Resource Sharing middleware for enabling CORS in FastAPI applications.

## Team:

**Meet the ImageApp Team!**

We're a passionate group of developers dedicated to building a powerful and user-friendly photo application. Here's how
you can connect with each team member:

* **Kyrylo Chalov** ([github.com/KyryloChalov](https://github.com/KyryloChalov))
* **Oleksandr** ([github.com/1Oleksandr](https://github.com/1Oleksandr))
* **Jurij Procenko** ([github.com/JurijProcenko](https://github.com/JurijProcenko))
* **UreshiiSushi** ([github.com/UreshiiSushi](https://github.com/UreshiiSushi))
* **Oleksiy M** ([github.com/OleksiyM](https://github.com/OleksiyM))

**Feel free to check out their profiles to learn more about their contributions to the project!**
