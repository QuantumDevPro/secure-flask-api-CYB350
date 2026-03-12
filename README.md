# SecureAPI

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-green)](https://flask.palletsprojects.com/)
[![Security](https://img.shields.io/badge/API-Secure-red)](https://github.com/QuantumDevPro/secure-flask-api-CYB350)

A **secure Flask REST API** demonstrating modern API security techniques.

---

# Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Obtain the Project](#obtain-the-project)
- [Install Dependencies](#install-dependencies)
- [Run the API](#run-the-api-https-enabled)
- [Swagger Documentation](#swagger-documentation)
- [Authentication Methods](#authentication-methods)
- [API Endpoints](#api-endpoints)
- [Testing via PowerShell](#testing-via-powershell)
- [Validation Tests](#validation-tests)
- [Stopping the Server](#stopping-the-server)
- [Notes](#notes)

---

# Overview

This project implements a **secure REST API using the Flask framework**.  
It demonstrates several modern API security mechanisms including API Key authentication, GitHub OAuth2 authentication, HTTPS encryption, and interactive API documentation using Swagger.

Features:

* CRUD API for managing items
* HTTPS using a self-signed SSL certificate
* API Key authentication
* GitHub OAuth2 login
* Interactive Swagger documentation
* Input validation and proper error handling
* In-memory storage (no external database)
This project demonstrates **multiple authentication methods and secure API practices**.

## Project Structure

```
secureAPI/
│
├── app.py
├── jwt_app.py
├── key_manager.py
├── swagger.yaml
├── requirements.txt
│
├── cert/
│   ├── cert.pem
│   └── key.pem
│
└── README.md
```


# Requirements

* Windows
* Python 3.12+
* PowerShell

---

# Obtain the Project

You can either **download the project archive** or **clone the repository from GitHub**.

### Option 1: Download the ZIP

1. Download the project `.zip` file.
2. Extract the archive.
3. Open the extracted folder in your terminal.

### Option 2: Clone the Repository

```powershell
git clone https://github.com/QuantumDevPro/secure-flask-api-CYB350
cd secureAPI
````
--- 
# Install Dependencies

Before installing the project dependencies, create and activate a Python virtual environment.

### 1. Create a virtual environment

From the project root directory:

```powershell
python -m venv venv
```

### 2. Activate the virtual environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate
```

After activation, your terminal prompt should show `(venv)`.

### 3. Install project dependencies

With the virtual environment activated, install the required packages:

```powershell
pip install -r requirements.txt
```

This installs the required libraries:

* Flask
* Flasgger
* Authlib
* Flask-Limiter
* requests

---

# Run the API (HTTPS Enabled)

Start the server:

```powershell
python app.py
```

Expected output:

```
Running on https://127.0.0.1:5000
```

Because the API uses a **self-signed SSL certificate**, your browser will show a warning.

Click:

```
Advanced → Proceed
```

This is normal for local development.

---

# Swagger Documentation

Open the interactive documentation:

```
https://127.0.0.1:5000/docs
```

Before testing endpoints:

1. Click the **Authorize** button in Swagger.
2. Enter the API key:

```
secret_key
```

This authorizes your browser to access protected endpoints.

Swagger allows you to:

* Explore endpoints
* Send test requests
* View request/response models
* Debug the API interactively

OpenAPI specification:

```
https://127.0.0.1:5000/swagger.json
```

---

# Authentication Methods

This API demonstrates **three authentication methods**.


## API Key Authentication

Protected endpoints require an API key.

Required header:

```
X-API-Key: secret_key
```

Routes **excluded from API key validation**:

```
/
/docs
/swagger.json
/login
/authorize
```

---

## GitHub OAuth2 Authentication

The API supports login through **GitHub OAuth2**.

### Step 1: Login

Open:

```
https://127.0.0.1:5000/login
```

This redirects to GitHub authorization.

---

### Step 2: Authorize Application

GitHub will ask you to approve access.

After authorization, GitHub redirects to:

```
/authorize
```

Example response:

```json
{
  "github_user": "QuantumDevPro",
  "message": "OAuth2 Authentication Successful"
}
```

The access token is stored in the Flask session.

---

Below is the **exact section you can add to your README under “Authentication Methods”**.
It matches **your screenshot commands and output exactly** and keeps the same documentation style as the rest of your README.

---
## JWT Authentication

The API also supports **JSON Web Token (JWT) authentication** for accessing protected endpoints.

JWT authentication works by issuing a signed token after a successful login.  
The client must include this token in the `Authorization` header when accessing protected routes.

### Step 1: Obtain a Token

Send a login request with valid credentials.

```powershell
$r = Invoke-RestMethod -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"1234"}'
````

Extract the token:

```powershell
$token = $r.access_token
```

---

### Step 2: Access a Protected Endpoint

Use the token in the `Authorization` header.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/protected" `
  -Headers @{Authorization="Bearer $token"}
```

Expected response:

```json
{
  "message": "Hello admin, you are authorized!"
}
```

If the token is **missing, invalid, or expired**, the API will deny access to the endpoint.

---
# API Endpoints

| Method | Endpoint      | Description        |
| :----: | :------------ | :----------------- |
|   GET  | `/`           | Health check       |
|   GET  | `/items`      | Get all items      |
|   GET  | `/items/<id>` | Get item by ID     |
|  POST  | `/items`      | Create item        |
|   PUT  | `/items/<id>` | Update item        |
| DELETE | `/items/<id>` | Delete item        |
|   GET  | `/login`      | GitHub OAuth login |
|   GET  | `/authorize`  | OAuth callback     |

---

# Testing via PowerShell

Because the API uses **HTTPS with a self-signed certificate**, PowerShell must bypass certificate validation.

Run once per session:

```powershell
add-type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy : ICertificatePolicy {
    public bool CheckValidationResult(
        ServicePoint srvPoint,
        X509Certificate certificate,
        WebRequest request,
        int certificateProblem) {
        return true;
    }
}
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
```



## Health Check

```powershell
Invoke-RestMethod https://127.0.0.1:5000/
```

Expected:

```json
{
  "message": "Secure API is running!",
  "status": "ok"
}
```



## Create Item

```powershell
Invoke-RestMethod -Uri https://127.0.0.1:5000/items `
  -Method POST `
  -Headers @{ "X-API-Key"="secret_key" } `
  -ContentType "application/json" `
  -Body '{"name":"sword","quantity":5}'
```



## Get All Items

```powershell
Invoke-RestMethod https://127.0.0.1:5000/items `
  -Headers @{ "X-API-Key"="secret_key" }
```



## Update Item

```powershell
Invoke-RestMethod -Uri https://127.0.0.1:5000/items/1 `
  -Method PUT `
  -Headers @{ "X-API-Key"="secret_key" } `
  -ContentType "application/json" `
  -Body '{"quantity":99}'
```



## Delete Item

```powershell
Invoke-RestMethod -Uri https://127.0.0.1:5000/items/1 `
  -Method DELETE `
  -Headers @{ "X-API-Key"="secret_key_key" }
```

---

# Validation Tests

Using Swagger `/docs`, try these invalid requests.

### Missing Field → 400

```json
{
  "name": "bow"
}
```

### Negative Quantity → 400

```json
{
  "name": "arrows",
  "quantity": -5
}
```

A secure API must **fail gracefully and predictably**.

---

# Stopping the Server

Press:

```
Ctrl + C
```

in the terminal running the API.

---

# Notes

Ensure the SSL certificate folder exists:

```
cert/cert.pem
cert/key.pem
```

These certificates enable **HTTPS for local development**.


**Important security note**

The OAuth `client_secret` should never be committed in production environments.
It is included here only for **educational purposes**, and it was deleted from the account already.
