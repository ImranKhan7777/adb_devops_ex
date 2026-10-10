# ADB Safegate DevOps Assignment

## Overview

This project demonstrates an end-to-end DevOps implementation using a Python Flask application, PostgreSQL database, Docker, Terraform, Kubernetes (Kind), and GitHub Actions.

The solution runs locally on a single-node Kubernetes cluster provisioned using Terraform.

It includes:

- Python Flask web application with automated unit tests
- PostgreSQL database with persistent storage
- Secure multi-stage Docker image running as a non-root user
- Kubernetes Deployments and Services
- ConfigMap and Secret-based configuration
- CPU and memory requests and limits
- Readiness and liveness probes
- Metrics Server for Kubernetes resource monitoring
- GitHub Actions CI pipeline with automated smoke tests

## Technology Stack

| Component | Technology |
|-----------|------------|
| Application | Python 3.12, Flask, Gunicorn |
| Database | PostgreSQL 16 |
| Containerization | Docker |
| Infrastructure as Code | Terraform |
| Kubernetes | Kind |
| Configuration | ConfigMaps and Secrets |
| Storage | Kubernetes PVC |
| Monitoring | Metrics Server |
| CI | GitHub Actions |
| Integration Testing | Docker Compose |
| Unit Testing | pytest |

## Repository Structure

