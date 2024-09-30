## Description
**Title**:

Development of a Restaurant Vote API Server

**Objective**:

Company needs internal service for its’ employees which helps them to make a decision
on lunch place.

Each restaurant will be uploading menus using the system every day over API
Employees will vote for menu before leaving for lunch on mobile app for whom backend has to be implemented
There are users which did not update app to the latest version and backend has to support both versions.
Mobile app always sends build version in headers.

## Features
- Authentication
- Creating restaurant
- Uploading menu for restaurant (There should be a menu for each day)
- Creating employee
- Getting current day menu
- Voting for restaurant menu (Old version api accepted one menu, New one accepts top three menus with respective points (1 to 3)
- Getting results for current day


## What we are using
    Language: Python 3.10
    Backend : Django Rest Framework 2.2.0
    Database : PostreSQL 14
    Linting tool: Ruff
    Static Type checking tool: Mypy
    Containerization: Docker, Docker-Compose
    API Testing tool: Postman
    API Documentation: Swagger
    VCS: Git, pre-commit hooks



## Development
1. Install Docker, Docker Compose
2. Create venv for this project.
3. Install packages for production and also for development.
    ```commandline
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
   ```
4. Add custom pre commit hooks for linting and static type checking(ruff, mypy)
    ```commandline
    pre-commit install
    ```
5. Check static type check
    ```commandline
    mypy .
    ```
## Running the app

1. Confirm you have installed Docker, Docker-compose
    - docker-compose version 1.29.2
2. Edit .env
    - Copy `.env.example` to `.env` and you can customize the environment variables.

3. Run the docker images
    - Build Docker images and run
    ```commandline
    sudo docker-compose build
    sudo docker-compose up
    ```
    - Make a database on docker postgresql.
        - Create a database with the name `DB_NAME` in `.env`
          ```commandline
          sudo docker-compose exec db bash
          psql -h localhost -U postgres
          CREATE DATABASE restaurant-vote
          ```

    - Run initial commands
    ```commandline
    // migrate database
    sudo docker-compose exec web python manage.py migrate
    // generate auth groups and permissions
    sudo docker-compose exec web python manage.py init_groups
    // generate seed data
    sudo docker-compose exec web python manage.py seed
    ```

4. API server is running on http://localhost:8000
    - Swagger Documentation: http://localhost:8000/docs/
    - API url: http://localhost:8000/api/

5. Test credential
    - Admin User
        - username: admin
        - password: adminpassword
    - Employee User
        - username: employee1
        - password: 123qwe!@#QWE
    - Restaurant Owner
        - username: rest_owner1
        - password: 123qwe!@#QWE
6. Generate JWT Token from http://localhost:8000/token/ with username and password.

7. Call APIs with Bearer Token Authentication using generated JWT Token.

## Testcases

```commandline
sudo docker-compose exec web python manage.py test
```
## Postman Collection
[ResList.postman_collection.json](docs/ResList.postman_collection.json)

## HA Cloud Architecture Diagram
![HA Cloud Diagram.png](docs/HA%20Cloud%20Diagram.png)