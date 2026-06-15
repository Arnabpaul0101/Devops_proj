# Community Food Bank Management System

A Dockerized Flask and MySQL application for managing a community food bank.

## Features
- Contributor registration and management
- Food inventory tracking across 8 categories
- Food request creation, approval, and rejection
- Partner agency registration
- Dashboard with real-time summary
- Search contributors and inventory by food category

## Prerequisites
- Docker Desktop
- Git

## Quick Start

```bash
git clone <your-repo-url>
cd devops-project
docker-compose up --build
```

Open http://localhost:5000 in your browser.

Admin login:

- Username: `admin`
- Password: `admin123`

MySQL is available to tools such as MySQL Workbench at:

- Host: `127.0.0.1`
- Port: `3307`
- Username: `root`
- Password: `rootpassword`
- Schema: `foodbank`

To stop the project:

```bash
docker-compose down
```

## Running Tests Locally

```bash
cd app
pip install -r requirements.txt
pytest ../tests/ -v
```

## Project Structure

```text
devops-project/
|-- docker-compose.yml
|-- db/init.sql
|-- app/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- run.py
|   |-- config.py
|   |-- __init__.py
|   |-- models/db.py
|   |-- routes/
|   |-- templates/
|   `-- static/
`-- tests/
```