```text
adb-devops-assignment/
├── app/
│   ├── app.py
│   ├── __init__.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── tests/
│       └── test_app.py
├── docker/
│   └── Dockerfile
├── terraform/
│   ├── main.tf
│   └── .terraform.lock.hcl
├── k8s/
│   ├── config.yaml
│   ├── database.yaml
│   └── web.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── DESIGN.md
└── README.md

## Prerequisites

The following tools are required:

- Linux or WSL2 environment
- Docker Engine or Docker Desktop with Linux container support
- Terraform
- Kind
- kubectl
- Python 3.9 or later
- Git

Docker must be running before creating the Kind cluster.

Verify the tools:

```bash
docker --version
docker compose version
terraform version
kind version
kubectl version --client
python3 --version
```

## Clone the Repository

Clone the project from GitHub:

    git clone https://github.com/ImranKhan7777/adb_devops_ex.git
    cd adb_devops_ex

The commands above are examples for a new environment.
If you are already working inside the repository, do not clone it again.


## Create the Kubernetes Cluster

Terraform provisions a single-node Kind Kubernetes cluster named `adb-devops`.

Initialize Terraform:

    terraform -chdir=terraform init

Review the infrastructure plan:

    terraform -chdir=terraform plan

Create the Kubernetes cluster:

    terraform -chdir=terraform apply

Type `yes` when Terraform asks for confirmation.

Verify the cluster:

    kind get clusters
    kubectl get nodes --context kind-adb-devops

Select the Kubernetes context:

    kubectl config use-context kind-adb-devops

The cluster runs locally using Docker containers.
No cloud account is required.


## Build and Load the Docker Image

The Flask application uses a multi-stage Dockerfile and runs as a non-root user.

Build the application image:

    docker build -t adb-devops-app:1.1 -f docker/Dockerfile .

Verify the image exists:

    docker images adb-devops-app

Load the image into the Kind cluster:

    kind load docker-image adb-devops-app:1.1 --name adb-devops

Kind runs Kubernetes nodes as Docker containers. Loading the image makes it available to the cluster without pushing it to an external container registry.

The web Deployment uses imagePullPolicy: IfNotPresent.


## Deploy the Application to Kubernetes

### 1. Create the ConfigMap

The ConfigMap stores non-sensitive database connection settings.

    kubectl apply -f k8s/config.yaml

### 2. Create the Database Secret

Create a Kubernetes Secret containing development-only database credentials.

Replace the example password with your own local development password.

    kubectl create secret generic adb-db-secret \
      --from-literal=DB_USER=adbuser \
      --from-literal=DB_PASSWORD=localdevpassword \
      --from-literal=POSTGRES_USER=adbuser \
      --from-literal=POSTGRES_PASSWORD=localdevpassword

The Secret is created locally and is not stored in Git.

Do not use these example credentials in production.

### 3. Deploy PostgreSQL

    kubectl apply -f k8s/database.yaml

Wait for PostgreSQL:

    kubectl rollout status deployment/adb-postgres --timeout=120s

Verify persistent storage:

    kubectl get pvc

The PostgreSQL database uses a 1Gi PersistentVolumeClaim.

### 4. Deploy the Flask Application

    kubectl apply -f k8s/web.yaml

Wait for the web application:

    kubectl rollout status deployment/adb-web --timeout=120s

### 5. Verify the Deployment

    kubectl get pods
    kubectl get services
    kubectl get pvc

Both application Pods should be Running and Ready.


## Test the Application

The Flask application is exposed internally through the Kubernetes Service `adb-web`.

Forward the Service port to localhost:

    kubectl port-forward service/adb-web 8080:8080

Keep this command running in a separate terminal.

Open another terminal and test the application.

### Application Health Check

    curl -i http://localhost:8080/health

Expected response:

    HTTP/1.1 200 OK
    {"status":"healthy"}

### Database Connectivity Check

    curl -i http://localhost:8080/db-health

Expected response:

    HTTP/1.1 200 OK
    {"database":"connected"}

The `/health` endpoint checks application availability.

The `/db-health` endpoint performs a database query to verify PostgreSQL connectivity.

Stop port forwarding using Ctrl+C in the terminal running `kubectl port-forward`.


## Observability with Metrics Server

Metrics Server provides CPU and memory usage information for Kubernetes nodes and Pods.

Install Metrics Server:

    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.8.1/components.yaml

For the local Kind environment, configure Metrics Server to accept the development kubelet certificates:

    kubectl patch deployment metrics-server -n kube-system \
      --type='json' \
      -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

Wait for Metrics Server:

    kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s

Check node resource usage:

    kubectl top nodes

Check application Pod resource usage:

    kubectl top pods

Check resource usage across all namespaces:

    kubectl top pods -A

Metrics may take a short time to become available after installation.

The --kubelet-insecure-tls option is used only for this local development environment and should not be used in production.

Metrics Server provides current CPU and memory metrics, but not long-term monitoring or alerting.


## Local Unit Testing

Create and activate a Python virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install test dependencies:

    python -m pip install -r app/requirements-dev.txt

Run the automated unit tests:

    python -m pytest -v

The test suite validates the home endpoint, application health endpoint, and database-health endpoint using a mocked database connection.

## Docker Compose Integration Testing

Docker Compose provides a lightweight environment for running Flask and PostgreSQL together.

Start the application stack:

    DB_PASSWORD=localdevpassword docker compose up -d --build

Verify the running containers:

    docker compose ps

Test the application:

    curl -i http://localhost:8080/health
    curl -i http://localhost:8080/db-health

Both endpoints should return HTTP 200 when the stack is healthy.

Stop the containers:

    docker compose down

Remove the containers and development database volume if a complete reset is required:

    docker compose down -v

Warning: Removing the volume deletes the local Docker Compose database data.

## GitHub Actions CI Pipeline

The CI workflow is defined in `.github/workflows/ci.yml`.

It runs automatically on pushes and pull requests and can also be started manually.

The pipeline performs:

1. Checkout the repository.
2. Configure Python 3.12.
3. Install application and test dependencies.
4. Run pytest unit tests.
5. Build and start the Flask and PostgreSQL stack using Docker Compose.
6. Perform HTTP smoke tests against `/health` and `/db-health`.
7. Collect logs on failure and clean up the containers.

View the workflow runs:

https://github.com/ImranKhan7777/adb_devops_ex/actions

The pipeline validates application functionality and database connectivity. It does not deploy the application to Kubernetes or production.


## Cleanup

To remove the Kind Kubernetes cluster created by Terraform:

    terraform -chdir=terraform destroy

Review the Terraform destroy plan and type yes to confirm.

Warning: Destroying the Kind cluster also removes its local Kubernetes workloads and database storage. Back up any important data first.

To stop the Docker Compose application:

    docker compose down

To also delete the local Docker Compose database volume:

    docker compose down -v

The -v option permanently removes data stored in the Docker Compose volume.

## Architecture and Design

See [DESIGN.md](DESIGN.md) for the architecture, technical decisions, security considerations, limitations, and proposed Azure AKS production design.
