# AI Assist Async Jamboree

A multi-application project featuring Flask and Tornado web applications with async communication capabilities.

## Applications

### Flask App (Port 5000)
- Web interface for interacting with the Tornado app
- Synchronous and asynchronous HTTP clients
- Frontend with Bootstrap UI

### Tornado App (Port 8888)
- Simple async web server
- Hello world endpoint

## Development Setup

### Prerequisites
- Python 3.12
- Pipenv
- Docker & Docker Compose (for containerized deployment)
- Claude Code CLI (optional, for AI-assisted development)

### Local Development

1. Install dependencies:
   ```bash
   pipenv install --dev
   ```

2. Activate virtual environment:
   ```bash
   pipenv shell
   ```

3. Run tests:
   ```bash
   PYTHONPATH=. pipenv run pytest -v
   ```

4. Start applications:
   ```bash
   # Terminal 1 - Tornado app
   python tornado_app/main.py
   
   # Terminal 2 - Flask app  
   python flask_app/flask_app.py
   ```

### AI Development with Claude Code

1. **Install Claude Code:**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Start Claude Code in project directory:**
   ```bash
   cd /path/to/ai_assist_async_jamboree
   claude
   ```

3. **Key features:**
   - Natural language commands for development tasks
   - Access to project structure and dependencies via `CLAUDE.md`
   - Code analysis and modification assistance
   - Integration with existing development workflows

## Docker Deployment

### Prerequisites: Docker Installation

**Linux:**
- Install Docker and Docker Compose from your package manager or [Docker's official documentation](https://docs.docker.com/engine/install/)
- Add your user to the docker group: `sudo usermod -aG docker $USER`
- Log out and back in for group permissions to take effect

**Windows:**
- Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Important:** Enable WSL 2 integration in Docker Desktop settings:
  1. Open Docker Desktop
  2. Go to Settings → Resources → WSL Integration
  3. Enable integration with your WSL 2 distro
  4. Apply & Restart

**macOS:**
- Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)

### Quick Start

Choose your environment:

**Development (with debugging):**
```bash
make dev
```
- Exposes debug ports 5678 (Flask) and 5679 (Tornado)
- Direct app access: http://localhost:5000, http://localhost:8888
- Nginx access: http://localhost:80

**Reference/Staging:**
```bash
make ref
```

**Production:**
```bash
make prod
```

**Access applications:**
- Flask App: http://localhost:80 (via nginx)
- Tornado App: http://localhost:80/tornado/ (via nginx)

### Services

- **nginx**: Reverse proxy (port 80)
  - Routes `/` to Flask app
  - Routes `/tornado/` to Tornado app
- **tornado-app**: Tornado application container (internal port 8888)
- **flask-app**: Flask application container (internal port 5000)
  - Depends on tornado-app
  - Pre-configured to communicate with tornado-app via internal network

### Docker Commands

**Environment Management:**
```bash
make dev         # Start development environment (with debug ports)
make ref         # Start reference/staging environment
make prod        # Start production environment
```

**General Commands (work with any environment):**
```bash
make down        # Stop all containers
make logs        # View logs
make restart     # Restart containers
make rebuild ENV=dev # Stop, rebuild, and start specific environment
make clean       # Clean up everything
```

**Testing:**
```bash
make test        # Run tests in containers
make test-integration # Run full integration test (start, test, stop)
```

**Setup:**
```bash
make dev-setup   # Setup local development environment
make help        # See all available commands
```

**Direct Docker commands:**
```bash
docker compose up --build        # Start services
docker compose up -d --build     # Start in background
docker compose logs -f           # View logs
docker compose down              # Stop services
docker compose restart           # Restart services
```

## Project Structure

```
├── flask_app/
│   ├── Dockerfile
│   ├── flask_app.py          # Main Flask application
│   ├── static/               # CSS, JS assets
│   ├── templates/            # HTML templates
│   └── tests/                # Flask app tests
├── tornado_app/
│   ├── Dockerfile
│   ├── main.py               # Main Tornado application
│   └── tests/                # Tornado app tests
├── nginx/
│   └── nginx.conf            # Reverse proxy configuration
├── docker-compose.yml        # Multi-container setup
├── Makefile                  # Docker management commands
├── Pipfile                   # Python dependencies
└── CLAUDE.md                 # Development guidance
```

## Development Workflow

### Environment Strategy
- **dev**: Development with debugging enabled, direct port access
- **ref**: Reference/staging environment for testing releases
- **prod**: Production environment with resource limits and scaling

### Image Tagging

**Default Tags by Environment:**
- `ai-assist-flask:dev`, `ai-assist-tornado:dev`
- `ai-assist-flask:ref`, `ai-assist-tornado:ref`  
- `ai-assist-flask:latest`, `ai-assist-tornado:latest`

**Setting Custom Image Tags:**

1. **Environment Variables:**
   ```bash
   IMAGE_TAG=v1.2.3 make up-prod
   FLASK_IMAGE=myregistry.com/flask:v1.2.3 make up-ref
   ```

2. **Using environment-specific .env files:**
   ```bash
   # Create environment-specific config files
   cp .env.example .env.dev
   cp .env.example .env.ref  
   cp .env.example .env.prod
   
   # Edit each file with appropriate image tags
   # Then run environment commands (automatically loads correct .env)
   make up-dev   # loads .env.dev
   make up-ref   # loads .env.ref
   make up-prod  # loads .env.prod
   ```

3. **For CI/CD deployments:**
   ```bash
   export IMAGE_TAG=v1.2.3
   export FLASK_IMAGE=myregistry.com/ai-assist-flask:v1.2.3
   export TORNADO_IMAGE=myregistry.com/ai-assist-tornado:v1.2.3
   make up-prod
   ```

### Development Setup

1. **Create environment config:**
   ```bash
   cp .env.dev.example .env.dev
   # Edit .env.dev as needed
   ```

2. **Setup VSCode debugging:**
   ```bash
   mkdir -p .vscode
   cp launch.json.example .vscode/launch.json
   ```

3. **Start development environment:**
   ```bash
   make dev
   ```

### Remote Debugging (VSCode)
1. Start development environment: `make dev`
2. In VSCode, use "Remote Debug: Flask Container" or "Remote Debug: Tornado Container" 
3. Apps wait for debugger connection on ports 5678/5679
4. Set breakpoints in your code and attach the debugger

### Testing

**Unit Tests:**
```bash
# Local testing (requires pipenv)
PYTHONPATH=. pipenv run pytest -v

# Container testing (requires services running)
make test
```

**Integration Testing:**
```bash
make test-integration
```

Integration tests verify:
- All services start correctly
- Nginx reverse proxy routing
- Inter-service communication
- Service health checks

## Features

- **Async Communication**: Flask app can make both sync and async requests to Tornado
- **Docker Networks**: Internal container communication
- **Nginx Reverse Proxy**: Route traffic to multiple services
- **Health Checks**: Both apps include health endpoints
- **Testing**: Comprehensive test suites for both applications
- **Integration Testing**: Full stack testing with automated service lifecycle
- **Development Tools**: VSCode launch configurations and settings