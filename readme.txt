================================================================================
Academic Conference Paper Submission System
Student: Srinidhi Vutkoori
Student ID: X25173243
Module: Cloud Platform Programming
Institution: National College of Ireland
================================================================================

PROJECT OVERVIEW
================
A cloud-native academic conference paper submission system built with Flask,
React, and six AWS services. Supports conference management, paper submission
with PDF upload, peer review assignment, NLP analysis of abstracts, email
notifications, and CDN-based content delivery.

AWS SERVICES USED
=================
1. Amazon DynamoDB    - NoSQL data store for conferences, papers, reviews, authors
2. Amazon S3          - Object storage for uploaded paper PDFs
3. Amazon SES         - Email notifications (submission, review, decision)
4. Amazon Comprehend  - NLP analysis of paper abstracts (keywords, sentiment)
5. Amazon CloudFront  - CDN for frontend assets and paper downloads
6. AWS Lambda         - Async paper processing and reviewer assignment

CUSTOM LIBRARY
==============
PaperFlow (paperflow/) - OOP library with 5 classes:
  - Paper: metadata validation, format checking, word count estimation
  - Reviewer: expertise matching, conflict detection, assignment optimization
  - Conference: deadline management, track organization, capacity planning
  - Submission: workflow state machine (draft -> submitted -> review -> decision)
  - Scoring: weighted review aggregation, statistical analysis, recommendations

DIRECTORY STRUCTURE
===================
Srinidhi/
  backend/          - Flask backend application
  frontend/         - React frontend application
  paperflow/        - Custom PaperFlow Python library
  report/           - IEEE LaTeX report and architecture diagram generator
  .github/workflows - CI/CD pipeline configuration
  readme.txt        - This file

PREREQUISITES
=============
  - Python 3.8 or higher
  - Node.js 18 or higher
  - npm 9 or higher
  - pip (Python package manager)

BACKEND SETUP
=============
1. Navigate to the backend directory:
     cd Srinidhi/backend

2. Create and activate a virtual environment (recommended):
     python -m venv venv
     source venv/bin/activate        (Linux/Mac)
     venv\Scripts\activate           (Windows)

3. Install the PaperFlow library:
     pip install -e ../paperflow

4. Install backend dependencies:
     pip install -r requirements.txt

5. Run the Flask development server:
     python app.py

   The backend will start on http://localhost:5000
   By default, USE_AWS=False (mock mode - no AWS credentials needed)

FRONTEND SETUP
==============
1. Navigate to the frontend directory:
     cd Srinidhi/frontend

2. Install Node.js dependencies:
     npm install

3. Start the React development server:
     npm start

   The frontend will start on http://localhost:3000

RUNNING TESTS
=============
Backend tests:
     cd Srinidhi/backend
     pytest tests/ -v

Library tests:
     cd Srinidhi/paperflow
     pytest tests/ -v

All tests together:
     cd Srinidhi/backend && pytest tests/ -v
     cd Srinidhi/paperflow && pytest tests/ -v

CONFIGURATION
=============
The backend runs in mock mode by default (USE_AWS=False in config.py).
To connect to real AWS services, set the following environment variables:

  export USE_AWS=True
  export AWS_REGION=eu-west-1
  export AWS_ACCESS_KEY_ID=your-access-key
  export AWS_SECRET_ACCESS_KEY=your-secret-key
  export S3_BUCKET_NAME=your-bucket-name
  export SES_SENDER_EMAIL=verified@email.com
  export CLOUDFRONT_DOMAIN=your-distribution.cloudfront.net
  export CLOUDFRONT_DISTRIBUTION_ID=your-dist-id

API ENDPOINTS
=============
  GET    /api/dashboard              - System statistics
  GET    /api/health                 - Health check

  GET    /api/conferences            - List all conferences
  POST   /api/conferences            - Create conference
  GET    /api/conferences/<id>       - Get conference details
  PUT    /api/conferences/<id>       - Update conference
  DELETE /api/conferences/<id>       - Delete conference

  GET    /api/papers                 - List all papers
  POST   /api/papers                 - Submit paper
  GET    /api/papers/<id>            - Get paper details
  PUT    /api/papers/<id>            - Update paper
  DELETE /api/papers/<id>            - Delete paper
  POST   /api/papers/<id>/analyze    - Run NLP analysis

  GET    /api/reviews                - List all reviews
  POST   /api/reviews                - Create review
  GET    /api/reviews/<id>           - Get review details
  PUT    /api/reviews/<id>           - Update review
  DELETE /api/reviews/<id>           - Delete review

  GET    /api/authors                - List all authors
  POST   /api/authors                - Create author
  GET    /api/authors/<id>           - Get author details
  PUT    /api/authors/<id>           - Update author
  DELETE /api/authors/<id>           - Delete author

  GET    /api/aws/status             - All AWS service statuses

GENERATING ARCHITECTURE DIAGRAM
================================
     cd Srinidhi/report
     python architecture.py

   This creates architecture.png in the report directory.

BUILDING THE LATEX REPORT
=========================
     cd Srinidhi/report
     pdflatex main.tex
     bibtex main
     pdflatex main.tex
     pdflatex main.tex

CI/CD PIPELINE
==============
The GitHub Actions workflow (.github/workflows/deploy.yml) runs on every push:
  1. Tests the PaperFlow library
  2. Tests and packages the Flask backend
  3. Builds the React frontend

DEPENDENCIES
============
Backend (Python):
  - Flask 3.0.0
  - Flask-SQLAlchemy 3.1.1
  - Flask-CORS 4.0.0
  - boto3 1.34.0
  - pytest 7.4.3
  - matplotlib 3.8.2

Frontend (Node.js):
  - React 18.2.0
  - react-router-dom 6.20.0
  - axios 1.6.2

Library (Python):
  - No external dependencies (stdlib only)
  - Dev: pytest, pytest-cov
================================================================================
