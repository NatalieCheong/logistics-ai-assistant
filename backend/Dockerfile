# backend/Dockerfile
"""
Multi-stage Docker build for FastAPI backend
"""

# Stage 1: Base image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development image
FROM base as development

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with auto-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production image
FROM base as production

# Copy only necessary files
COPY ./app /app/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run with optimized settings for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# =====================================================
# backend/requirements.txt
# =====================================================

# FastAPI and server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# OpenAI and LangChain
openai==1.3.7
langchain==0.1.0
langchain-openai==0.0.2
chromadb==0.4.18
tiktoken==0.5.2

# Document processing
pypdf==3.17.1
python-docx==1.1.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# =====================================================
# docker-compose.yml
# =====================================================
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: logistics_db
    environment:
      POSTGRES_USER: logistics_user
      POSTGRES_PASSWORD: logistics_password
      POSTGRES_DB: logistics_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U logistics_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: logistics_api
    environment:
      - DATABASE_URL=postgresql://logistics_user:logistics_password@postgres:5432/logistics_db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-in-production}
      - ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
      - DEBUG=True
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - chroma_data:/app/chroma_db
    depends_on:
      postgres:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: logistics_frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    stdin_open: true
    tty: true

volumes:
  postgres_data:
  chroma_data:

# =====================================================
# .env.example
# =====================================================

# Application
APP_NAME=Logistics AI Assistant
DEBUG=True

# Database
DATABASE_URL=postgresql://logistics_user:logistics_password@localhost:5432/logistics_db

# Security
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# =====================================================
# .dockerignore
# =====================================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Misc
*.log
.DS_Store
chroma_db/
