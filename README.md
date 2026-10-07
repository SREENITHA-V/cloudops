CloudOps — DevOps Web Application with Docker, CI/CD & Monitoring

CloudOps is a containerized web application deployed using Docker Compose with PostgreSQL, Nginx, Prometheus, and Grafana.

The project demonstrates a practical DevOps workflow:

Application
    ↓
Git & GitHub
    ↓
Docker
    ↓
Docker Compose
    ↓
Nginx
    ↓
Web Application
    ↓
PostgreSQL

Monitoring:
Prometheus → Grafana

**1. Project Overview**
CloudOps is a DevOps-focused web application designed to demonstrate how an application can be:
Developed locally
Containerized using Docker
Connected to PostgreSQL
Managed using Docker Compose
Exposed through Nginx
Monitored using Prometheus and Grafana
Version-controlled using Git and GitHub
Deployed on an AWS EC2 instance
Automated using GitHub Actions
The project is useful as a practical demonstration of DevOps, containerization, CI/CD, cloud deployment, networking, and monitoring.

**2. Technologies Used**
Technology	Purpose
Python	Backend application
Flask	Web application framework
PostgreSQL	Application database
SQLAlchemy	Database interaction
Docker	Containerization
Docker Compose	Multi-container orchestration
Nginx	Reverse proxy
Prometheus	Metrics collection
Grafana	Monitoring dashboards
Git	Version control
GitHub	Source-code repository
GitHub Actions	CI/CD automation
AWS EC2	Cloud deployment
Linux/Ubuntu	Server operating system
3. Architecture
                         Internet
                            │
                            ▼
                  ┌──────────────────┐
                  │    AWS EC2       │
                  │   Ubuntu Server  │
                  └────────┬─────────┘
                           │
                           │ Port 80
                           ▼
                  ┌──────────────────┐
                  │      Nginx       │
                  │ Reverse Proxy    │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         ┌─────────┐ ┌────────────┐ ┌───────────┐
         │   Web   │ │ Prometheus │ │  Grafana  │
         │ Flask   │ │ Monitoring │ │ Dashboard │
         └────┬────┘ └────────────┘ └───────────┘
              │
              ▼
         ┌──────────┐
         │PostgreSQL│
         │ Database │
         └──────────┘
   
**5. Docker Compose Architecture**
The application consists of multiple services.

cloudops
│
├── web
│   └── Flask application + Gunicorn
│
├── db
│   └── PostgreSQL
│
├── nginx
│   └── Reverse proxy
│
├── prometheus
│   └── Metrics collection
│
└── grafana
    └── Monitoring dashboard

All services communicate through the Docker network:
appnet
The database is accessed using the Docker service name:
db
Important: Inside Docker Compose, the application should use:
db
and not:
localhost
because localhost inside the web container refers to the web container itself.

5. Important Project Files
A typical project structure is:
CloudOps/
│
├── app.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── pytest.ini
├── .env
├── .gitignore
│
├── monitoring/
│   └── prometheus.yml
│
├── nginx/
│   └── default.conf
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
└── .github/
    └── workflows/
        └── deploy.yml
        
**6. What Each File Does**
app.py
Main Python application.
It contains:
Flask application
Routes
Database connection
SQLAlchemy configuration
Application functionality
Health/API endpoints

The application obtains the database connection from:
DATABASE_URL
Dockerfile
Defines how the web application Docker image is built.
General flow:

Python Base Image
       ↓
Install dependencies
       ↓
Copy application
       ↓
Start Gunicorn

compose.yaml
Defines the complete application infrastructure.
It manages:
web
db
prometheus
grafana
nginx

Instead of starting each container manually, Docker Compose starts everything together.
.env
Contains environment-specific configuration and secrets.

Example:
POSTGRES_USER=cloudops
POSTGRES_PASSWORD=YOUR_DATABASE_PASSWORD
POSTGRES_DB=cloudops
DATABASE_URL=postgresql://cloudops:YOUR_ENCODED_PASSWORD@db:5432/cloudops
IMPORTANT
Never commit .env to GitHub.
Add this to .gitignore:
.env

**7. Database Configuration**
The PostgreSQL service uses:
Database:
cloudops
User:
cloudops
Host:
db
Port:
5432

The application connects using:
postgresql://cloudops:PASSWORD@db:5432/cloudops
Important Password Rule
Passwords used inside a database URL may contain characters that have special meanings in URLs.
For example:
@

must be encoded as:
%40

Therefore:
CloudOpsDB@2026
becomes:
CloudOpsDB%402026
when used inside DATABASE_URL.
However, the actual PostgreSQL password remains the original password.

**8. Running CloudOps Locally**
Step 1 — Clone the repository
git clone https://github.com/SREENITHA-V/CloudOps.git
Enter the project:
cd CloudOps

