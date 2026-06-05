# ECS Flask CI/CD Project

A containerized Python Flask application deployed using Docker and designed for AWS ECS Fargate with GitHub Actions CI/CD automation.

## Project Overview

This project demonstrates modern DevOps practices by:

- Containerizing a Flask application with Docker
- Running the application locally using Docker
- Preparing deployment to AWS ECS Fargate
- Automating build and deployment using GitHub Actions
- Following Infrastructure as Code and CI/CD principles

---

## Tech Stack

- Python
- Flask
- Docker
- Amazon ECS Fargate
- Amazon ECR
- GitHub Actions
- AWS IAM

---

## Architecture

```text
Developer
    │
    ▼
GitHub Repository
    │
    ▼
GitHub Actions CI/CD
    │
    ▼
Build Docker Image
    │
    ▼
Amazon ECR
(Container Registry)
    │
    ▼
Amazon ECS Fargate
(Container Service)
    │
    ▼
Flask Application
    │
    ▼
End Users
```

---

## Project Structure

```text
ecs-flask-ci-cd-project/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
│
└── .github/
    └── workflows/
        └── deploy.yml
```

---

## Docker Build

Build the Docker image:

```bash
docker build -t ecs-flask-app .
```

Run the container:

```bash
docker run -p 5001:5000 ecs-flask-app
```

Access the application:

```text
http://localhost:5001
```

Expected output:

```text
Hello from ECS Fargate Project
```

---

## CI/CD Workflow

The deployment pipeline performs:

1. Code pushed to GitHub
2. GitHub Actions workflow triggered
3. Docker image built automatically
4. Image pushed to Amazon ECR
5. ECS service updated
6. New version deployed automatically

---

## Learning Outcomes

Through this project I gained experience with:

- Docker containerization
- Flask application deployment
- AWS ECS Fargate
- Amazon ECR
- GitHub Actions
- CI/CD automation
- Cloud-native application deployment

---

## Author 

**Badal BK**


Aspiring Cloud & DevOps Engineer

