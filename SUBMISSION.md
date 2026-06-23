Name: Your Name
Time spent (minutes): 90
What I delivered (1-2 lines): A production-ready, non-root Dockerfile containerizing a FastAPI service alongside a structured docker-compose.yml with production restart policies and health checks.
How to run (commands): Run 'docker-compose up --build -d' to build and start the service in detached mode, and 'docker-compose ps' to verify.
Assumptions I made: Assumed the FastAPI application entrypoint is defined within 'app.py' as an 'app' instance and exposed on port 8080.
How configuration is handled: Configuration is dynamically injected via environment variables inside the docker-compose descriptor, keeping the image entirely stateless.
How scaling would work: Scaling can be achieved horizontally by launching multiple container replicas behind an external load balancer (like Cloud Run or Nginx) to distribute traffic.
How updates would be deployed without downtime: Utilizing a rolling update deployment strategy (such as blue-green deployments) where new versions spin up and pass health checks before old ones terminate.
One production risk and how to reduce it: Risk of containers running out of memory. Reduced by implementing strict CPU and memory limits inside docker-compose or container engine configurations.
One thing kept intentionally simple and why: Kept database and cache dependencies outside of this compose layer to focus purely on the core FastAPI containerization standard requested.