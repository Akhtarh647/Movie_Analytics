Name: Your Name
Time spent (minutes): 90
What I delivered (1-2 lines): A production-grade containerized Python WSGI backend with dedicated non-root user execution, paired with an optimized docker-compose layer for localized runtime tests.
How to run (commands): Execute 'docker-compose up --build -d' to deploy locally in detached mode, and verify health statuses via 'docker-compose ps'.
Assumptions I made: Assumed the entrypoint binding relies on an 'app' instance initialized within 'app.py' mapping securely across port 8080.
How configuration is handled: Environment configurations are kept entirely decoupled and state-independent, safely injected on-runtime inside the deployment descriptors.
How scaling would work: Can easily scale horizontally by replicating core container targets across target instances behind an independent external layer like Cloud Run or Nginx proxies.
How updates would be deployed without downtime: Handled via progressive rolling-update deployment flows (such as Blue-Green routes) which require strict health check passing before traffic shifts.
One production risk and how to reduce it: Host system vulnerability leaks via root execution. Fully mitigated by embedding dedicated OS-level group privileges and restricting container scope to 'appuser'.
One thing kept intentionally simple and why: Kept downstream external DB and cache adapters decoupled to highlight pure deployment containerization fundamentals.