Step 2 — Create .env
Create:
.env
Example:
POSTGRES_USER=cloudops
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DB=cloudops
DATABASE_URL=postgresql://cloudops:YOUR_ENCODED_PASSWORD@db:5432/cloudops
Do not upload this file to GitHub.

Step 3 — Start the application
docker compose up -d --build
Check containers:
docker compose ps
You should see services such as:
web
db
nginx
prometheus
grafana

**9. Useful Docker Commands**
Start everything
docker compose up -d
Build and start
docker compose up -d --build
Stop containers
docker compose down
Restart everything
docker compose restart
Check containers
docker compose ps
View all logs
docker compose logs
View web logs
docker compose logs web
View last 50 web log lines
docker compose logs web --tail=50
Follow logs continuously
docker compose logs -f web

**10. Database Troubleshooting**
Check whether PostgreSQL is healthy:
docker compose exec db pg_isready -U cloudops -d cloudops
Expected:
/var/run/postgresql:5432 - accepting connections
Test Docker DNS
The web container must be able to resolve:
db
Test from the Docker network:
docker run --rm --network cloudops_appnet alpine:3.20 getent hosts db
Expected:
172.18.x.x    db    db
Test PostgreSQL connectivity
docker run --rm \
  --network cloudops_appnet \
  postgres:16-alpine \
  pg_isready -h db -U cloudops -d cloudops
Expected:
db:5432 - accepting connections

**11. Nginx**
Nginx acts as the reverse proxy.
Instead of accessing every service directly, users access:
http://SERVER_IP
Nginx routes requests to the correct container.
Conceptually:
Browser
   │
   ▼
Nginx :80
   │
   ├── /              → Web application
   │
   ├── /prometheus/  → Prometheus
   │
   └── /grafana/     → Grafana
   
**12. Monitoring**
Prometheus
Prometheus collects monitoring metrics.
The Prometheus configuration is located at:
monitoring/prometheus.yml
Prometheus runs inside Docker.
Typical internal port:
9090
Grafana
Grafana provides dashboards for monitoring.
Typical internal port:
3000
Grafana connects to Prometheus as a monitoring data source.

**13. AWS EC2 Deployment**
CloudOps can be deployed on an Ubuntu EC2 instance.
The general deployment process is:

AWS EC2
   ↓
Ubuntu
   ↓
Install Docker
   ↓
Clone GitHub repository
   ↓
Create .env
   ↓
Docker Compose
   ↓
Nginx
   ↓
Live Application

**14. EC2 Setup**
Connect to EC2 through SSH:
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
Clone the project:
git clone https://github.com/SREENITHA-V/CloudOps.git
Enter the project:
cd CloudOps
Create the environment file:
nano .env
Add the required environment variables.
Then start:
docker compose up -d --build
Check:
docker compose ps

**15. AWS Security Group**
For a public web application, the EC2 Security Group needs the appropriate inbound rules.
For example:
Type	Port	Purpose
SSH	22	Server administration
HTTP	80	Web application
SSH should preferably be restricted to your own IP rather than opened to everyone.

**16. Accessing the Live Application**
After Nginx and the containers are running:
http://YOUR_EC2_PUBLIC_IP
For example:
http://34.228.231.111
The exact IP can change if the EC2 instance is stopped and started unless an Elastic IP is used.

**17. CI/CD**
GitHub Actions is used to automate parts of the development workflow.
The general pipeline is:

Developer
    ↓
git push
    ↓
GitHub
    ↓
GitHub Actions
    ↓
Install Python
    ↓
Install dependencies
    ↓
Run tests
    ↓
Build Docker image
    ↓
Push image
    ↓
Deployment
The workflow files are located at:
.github/workflows/

**18. Git Commands**
Check repository status:
git status
Add changes:
git add .
Commit:
git commit -m "Update CloudOps deployment"
Push:
git push origin main
Pull latest changes:
git pull origin main

**19. Typical Development Workflow**
Whenever you make a change:

1. Modify code
       ↓
2. Test locally
       ↓
3. Build Docker image
       ↓
4. Run Docker Compose
       ↓
5. Test application
       ↓
6. git add .
       ↓
7. git commit
       ↓
8. git push
       ↓
9. GitHub Actions
       ↓
10. Deployment
    
**20. Troubleshooting Guide**
Problem: 502 Bad Gateway
CheCk:
docker compose ps
Then:
docker compose logs web --tail=50
If the web container is restarting, fix the web application first.
Nginx returning 502 usually means it cannot successfully reach the backend application.
Problem: Worker failed to boot

