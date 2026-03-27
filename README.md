# PaperHub - Academic Conference Paper Submission System

**Student:** Srinidhi Vutkoori (X25173243)
**Module:** Cloud Platform Programming - MSc at NCI
**Deadline:** 15 April 2026

## Overview

PaperHub is a full-stack cloud-native platform for managing academic conference paper submissions, peer reviews, and conference organisation. The system enables researchers to submit papers, conference organisers to manage events, and reviewers to provide structured feedback.

## Architecture

```
frontend/          React SPA (S3 static hosting)
backend/           Flask REST API (AWS Lambda)
library/           confmanager - shared Python library
paperflow/         PaperFlow - paper workflow library
report/            LaTeX project report
```

## AWS Services (eu-west-1)

| Service       | Resource                            | Purpose                          |
|---------------|-------------------------------------|----------------------------------|
| DynamoDB      | `confpapers-prod`                   | Paper and conference data store  |
| S3            | `confpapers-files-prod-srinidhi`    | Paper file uploads               |
| S3            | `confpapers-frontend-prod-srinidhi` | Frontend static hosting          |
| Lambda        | `confpapers-api`                    | Backend API runtime              |
| API Gateway   | `confpapers-api`                    | REST API endpoint                |
| SNS           | `confpapers-notifications`          | Email notifications              |
| IAM           | `confpapers-lambda-role`            | Lambda execution role            |

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) runs three jobs:

1. **test-library** - Installs and tests the confmanager library with pytest
2. **deploy-backend** - Provisions AWS infrastructure and deploys the Lambda function
3. **deploy-frontend** - Builds the React app and syncs to S3

### Required Secrets

| Secret                | Description            |
|-----------------------|------------------------|
| `AWS_ACCESS_KEY_ID`   | AWS IAM access key     |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key   |

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
pip install -e ../library
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Library Tests
```bash
cd library
pip install -e .
pip install pytest
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/conferences`        | List all conferences     |
| POST   | `/api/conferences`        | Create a conference      |
| GET    | `/api/papers`             | List all papers          |
| POST   | `/api/papers`             | Submit a paper           |
| GET    | `/api/reviews`            | List all reviews         |
| POST   | `/api/reviews`            | Submit a review          |
| GET    | `/api/authors`            | List all authors         |
| GET    | `/api/health`             | Health check             |
| GET    | `/api/dashboard`          | Dashboard statistics     |
| GET    | `/api/aws/status`         | AWS services status      |
