# ADB Safegate DevOps Assignment — Architecture and Design

## 1. Overview

This project demonstrates a local Kubernetes-based deployment of a two-tier application using Infrastructure as Code, containerization, automated testing, and basic observability.

The solution consists of:

- Python Flask web application
- PostgreSQL database
- Docker multi-stage image
- Terraform-managed Kind Kubernetes cluster
- Kubernetes Deployments and Services
- PersistentVolumeClaim for PostgreSQL
- ConfigMap and Secret references
- Kubernetes resource requests, limits, and health probes
- Metrics Server for CPU and memory monitoring
- GitHub Actions CI pipeline using Docker Compose

## 2. Local Architecture

The local environment uses a single-node Kind Kubernetes cluster provisioned through Terraform.

Application traffic flows through a Kubernetes ClusterIP Service to the Flask application. The application connects to PostgreSQL using the database Service name.

Architecture:

    Developer / kubectl port-forward
                  |
                  v
         Kubernetes Service
              adb-web
                  |
                  v
         Flask Web Deployment
             (1 replica)
                  |
                  v
         PostgreSQL Service
            adb-postgres
                  |
                  v
        PostgreSQL Deployment
             (1 replica)
                  |
                  v
          PersistentVolumeClaim
                 (1Gi)

Both application components run inside the Kind cluster.

## 3. Infrastructure as Code

Terraform provisions the local Kubernetes cluster using the Kind provider.

Benefits:

- Repeatable cluster provisioning
- Declarative infrastructure definition
- Version-controlled configuration
- Consistent local environments

The Terraform state is stored locally for this assignment and excluded from Git.

For production, remote state storage with encryption, locking, and restricted access would be used.

## 4. Container Design and Security

The Python application uses a multi-stage Docker build.

The builder stage installs dependencies, while the runtime stage copies the installed dependencies and application source.

Security choices:

- Python slim base image reduces unnecessary packages.
- The application runs as non-root UID 10001.
- Dependencies are installed using pinned versions.
- Only application dependencies and source are copied into the runtime image.
- The application runs through Gunicorn on port 8080.

These choices reduce unnecessary image content and avoid running the application with root privileges.

Additional production improvements would include vulnerability scanning, digest-pinned base images, a read-only root filesystem where practical, and stronger runtime security controls.

## 5. Kubernetes Deployment Design

The application and PostgreSQL run as separate Kubernetes Deployments.

Each component has an internal ClusterIP Service.

The web application uses Kubernetes DNS to connect to the database through the service name `adb-postgres`.

Resource requests and limits are configured to support scheduling and prevent uncontrolled resource consumption.

Readiness probes determine whether a container is ready to receive traffic.

Liveness probes allow Kubernetes to restart containers that fail their health checks.

The web application's `/health` endpoint checks application availability, while `/db-health` verifies actual PostgreSQL connectivity.

## 6. Configuration and Secrets

Non-sensitive application configuration is stored in a Kubernetes ConfigMap.

Database credentials are provided through Kubernetes Secret references.

The local development Secret is created separately using kubectl and is not committed to Git.

Kubernetes Secrets should not be considered fully secure simply because they are stored as Secret resources.

For production, stronger controls would include:

- Encryption at rest
- Restricted RBAC permissions
- External secret management
- Credential rotation

## 7. Database Persistence

PostgreSQL uses a 1Gi PersistentVolumeClaim with ReadWriteOnce access.

This allows database files to persist across container or Pod replacement while the underlying volume remains available.

However, the local storage is not a backup solution.

The single-node Kind environment does not provide protection against complete node or host failure.

## 8. Observability

Metrics Server is deployed in the Kind cluster.

It provides CPU and memory usage information through:

- kubectl top nodes
- kubectl top pods
- kubectl top pods -A

Kubernetes readiness and liveness probes provide basic application health monitoring.

Metrics Server does not provide long-term metrics retention, alerting, or application tracing.

A production platform would typically use Prometheus, Grafana, centralized logging, and alerting.

The local Metrics Server uses `--kubelet-insecure-tls` to accommodate the development environment. This is not recommended for production.

## 9. CI Pipeline

GitHub Actions automatically runs on pushes and pull requests.

The workflow performs:

1. Repository checkout
2. Python environment setup
3. Dependency installation
4. Python unit tests
5. Docker Compose image build and application startup
6. HTTP smoke tests for `/health` and `/db-health`
7. Container cleanup

Docker Compose is used in CI because it provides a lightweight way to validate the complete web and database stack.

The pipeline does not deploy to a production environment.

## 10. Single Points of Failure

The local Kind cluster has one Kubernetes node.

If this node fails, the application becomes unavailable.

PostgreSQL also runs as a single replica and is a single point of failure.

The PVC protects against some Pod lifecycle events but does not provide database replication or disaster recovery.

Mitigations for production would include:

- Multiple Kubernetes worker nodes
- Multiple application replicas
- Pod anti-affinity or topology spread constraints
- Managed PostgreSQL with high availability
- Automated backups and recovery testing
- Multi-zone infrastructure

## 11. Scaling to Production on Azure AKS

A production implementation could use Azure Kubernetes Service (AKS).

Proposed improvements:

### Infrastructure

- AKS cluster across availability zones
- Multiple worker nodes
- Terraform-managed infrastructure
- Remote Terraform state with locking
- Private networking and restricted cluster access

### Application

- Multiple Flask replicas
- Horizontal Pod Autoscaler
- Ingress controller with TLS
- Rolling deployments
- PodDisruptionBudget
- Topology spread constraints

### Database

- Azure Database for PostgreSQL with high availability
- Automated backups
- Private database connectivity
- Recovery procedures and testing

### Security

- Azure Key Vault for secrets
- Workload identity
- Least-privilege RBAC
- Image vulnerability scanning
- Network policies
- Container security contexts

### Observability

- Prometheus and Grafana
- Centralized application and infrastructure logs
- Alerting for availability, latency, errors, and resource usage

## 12. Local Development Trade-offs

The local solution prioritizes simplicity, reproducibility, and low cost.

Limitations include:

- Single Kubernetes node
- Single web and database replicas
- Local persistent storage
- No external ingress or TLS
- Basic resource metrics only
- Development-only database credentials
- No automated production deployment
- No multi-zone disaster recovery

These trade-offs are acceptable for a local demonstration but would need to be addressed before production deployment.

## 13. Conclusion

The project demonstrates an end-to-end DevOps workflow covering infrastructure provisioning, container security, Kubernetes deployment, persistent storage, configuration management, basic monitoring, and automated CI testing.

The architecture is intentionally lightweight for local development while providing a foundation for a production-ready, highly available cloud platform.
