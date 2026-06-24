# FastAPI DevOps Containerization & Deployment Setup

This repository contains a production-minded containerization setup for a FastAPI-based backend service. Additionally, it features a complete enterprise-grade cloud native architecture deployed on Google Cloud Platform (GCP) utilizing Infrastructure as Code (IaC).

---

## Local Environment Setup

### Prerequisites
* Docker installed locally
* Docker Compose installed locally

### How to Run Locally
1. Clone this repository to your local system.
2. Build and launch the containerized application in detached mode:
```bash
   docker-compose up --build -d


Verify the deployment status and monitor active health checks:
docker-compose ps

Access the API endpoint inside your browser at http://localhost:8000.

Production Cloud Architecture (GCP + IaC)

Beyond local orchestration, a full-scale continuous deployment infrastructure has been provisioned on Google Cloud Platform using Terraform. 

Key Architectural Pillars:
  Infrastructure as Code (IaC): Designed with modular Terraform blocks (vpc.tf, sql.tf, secrets.tf, cloudrun.tf, providers.tf) ensuring structural scalability.

  Remote State Management: Local state files are eliminated. All structural mutations are locked dynamically using a remote Google Cloud Storage (GCS) state backend (bucket647).

  Zero-Trust Secret Resolution: The Python backend (main.py) contains zero hardcoded API keys or plaintext environment values. All dynamic string tokens are resolved at runtime via Google Secret Manager vault mapping.  

  Network Isolation: Public access to the Cloud SQL (PostgreSQL) cluster is completely disabled. Compute workloads route queries exclusively via an isolated Google Serverless VPC Access Connector tunnel.

  Automated CI/CD Pipeline: Integrated a GitHub Actions workflow that automatically triggers on change vectors, manages dependency verification, compiles production-ready assets, and pushes live artifacts directly to the Google Artifact Registry (GAR).
