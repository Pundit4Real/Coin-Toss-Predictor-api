# Coin Toss Predictor API Documentation

<!-- A warm welcome to the documentation for HNGx Backend Stage 2 Task API. This API allows you to perform CRUD (Create, Read, Update, Delete) operations on person profiles. -->

## Table of Contents

- [Prerequisites:](#prerequisites)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
- [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
  <!-- - [Create a Person Profile](#create-a-person-profile)
  - [Get Person Profile](#get-person-profile)
  - [Update Person Profile](#update-person-profile)
  - [Delete Person Profile](#delete-person-profile)
- [Sample Usage](#sample-usage)
- [Limitations and Assumptions](#limitations-and-assumptions) -->

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed.
- Pip package manager installed.
- A code editor (e.g., VSCode) for development.
- Postman or a similar tool for API testing.

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   https://github.com/Pundit4Real/HNGx-s2-Rest-Api-Basic-CRUD.git
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
3. Activate the virtual environment:
   ```bash
   - On Windows:
   venv\Scripts\activate or .\\Scripts.activate.ps1
   
   - On macOS and Linux:
   source venv/bin/activate

4. Install the required dependencies:
    `pip install -r requirements.txt`

### Database Setup
    python manage.py makemigrations
..................................

    python manage.py migrate

### Running the API
*To run the API locally, use the following command:*
    `python manage.py runserver`

*The API will be available at http://localhost:8000/.*

