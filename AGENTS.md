# AGENTS.md

> **A README for AI Coding Assistants**
> This file guides AI agents on project scaffolding, development workflows, coding standards, and deployment practices for Python (Django/Flask), Node.js, and React applications.

---

## Table of Contents

- [Project Scaffolding](#project-scaffolding)
- [Spec-Driven Development](#spec-driven-development)
- [Tech Stack & Architecture](#tech-stack--architecture)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Docker & Deployment](#docker--deployment)
- [Git Workflow](#git-workflow)
- [Testing](#testing)
- [Security](#security)
- [AI Agent Instructions](#ai-agent-instructions)

---

## Project Scaffolding

### Quick Start: Scaffolding a New Project

When scaffolding a new project, **ALWAYS** create the following core files:

1. **`.gitignore`** - Environment-specific ignore patterns
2. **`.env.example`** - Template for environment variables (never commit `.env`)
3. **`docker-compose.yml`** - Production docker configuration
4. **`docker-compose.dev.yml`** - Development docker configuration with hot-reload
5. **`Dockerfile`** - Application container definition
6. **`Makefile`** - Common development commands
7. **`README.md`** - Project documentation
8. **`AGENTS.md`** - This file (copy to new projects)

### Architecture Defaults

**For ALL web applications, the default Docker Compose stack includes:**

1. **Main Application** - Django/Flask/Node.js/React app
2. **PostgreSQL** - Primary database (alternative: MySQL if specified)
3. **Redis** - Caching, session storage, and task queue backend
4. **Nginx** - Reverse proxy and load balancer

**Additional services (add when needed):**
- Celery Worker (Python async tasks)
- Celery Beat (Python scheduled tasks)
- RabbitMQ/Kafka (message queuing)
- Elasticsearch (search functionality)

---

## Spec-Driven Development

This repository now uses **GitHub Spec Kit** as the required workflow for non-trivial work.

### Mandatory Workflow

For any meaningful feature, behavioral change, refactor, schema change, payment-flow change,
integration change, admin workflow change, or security-sensitive update, agents **MUST**
use the Spec Kit flow before implementation:

1. `$speckit-constitution` - only when project-level engineering rules need to change
2. `$speckit-specify "<feature description>"`
3. `$speckit-clarify` - when ambiguity materially affects scope, UX, or security
4. `$speckit-plan`
5. `$speckit-checklist` and/or `$speckit-analyze` when the change has meaningful risk
6. `$speckit-tasks`
7. `$speckit-implement`

### Artifact Locations

- Constitution: `.specify/memory/constitution.md`
- Spec Kit scripts: `.specify/scripts/powershell/`
- Spec templates: `.specify/templates/`
- Feature artifacts: `specs/<number>-<short-name>/`
- Agent skills: `.agents/skills/`

### Enforcement Rules

- Do **not** jump straight to code for non-trivial work without the relevant Spec Kit artifacts.
- Specs and plans must explicitly address backward compatibility, payment/idempotency risk,
  security handling, and verification strategy when those concerns apply.
- Trivial changes may skip Spec Kit only if they are clearly non-behavioral
  (examples: typo fixes, comments, formatting-only edits, mechanical renames with no logic change).
- When Spec Kit is skipped, agents must say so explicitly and explain why the change qualifies.

---

## Tech Stack & Architecture

### Supported Frameworks

#### Python Backend
- **Django** - Full-stack web framework with ORM, admin panel, and auth
- **Flask** - Lightweight web framework for APIs and microservices
- **FastAPI** - Modern async API framework (preferred for new microservices)

#### Frontend
- **React** - Component-based UI library
- **Next.js** - React framework with SSR/SSG
- **Vite** - Fast build tool for modern web projects

#### Node.js Backend
- **Express.js** - Minimalist web framework
- **NestJS** - TypeScript framework with Angular-like architecture

### Database & Infrastructure
- **PostgreSQL 15+** - Primary relational database
- **Redis 7+** - Caching and session storage
- **Nginx** - Reverse proxy, load balancer, static file serving

---

## Development Environment

### Docker Development Setup

**CRITICAL REQUIREMENTS:**

1. **Hot-Reload in Development**
   - Django: Use `manage.py runserver` instead of Gunicorn
   - Flask: Use `flask run --debug`
   - Node.js: Use `nodemon` or framework's dev server
   - React: Use `npm start` or `vite dev`

2. **Volume Mounting**
   - Mount source code as volumes in `docker-compose.dev.yml`
   - Changes in local files should immediately reflect in containers

3. **Environment Files**
   - Development: `docker-compose.dev.yml` uses `.env.dev`
   - Production: `docker-compose.yml` uses `.env`
   - Always provide `.env.example` with placeholder values

### Makefile Commands

Every project **MUST** include a Makefile with these targets:

```makefile
# Development
make dev           # Start development environment
make build         # Build docker images
make logs          # Show logs
make shell         # Access application shell
make db-shell      # Access database shell

# Database
make migrate       # Run database migrations
make makemigrations # Create new migrations
make reset-db      # Reset database (DANGEROUS)

# Testing
make test          # Run all tests
make test-unit     # Run unit tests
make test-integration # Run integration tests
make coverage      # Generate test coverage report

# Code Quality
make lint          # Run linters
make format        # Auto-format code
make type-check    # Run type checkers

# Cleanup
make clean         # Remove cache and temp files
make down          # Stop all containers
make prune         # Remove all containers, volumes, images
```

---

## Coding Standards

### Python (Django/Flask)

**File Structure:**
```
project_name/
├── apps/               # Django apps or Flask blueprints
│   ├── users/
│   ├── api/
│   └── core/
├── config/             # Settings and configuration
├── tests/              # Test files
├── requirements/       # Split requirements (base, dev, prod)
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── manage.py           # Django management
└── wsgi.py             # WSGI entry point
```

**Code Style:**
- Follow **PEP 8** strictly
- Use **Black** for formatting (line length: 88)
- Use **isort** for import sorting
- Use **flake8** or **ruff** for linting
- Use **mypy** for type checking
- Use **type hints** for all function signatures

**Django Specific:**
- One app per feature/domain
- Keep models lean, use managers and querysets
- Use Django Rest Framework (DRF) for APIs
- Custom user model from the start
- Settings: split into `base.py`, `dev.py`, `prod.py`

**Flask Specific:**
- Use Blueprints for modular apps
- Application factory pattern
- Use Flask-Migrate for database migrations
- Use Marshmallow or Pydantic for serialization

**Example Code:**

```python
# Good: Type-hinted, clear, documented
from typing import Optional, List
from django.db import models

class Membership(models.Model):
    """Represents a user's membership in the brotherhood."""

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    tier = models.CharField(max_length=50, choices=MembershipTier.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'memberships'
        verbose_name_plural = 'Memberships'

    def calculate_benefits(self) -> List[str]:
        """Calculate available benefits based on tier."""
        # Implementation here
        pass
```

### JavaScript/TypeScript (React/Node.js)

**File Structure:**
```
src/
├── components/         # Reusable UI components
├── pages/             # Page components
├── hooks/             # Custom React hooks
├── services/          # API calls and business logic
├── utils/             # Utility functions
├── types/             # TypeScript types
├── styles/            # Global styles
└── tests/             # Test files
```

**Code Style:**
- Use **TypeScript** for all new projects
- Use **ESLint** + **Prettier** for linting/formatting
- Use **React functional components** with hooks (no class components)
- Use **named exports** over default exports
- Use **absolute imports** (configure paths in tsconfig.json)

**Example Code:**

```typescript
// Good: Typed, functional, clear
import { useState, useEffect } from 'react';
import type { User } from '@/types/user';
import { fetchUserData } from '@/services/api';

interface UserProfileProps {
  userId: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const data = await fetchUserData(userId);
        setUser(data);
      } catch (error) {
        console.error('Failed to load user:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [userId]);

  if (loading) return <LoadingSpinner />;
  if (!user) return <ErrorMessage />;

  return <div>{user.name}</div>;
};
```

### Naming Conventions

**Files:**
- Python: `snake_case.py`
- JavaScript/TypeScript: `camelCase.ts` or `PascalCase.tsx` (for components)
- CSS/SCSS: `kebab-case.css`

**Variables/Functions:**
- Python: `snake_case`
- JavaScript/TypeScript: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Classes/Components: `PascalCase`

**Git Branches:**
- Feature: `feature/user-authentication`
- Bugfix: `bugfix/fix-login-error`
- Hotfix: `hotfix/security-patch`
- Release: `release/v1.2.0`

---

## Docker & Deployment

### Dockerfile Best Practices

**Multi-stage builds:**
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "app:application"]
```

**Node.js Multi-stage:**
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### Frontend Public Environment Variables

**Critical rule for Next.js / Vite / browser bundles:**

- Variables exposed to browser code (`NEXT_PUBLIC_*`, `VITE_*`, etc.) must be available during the frontend image build, not only at container runtime.
- In `docker-compose.yml`, pass browser-facing variables through `build.args` to the image that runs `npm run build`.
- Also pass the same values through `environment` when server-side rendering or runtime server code reads them.
- If nginx is the image that builds or serves the frontend artifact, inject the values into that nginx/frontend build stage or generate a runtime config file with `envsubst`.
- Do not assume backend env files, nginx env, or reverse-proxy config will magically reach already-built frontend assets.
- Keep root `.env.example`, frontend `.env.example`, Dockerfile `ARG`/`ENV`, and compose `build.args` in sync.


### Docker Compose Structure

**Development (`docker-compose.dev.yml`):**
- Use volumes for hot-reload
- Expose all ports for debugging
- Use environment-specific settings (DEBUG=True)
- Include development tools (debuggers, profilers)

**Production (`docker-compose.yml`):**
- Use build caching
- Limit resource usage
- Use restart policies
- Health checks for all services
- Nginx reverse proxy

**Example Production Stack:**

```yaml
version: '3.9'

services:
  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 app:application
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app_network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=dbname
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/staticfiles:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    networks:
      - app_network

volumes:
  postgres_data:
  redis_data:
  static_volume:

networks:
  app_network:
    driver: bridge
```

### Nginx Configuration

**Default reverse proxy config:**

```nginx
upstream web_backend {
    server web:8000;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://web_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/mediafiles/;
    }
}
```

---

## Git Workflow

### Commit Messages

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add JWT authentication

Implement JWT-based authentication with refresh tokens.
Includes login, logout, and token refresh endpoints.

Closes #123
```

```
fix(api): handle null values in serializer

Previous implementation crashed when encountering null.
Added validation and default value handling.
```

### Branching Strategy

**Main branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features

**Supporting branches:**
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes
- `release/*` - Release preparation

**Workflow:**
1. Create feature branch from `develop`
2. Implement and test feature
3. Create pull request to `develop`
4. Code review and approval
5. Merge to `develop`
6. Create release branch for deployment
7. Merge release to `main` and tag version

---

## Testing

### Python Testing

**Framework:** pytest

**Structure:**
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── e2e/              # End-to-end tests
├── fixtures/         # Test fixtures
└── conftest.py       # Pytest configuration
```

**Coverage:** Minimum 80% coverage required

**Example:**
```python
import pytest
from app.models import User

@pytest.fixture
def test_user():
    return User.objects.create(email="test@example.com")

def test_user_creation(test_user):
    assert test_user.email == "test@example.com"
    assert test_user.is_active is True
```

### JavaScript/TypeScript Testing

**Frameworks:**
- **Jest** - Unit testing
- **React Testing Library** - Component testing
- **Cypress** or **Playwright** - E2E testing

**Coverage:** Minimum 80% coverage required

**Example:**
```typescript
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('renders user name', () => {
    render(<UserProfile userId="123" />);
    expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
  });
});
```

---

## Security

### Critical Security Rules

**NEVER commit:**
- `.env` files with real credentials
- API keys, tokens, passwords
- Private keys or certificates
- Database dumps with real data

**ALWAYS:**
- Use environment variables for secrets
- Validate and sanitize all user input
- Use parameterized queries (prevent SQL injection)
- Implement CSRF protection
- Use HTTPS in production
- Keep dependencies updated (run `npm audit` / `pip-audit`)
- Implement rate limiting on APIs
- Use secure password hashing (bcrypt, Argon2)

**Django Security Checklist:**
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

**Environment Variables Template:**
```env
# .env.example
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## AI Agent Instructions

### Spec-Driven Delivery (Required)

For any non-trivial feature, architectural change, cross-cutting refactor,
workflow change, or behavior-changing bug fix:

1. **Start in Spec Kit first**
   - Use the repository's Spec Kit workflow before writing implementation code
   - Treat artifacts in `specs/<NNN-short-name>/` as the source of truth for scope and execution

2. **Use the repo-local Codex skills**
   - Run `$speckit-specify` to create the numbered feature branch and `spec.md`
   - Run `$speckit-plan` before implementation
   - Run `$speckit-tasks` before substantial implementation work
   - Run `$speckit-implement` when executing the planned work

3. **Keep governance in sync**
   - If delivery rules change, update `.specify/memory/constitution.md`
   - If agent workflow changes, update `AGENTS.md` and `README.md` in the same change set


### Project Initialization

When asked to scaffold a new project:

1. **Ask clarifying questions:**
   - Project type (Django, Flask, React, Node.js)?
   - Database preference (PostgreSQL, MySQL)?
   - Need Celery/background tasks?
   - Need Nginx reverse proxy?
   - Authentication method (JWT, sessions)?

2. **Create core files in this order:**
   - `.gitignore` (use framework-specific templates)
   - `README.md` (with project description and setup instructions)
   - `.env.example` (with all required variables)
   - `Dockerfile` (multi-stage if applicable)
   - `docker-compose.yml` (production)
   - `docker-compose.dev.yml` (development with hot-reload)
   - `Makefile` (with standard commands)
   - `requirements.txt` or `package.json`
   - Framework-specific files (manage.py, app.py, index.ts)
   - Initialize GitHub Spec Kit for Codex after the core files exist:
     `uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai codex --ai-skills --script ps

3. **Set up default services:**
   - Application container
   - PostgreSQL with health checks
   - Redis with persistence
   - Nginx (if web app)

4. **Verify hot-reload works:**
   - Test that code changes reflect without rebuild
   - Confirm volume mounts are correct

### Code Modification

When modifying existing code:

1. **Use Spec Kit first for non-trivial work** - Run the required GitHub Spec Kit workflow before implementation unless the change is explicitly trivial/non-behavioral
2. **Read files first** - Never propose changes without reading the current code
3. **Understand context** - Review related files and dependencies
4. **Follow existing patterns** - Match the project's style and structure
5. **Minimize changes** - Only modify what's necessary
6. **Test your changes** - Verify the code works
7. **Update documentation** - Keep README, spec artifacts, and comments current when behavior changes

### Code Quality

**Before marking task complete:**
- [ ] Relevant Spec Kit artifacts created/updated when required
- [ ] Code follows style guide (PEP 8, ESLint)
- [ ] Type hints/TypeScript types added
- [ ] No security vulnerabilities introduced
- [ ] Tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation updated
- [ ] No secrets in code
- [ ] Environment variables used correctly

### Forbidden Actions

**DO NOT:**
- Implement non-trivial features directly without the required Spec Kit artifacts
- Commit `.env` files
- Use `--force` in git commands without explicit permission
- Delete production databases
- Modify migrations that are already applied
- Skip migrations in production
- Use `DEBUG=True` in production
- Expose sensitive data in logs
- Create overly complex abstractions
- Add unnecessary dependencies
- Implement features not requested

### Communication Style

- Be concise and specific
- Ask questions when requirements are unclear
- Explain trade-offs when multiple approaches exist
- Provide code examples in responses
- Reference file paths and line numbers
- Suggest improvements only when asked

---

## Quick Reference

### Common .gitignore Patterns

```gitignore
# Python
*.py[cod]
__pycache__/
.venv/
*.egg-info/
.pytest_cache/

# Node.js
node_modules/
npm-debug.log
.env.local

# IDEs
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.log

# Docker
docker-compose.override.yml
```

### Environment Variables Checklist

Every `.env.example` should include:

```env
# Application
DEBUG=False
SECRET_KEY=change-me-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@db:5432/dbname
DB_NAME=dbname
DB_USER=user
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Email (if needed)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-password

# Cloud Storage (if needed)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
```

---

## Resources & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Spec Kit Repository](https://github.com/github/spec-kit)
- [Spec Kit Documentation](https://github.github.com/spec-kit/)
- [AGENTS.md Specification](https://agents.md/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Last Updated:** 2026-05-19
**Version:** 1.1.0

---

## Notes

This AGENTS.md file should be copied to the root of every new project and customized as needed. Keep it updated as the project evolves and team practices change. Treat this file like CI/CD configuration - review it in every PR that changes build, test, or deployment behavior.