Run:
docker compose logs web --tail=100
Look for the first actual Python/SQLAlchemy error above the Gunicorn error.
Worker failed to boot is usually a consequence, not the root cause.
Problem: Name or service not known
First check Docker DNS:
docker run --rm --network cloudops_appnet alpine:3.20 getent hosts db
Then:
docker run --rm --network cloudops_appnet postgres:16-alpine pg_isready -h db -U cloudops -d cloudops
If both work, check DATABASE_URL.

Remember:
db
is the database hostname inside Docker Compose.
Do not replace it with:
localhost
Problem: YAML error

For example:
yaml: line 10: did not find expected key
Check the Compose file:
docker compose config
YAML depends on indentation.

Example:
services:
  web:
    build: .
    environment:
      DATABASE_URL: ${DATABASE_URL}

Not:
services:
  web:
    build: .
    environment:
    DATABASE_URL: ${DATABASE_URL}
Problem: Container keeps restarting
Check:
docker compose ps
Then:
docker compose logs <service-name> --tail=50
For example:
docker compose logs web --tail=50
Problem: PostgreSQL is not ready
Run:
docker compose exec db pg_isready -U cloudops -d cloudops
If it says:
accepting connections
PostgreSQL is running correctly.

**21. Important Things NOT to Do**
Don't use localhost for the database
Inside the web container:
localhost
means the web container itself.
Use:
db
Don't expose PostgreSQL unnecessarily
You don't need to expose port 5432 publicly to the Internet for the web application to use PostgreSQL.
The containers can communicate internally through Docker's network.
Don't commit .env
Never run:
git add .env
Instead:
.env
should be in .gitignore.
Don't delete Docker volumes unless you understand the consequence
Be careful with:
docker compose down -v
The -v option can remove persistent database volumes.
That can result in PostgreSQL data being deleted.

**22. Useful Verification Checklist**
Whenever CloudOps is deployed, run:
docker compose ps

Then:
docker compose logs web --tail=30

Then:
docker compose exec db pg_isready -U cloudops -d cloudops

Then test:
http://YOUR_EC2_PUBLIC_IP

Then monitoring:
http://YOUR_EC2_PUBLIC_IP/prometheus/
http://YOUR_EC2_PUBLIC_IP/grafana/

**23. Project Flow — Easy to Remember**
The entire project can be remembered as:
CODE
 │
 ▼
GITHUB
 │
 ▼
GITHUB ACTIONS
 │
 ├── TEST
 │
 ├── BUILD
 │
 └── PUSH
       │
       ▼
    DOCKER
       │
       ▼
 DOCKER COMPOSE
       │
 ┌─────┼─────────────┐
 ▼     ▼             ▼
WEB    DB        MONITORING
 │      │         │
 │      │      Prometheus
 │      │         │
 │      │       Grafana
 │      │
 └──────┴───────► NGINX
                    │
                    ▼
                 INTERNET

                 
**24. What This Project Demonstrates**
This project demonstrates practical experience with:
Linux server administration
Git and GitHub
Docker
Dockerfiles
Docker Compose
Container networking
PostgreSQL
Environment variables
Secrets management basics
Nginx reverse proxy
Prometheus
Grafana
GitHub Actions
CI/CD concepts
AWS EC2
Cloud deployment
Application troubleshooting
Database connectivity troubleshooting
Production-style service separation

**25. Future Improvements**
Possible next improvements:
Deploy using a managed PostgreSQL database
Add HTTPS using a domain and Let's Encrypt
Add Docker image versioning
Improve GitHub Actions deployment
Add automated EC2 deployment
Add application health checks
Add more Prometheus metrics
Create a professional Grafana dashboard
Add centralized logging
Add Kubernetes deployment
Add Terraform infrastructure-as-code
Add AWS load balancing
Add automatic rollback
Add vulnerability scanning for Docker images


**27. Quick Commands Cheat Sheet**
# Start
docker compose up -d --build
# Stop
docker compose down
# Status
docker compose ps
# Logs
docker compose logs web --tail=50
# Restart web
docker compose restart web
# Recreate web
docker compose up -d --force-recreate web
# Validate Compose
docker compose config
# Database health
docker compose exec db pg_isready -U cloudops -d cloudops
# Git status
git status
# Push changes
git add .
git commit -m "Update CloudOps"
git push origin main

**27. Final Project Summary**
CloudOps is a practical DevOps project that takes a web application from source code to a cloud-hosted, containerized, monitored application.
The core workflow is:
Develop
   ↓
Git
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Docker
   ↓
Docker Compose
   ↓
AWS EC2
   ↓
Nginx
   ↓
Web Application
   ↓
PostgreSQL

Monitoring:
Prometheus → Grafana

This README is intended to serve as the main reference whenever you return to the project, especially for remembering how the containers, database, networking, Nginx, monitoring, EC2 deployment, and CI/CD pieces fit together.
