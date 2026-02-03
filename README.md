# Blu-Reserve 🍽️

**A Touchless Corporate Cafeteria Booking System**

Blu-Reserve is a capacity management tool designed for the post-COVID workplace. It allows employees to reserve specific seats in the cafeteria, ensuring social distancing and equitable access to office resources.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Environment Variables](#-environment-variables)
- [Setup & Installation](#-setup--installation)
- [Running the Project](#-running-the-project)
- [Running with Containers](#-running-with-containers)
- [Testing](#-testing)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Deployment](#-deployment)
- [Contribution Guidelines](#-contribution-guidelines)
- [Limitations & Assumptions](#-limitations--assumptions)
- [License](#-license)

---

## 🎯 Overview

Blu-Reserve provides an interactive web-based platform where employees can:
- View available cafeteria seats through an interactive map
- Reserve seats with proximity to colleagues
- Automatically release seats after 45 minutes to optimize capacity
- Track bookings through a "Blu Dollar" billing system charged to manager cost centers

The system features a simulated SSO login flow (accepts any `@ibm.com` email) and includes smart seat assignment algorithms.

---

## ✨ Key Features

* **Interactive Seat Map:** Visual layout with 100 seats divided into 4 Dining Zones (Coffee, Pizza, Asian, Salad)
* **Smart Assign AI:** One-click algorithm to automatically find the best available seat
* **Friend Finder:** Search for colleagues by **Name** or **IBM Email** to book a seat near them
* **Simulated SSO:** Mimics IBM w3id login flow (accepts any valid `@ibm.com` email)
* **Auto-Release Logic:** Seats automatically vacated if occupied for more than **45 minutes**
* **Blu Dollar Billing:** Bookings are "charged" (5 tokens) to the manager's cost center
* **Real-time Updates:** Seat status updates reflecting current availability

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React.js 19.x
- **Build Tool:** Vite 7.x
- **Styling:** Tailwind CSS 3.x
- **HTTP Client:** Axios 1.x
- **Testing:** Vitest 4.x, Testing Library

### Backend
- **Framework:** Python FastAPI 0.128.x
- **Web Server:** Uvicorn 0.39.x
- **Database:** MongoDB (via Motor async driver 3.4.x)
- **Authentication:** Custom session-based auth
- **Testing:** Pytest 8.x

### DevOps & Infrastructure
- **Containerization:** Podman/Docker
- **Container Orchestration:** Podman Compose
- **CI/CD:** Jenkins with Podman agent
- **Deployment:** OpenShift (Kubernetes)
- **Container Registry:** Quay.io
- **Web Server (Production):** Nginx (for frontend static assets)

---

## 📂 Project Structure

```
dummyproject/
├── backend/                      # FastAPI backend application
│   ├── main.py                   # Main API logic (seats, booking, release)
│   ├── auth.py                   # Authentication routes & middleware
│   ├── schemas.py                # Pydantic data models
│   ├── test_main.py              # Pytest unit tests
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend container build
│   └── .dockerignore             # Docker ignore patterns
│
├── frontend/                     # React.js frontend application
│   ├── src/
│   │   ├── App.jsx               # Main React component with seat map logic
│   │   ├── App.css               # Component-level styles
│   │   ├── login.jsx             # Login page component
│   │   ├── main.jsx              # React app entry point
│   │   ├── index.css             # Global styles (Tailwind imports)
│   │   ├── App.test.jsx          # Component tests
│   │   └── setupTests.js         # Test environment setup
│   ├── public/                   # Static assets
│   ├── package.json              # Node.js dependencies & scripts
│   ├── vite.config.js            # Vite build configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── nginx.conf                # Nginx production server config
│   ├── Dockerfile                # Frontend container build (multi-stage)
│   └── .dockerignore             # Docker ignore patterns
│
├── openshift/                    # OpenShift/Kubernetes deployment configs
│   ├── namespace.yaml            # Project namespace definition
│   ├── backend-deployment.yaml   # Backend deployment & pod spec
│   ├── backend-service.yaml      # Backend service (ClusterIP)
│   ├── frontend-deployment.yaml  # Frontend deployment & pod spec
│   ├── frontend-service.yaml     # Frontend service
│   ├── route.yaml                # OpenShift route (external access)
│   ├── configmap.yaml            # Environment variables config
│   ├── secret.yaml               # Sensitive credentials
│   ├── imagestream.yaml          # Image stream for builds
│   ├── rbac.yaml                 # Role-based access control
│   └── DEPLOYMENT_GUIDE.md       # OpenShift deployment instructions
│
├── jenkins/                      # Jenkins CI/CD setup files
│   ├── jenkins-setup.sh          # Jenkins installation script
│   ├── podman-agent-setup.sh     # Configure Podman agent
│   └── credentials-template.txt  # Jenkins credentials template
│
├── scripts/                      # Deployment automation scripts
│   ├── deploy.sh                 # Automated deployment script
│   ├── health-check.sh           # Application health verification
│   ├── rollback.sh               # Rollback to previous deployment
│   └── cleanup.sh                # Clean up resources
│
├── Jenkinsfile                   # Jenkins pipeline definition (CI/CD)
├── podman-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variables template
├── .env.production               # Production environment config
├── BUILD_INSTRUCTIONS.md         # Container build instructions
├── JENKINS_SETUP_GUIDE.md        # Jenkins setup documentation
├── package.json                  # Root-level shared dependencies
├── .gitignore                    # Git ignore patterns
├── LICENSE                       # Project license
└── README.md                     # This file

```

---

## 📦 Prerequisites

### For Local Development

- **Python:** 3.9+ (for backend)
- **Node.js:** 18.x or higher (for frontend)
- **MongoDB:** 6.0+ (Community Edition)
- **Package Managers:** pip, npm

### For Container Development

- **Podman:** 4.x or Docker 20.x+
- **Podman Compose:** 1.0.x or Docker Compose 2.x+

### For CI/CD & Deployment

- **Jenkins:** 2.x with Podman agent
- **OpenShift CLI:** `oc` 4.x+ (for Kubernetes deployment)
- **Container Registry Access:** Quay.io or equivalent
- **MongoDB:** Hosted instance or cluster deployment

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure the following:

### Backend Configuration
```bash
BACKEND_PORT=8000                 # Backend API port
PYTHONUNBUFFERED=1                # Python logging mode
MONGO_URL=mongodb://localhost:27017  # MongoDB connection string
SESSION_SECRET=your-secret-key    # Session encryption key
```

### Frontend Configuration
```bash
FRONTEND_PORT=8080                # Frontend dev server port
VITE_API_URL=http://localhost:8000  # Backend API endpoint
```

### Container Registry (for CI/CD)
```bash
REGISTRY_URL=quay.io              # Container registry URL
REGISTRY_NAMESPACE=your-namespace # Your registry namespace
IMAGE_TAG=latest                  # Image version tag
```

### OpenShift Configuration
```bash
OPENSHIFT_PROJECT=blu-reserve     # OpenShift project name
OPENSHIFT_REGISTRY=image-registry.openshift-image-registry.svc:5000
```

**⚠️ Important:** Never commit `.env` files with real credentials to version control.

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dummyproject
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. MongoDB Setup (macOS)

```bash
# Install MongoDB via Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Verify MongoDB is running
mongosh
# Type 'exit' to leave the shell
```

For other operating systems, refer to the [official MongoDB installation guide](https://docs.mongodb.com/manual/installation/).

---

## ▶️ Running the Project

### Local Development Mode

#### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload
```

Backend will be available at: **http://localhost:8000**

#### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### Access the Application

1. Navigate to `http://localhost:5173`
2. Login with any `@ibm.com` email (e.g., `john.doe@ibm.com`)
3. Start booking seats!

---

## 🐳 Running with Containers

### Option 1: Using Podman Compose (Recommended)

```bash
# Build and start all services
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down
```

Application will be available at:
- **Frontend:** http://localhost:8080
- **Backend:** http://localhost:8000

### Option 2: Manual Container Build

```bash
# Build backend image
podman build -t blu-reserve-backend:latest -f backend/Dockerfile backend/

# Build frontend image
podman build -t blu-reserve-frontend:latest -f frontend/Dockerfile frontend/

# Run backend container
podman run -d -p 8000:8000 --name backend blu-reserve-backend:latest

# Run frontend container
podman run -d -p 8080:8080 --name frontend blu-reserve-frontend:latest
```

### Health Checks

The containers include built-in health checks:
- **Backend:** Checks `/seats` endpoint every 30s
- **Frontend:** Checks root path every 30s

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest test_main.py -v
```

Tests cover:
- API endpoint functionality
- Seat booking logic
- Authentication flows
- Auto-release mechanisms

### Frontend Tests

```bash
cd frontend
npm run test
```

Tests use Vitest and React Testing Library for component testing.

---

## 🔄 CI/CD Pipeline

The project uses **Jenkins** for continuous integration and deployment.

### Pipeline Stages

1. **Checkout:** Pull latest code from Git
2. **Build Backend:** Create backend container image
3. **Build Frontend:** Create frontend container image
4. **Push Images:** Push to container registry (Quay.io)
5. **Deploy:** Deploy containers using podman-compose
6. **Health Check:** Verify application endpoints

### Jenkins Configuration

```bash
# Setup Jenkins and Podman agent
cd jenkins
./jenkins-setup.sh
./podman-agent-setup.sh
```

**Required Jenkins Credentials:**
- `container-registry-url`: Your registry URL (e.g., quay.io)
- `registry-credentials`: Username and password for registry

### Triggering Builds

The Jenkinsfile is configured for:
- Manual builds via Jenkins UI
- Webhook triggers from Git commits
- Scheduled builds (if configured)

### Viewing Pipeline

Access your Jenkins instance and navigate to the pipeline dashboard to monitor build progress.

---

## 🚀 Deployment

### OpenShift/Kubernetes Deployment

#### Prerequisites
- OpenShift CLI (`oc`) installed
- Access to OpenShift cluster
- Container images pushed to registry

#### Quick Deploy

```bash
# Login to OpenShift
oc login https://api.your-cluster.com:6443 --token=<your-token>

# Run deployment script
./scripts/deploy.sh
```

#### Manual Deployment

```bash
cd openshift

# Create namespace
oc apply -f namespace.yaml

# Create secrets and configmaps
oc apply -f secret.yaml
oc apply -f configmap.yaml

# Deploy backend
oc apply -f backend-deployment.yaml
oc apply -f backend-service.yaml

# Deploy frontend
oc apply -f frontend-deployment.yaml
oc apply -f frontend-service.yaml

# Create route for external access
oc apply -f route.yaml
```

#### Verify Deployment

```bash
# Check pods status
oc get pods

# Check services
oc get svc

# View application logs
oc logs -f deployment/blu-reserve-backend
oc logs -f deployment/blu-reserve-frontend
```

#### Health Check & Rollback

```bash
# Run health check
./scripts/health-check.sh

# Rollback if needed
./scripts/rollback.sh
```

#### Cleanup

```bash
# Remove all resources
./scripts/cleanup.sh
```

---

## 🤝 Contribution Guidelines

We welcome contributions! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes: `git commit -m "Add: description of changes"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Submit a Pull Request

### Code Standards

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions/classes
- Maintain test coverage above 80%

#### JavaScript (Frontend)
- Use ESLint configuration provided
- Follow React best practices
- Use functional components with hooks
- Write meaningful component tests

### Commit Messages

Use conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### Testing Requirements

- All new features must include tests
- Ensure existing tests pass: `pytest` (backend) and `npm test` (frontend)
- Add integration tests for new API endpoints

### Pull Request Process

1. Update README.md if adding new features
2. Ensure Docker/Podman builds succeed
3. Add screenshots for UI changes
4. Reference related issues in PR description
5. Request review from maintainers

---

## ⚠️ Limitations & Assumptions

### Current Limitations

1. **Authentication:**
   - Uses simulated SSO (accepts any `@ibm.com` email)
   - No real IBM w3id integration
   - Session-based auth (not suitable for distributed deployments without session store)

2. **Database:**
   - No MongoDB replica set configuration in current setup
   - Auto-release logic depends on booking time (not real-time)
   - No database backups configured

3. **Scalability:**
   - Backend is stateful (sessions stored in-memory)
   - No horizontal scaling support without external session store
   - Single MongoDB instance (not production-ready)

4. **Features:**
   - No email notifications for bookings
   - No admin dashboard for seat management
   - No reporting/analytics features
   - Friend search is basic (no fuzzy matching)

5. **Security:**
   - Session secrets are environment-based (rotate regularly)
   - No rate limiting implemented
   - CORS configured for localhost only

### Assumptions

- MongoDB is running and accessible at configured URL
- Users have valid `@ibm.com` email addresses
- Cafeteria has exactly 100 seats
- Seat cost is fixed at 5 Blu Dollars
- Auto-release timer is 45 minutes for all bookings
- Application runs in trusted network environment
- Container registry credentials are properly configured
- OpenShift cluster has sufficient resources

### Known Issues

- Auto-release requires periodic cleanup job (not automated)
- Session middleware may cause issues in load-balanced environments
- Frontend assumes backend is always available (no offline mode)

### Future Enhancements

- Integrate with real IBM w3id SSO
- Add Redis for distributed session management
- Implement WebSocket for real-time seat updates
- Add email notifications via SMTP
- Create admin panel for configuration
- Add metrics and monitoring (Prometheus/Grafana)
- Implement database migrations (Alembic)

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For questions or issues:
1. Check existing documentation in `/openshift/DEPLOYMENT_GUIDE.md`
2. Review build instructions in `BUILD_INSTRUCTIONS.md`
3. Open an issue in the repository
4. Contact the development team

---

**Built with ❤️ for safer workplace collaboration**
