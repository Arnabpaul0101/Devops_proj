# Community Food Bank Management System

A DevOps mini project demonstrating Git, Docker, and Jenkins CI/CD workflows.

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
- Jenkins with Docker installed on the agent

## Quick Start

```bash
git clone <your-repo-url>
cd devops-project
docker-compose up --build
```

Open http://localhost:5000 in your browser.

## Running Tests Locally

```bash
cd app
pip install -r requirements.txt
pytest ../tests/ -v
```

## Jenkins Setup

1. Install Jenkins and the Pipeline plugin.
2. Add Docker Hub credentials in Jenkins -> Manage Jenkins -> Credentials.
   - Kind: Username with password
   - ID: `dockerhub-credentials`
3. Create a new Pipeline job.
4. Under Pipeline -> Definition, select Pipeline script from SCM.
5. Set SCM to Git and enter your repo URL.
6. Script Path: `Jenkinsfile`.
7. Edit `Jenkinsfile` and set `REGISTRY` to your Docker Hub username.
8. Run the pipeline. All 5 stages should go green.

## Branch Strategy

| Branch | Purpose | Pipeline |
|--------|---------|----------|
| `main` | Production-ready code | Full pipeline: Build -> Test -> Push -> Deploy |
| `develop` | Integration branch | Build + Test only |
| `feature/*` | Individual features | None, local only |

## Pipeline Stages

1. Checkout - pulls source from Git.
2. Build - builds Docker image tagged with `BUILD_NUMBER`.
3. Test - runs pytest inside the container.
4. Push Image - pushes to Docker Hub.
5. Deploy - restarts the stack with `docker-compose`.

## Project Structure

```text
devops-project/
|-- Jenkinsfile
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
