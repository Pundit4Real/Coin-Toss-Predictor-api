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

### API Endpoints
<!-- 
## API Endpoints
#### Create a Person Profile
Endpoint: POST /api

##### Request Format:
`{
    "name": "Tulasi Joshua"
}`

##### Response Format:
    {
        "status": 200 ok,
       
         {
            "id": 2,
            "name": "Tulasi Joshua",
            "country": "CHAD",
            "stack": "Backend",
            "added": "2023-09-15T16:32:29.220209Z"
        }

    }

#### Get Person Profile
Endpoint: GET /api/{user_id}

##### Request Format: 
`No request body required.`

##### Response Format:
    {
        {
            "id": 3,
            "name": "MOHAMMED ALI",
            "country": "GHANA",
            "stack": "Backend",
            "added": "2023-09-15T17:00:45.115412Z"
        }
    }

#### Update Person Profile
Endpoint: PATCH /api/{user_id}

##### Request Format:
    {
        "name": "Updated Name"
    }

##### Response Format:
    {
        "status": 200 ok,
       
    }

#### Delete Person Profile
Endpoint: DELETE /api/{user_id}

##### Request Format: 
    No request body required.

##### Response Format:
    {
        "status": 204 No Content,
       
    }

## Sample Usage

### Creating a Person Profile
##### Request:

###### POST /api
    Content-Type: application/json

    {
        "name": "MOHAMMED ALI"
    }

#### Response:
    HTTP/1.1 201 Created
    {
        "status": true,
       
        {
            "id": 3,
            "name": "MOHAMMED ALI",
            "country": "GHANA",
            "stack": "Backend",
            "added": "2023-09-15T17:00:45.115412Z"
        }
    }

### Getting Personal Profile
#### Request:
`GET /api/2`
#### Response:
    HTTP/1.1 200 OK
    {
        "status": 200 OK,
        {
            "id": 3,
            "name": "MOHAMMED ALI",
            "country": "GHANA",
            "stack": "Backend",
            "added": "2023-09-15T17:00:45.115412Z"
        }
    } -->
