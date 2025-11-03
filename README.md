# Logistics AI Assistant - Complete Full-Stack Project

## 🎯 Project Overview

A complete logistics management system with AI-powered assistant that demonstrates all required skills for the Full-Stack Developer role.

**Live Demo Features:**
- ✅ Track shipments in real-time
- ✅ AI chatbot answers logistics questions using LangChain
- ✅ Interactive dashboard with React
- ✅ REST API with authentication
- ✅ Containerized with Docker
- ✅ CI/CD pipeline ready

---

## 📋 Tech Stack (Matches Job Requirements Exactly)

### Backend (Python)
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **JWT** - Authentication

### AI/LLM Integration
- **OpenAI API** - GPT-4 for intelligent responses
- **LangChain** - Agent framework with tools
- **ChromaDB** - Vector database for RAG
- **Python OpenAI SDK** - Direct API integration

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - API calls
- **React Router** - Navigation

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD pipeline
- **pytest** - Backend testing
- **Jest** - Frontend testing

---

## 🏗️ Project Structure

```
logistics-ai-assistant/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entry
│   │   ├── database.py        # DB connection
│   │   ├── config.py            
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   ├── ai/                # LangChain AI integration
│   │   └── utils/             # Helper functions
│   ├── tests/                 # pytest tests
│   ├── requirements.txt
|   |── dockerignore
│   └── Dockerfile
│
├── frontend/                   # React frontend
|   |── public/
|   |   |── index.html
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          
│   │   ├── index.css
|   |   |── index.tsx             
│   │   └── App.tsx            # Main app
│   ├── package.json
|   |── package-lock.json
|   |── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml         # Multi-container setup
├── .env.example        
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone https://github.com/NatalieCheong/logistics-ai-assistant.git
cd logistics-ai-assistant

# Create .env file
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 2. Run with Docker (Easiest)

```bash
# Start all services (backend, frontend, database)
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### 3. Run Locally (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations to create database tables
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## 🎓 Learning Path - How This Project Teaches Each Skill

### 1. Backend Python Development
**Files to Study:**
- `backend/app/main.py` - FastAPI setup, middleware, routing
- `backend/app/routers/shipments.py` - REST API endpoints
- `backend/app/models/shipment.py` - Database models
- `backend/app/utils/auth.py` - JWT authentication

**What You'll Learn:**
- FastAPI routing and dependency injection
- SQLAlchemy ORM and relationships
- Pydantic validation
- JWT authentication flow
- API best practices

### 2. OpenAI & LangChain Integration
**Files to Study:**
- `backend/app/ai/agent.py` - LangChain agent setup
- `backend/app/ai/tools.py` - Custom tools with @tool decorator
- `backend/app/ai/rag.py` - RAG system implementation
- `backend/app/routers/ai.py` - AI endpoints

**What You'll Learn:**
- OpenAI API usage (completions, embeddings)
- LangChain agent with tools
- RAG (Retrieval Augmented Generation)
- Function calling patterns
- Error handling for LLM APIs

### 3. Frontend React Development
**Files to Study:**
- `frontend/src/App.tsx` - Main app structure
- `frontend/src/components/ShipmentDashboard.tsx` - Main dashboard
- `frontend/src/components/AIChat.tsx` - Chat interface
- `frontend/src/services/api.ts` - API integration
- `frontend/src/hooks/useAuth.ts` - Authentication hook

**What You'll Learn:**
- React hooks (useState, useEffect, useContext)
- TypeScript in React
- API integration with axios
- State management
- Responsive design with Tailwind

### 4. DevOps & Deployment
**Files to Study:**
- `docker-compose.yml` - Multi-container setup
- `backend/Dockerfile` - Backend containerization
- `frontend/Dockerfile` - Frontend containerization
- `.github/workflows/ci-cd.yml` - CI/CD pipeline

**What You'll Learn:**
- Docker containerization
- Multi-container orchestration
- Environment variables
- CI/CD with GitHub Actions
- Production deployment patterns

---

## 📚 Key Features Explained

### Feature 1: Shipment Tracking API
**Endpoint:** `GET /api/shipments`

Shows your ability to:
- Design RESTful APIs
- Implement CRUD operations
- Handle pagination and filtering
- Write comprehensive tests

### Feature 2: AI Chatbot
**Endpoint:** `POST /api/ai/chat`

Demonstrates:
- LangChain agent integration
- OpenAI API usage
- Custom tool creation
- Real-time streaming responses

### Feature 3: RAG Document Search
**Endpoint:** `POST /api/ai/search`

Shows knowledge of:
- Vector databases (ChromaDB)
- Embeddings generation
- Semantic search
- Context retrieval for LLMs

### Feature 4: Authentication System
**Endpoints:** `POST /api/auth/login`, `POST /api/auth/register`

Demonstrates:
- JWT token generation
- Password hashing (bcrypt)
- Protected routes
- User session management

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

**Coverage includes:**
- API endpoint tests
- Authentication tests
- Database operation tests
- AI integration tests

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📖 API Documentation

Once running, visit: **http://localhost:8000/docs**

Interactive Swagger UI with all endpoints:
- Authentication endpoints
- Shipment CRUD operations
- Warehouse management
- AI chat endpoints
- Document search

---

## 🚢 Deployment

### Option 1: Docker Deployment (Any Cloud Provider)
```bash
docker-compose up -d
```

### Option 2: Cloud Deployment (AWS/GCP/Azure)

**Backend to AWS Elastic Beanstalk:**
```bash
eb init -p python-3.11 logistics-api
eb create production
eb deploy
```

**Frontend to Vercel:**
```bash
cd frontend
vercel deploy --prod
```

### Option 3: Kubernetes (Advanced)
```bash
kubectl apply -f k8s/
```

---

## 🎓 Next Steps After Building This

1. **Customize it:** Add features relevant to logistics (route optimization, real-time tracking)
2. **Add your touch:** Implement additional AI features, better UI/UX
3. **Deploy live:** Put it on a real domain so employers can access it

---

## 🤝 Contributing

This is a portfolio project template. Feel free to:
- Fork and customize for your needs
- Add features specific to your target role
- Improve and extend the AI capabilities

---

## 📄 License

MIT License - Use freely for your portfolio and learning

---

**Built by:** Natalie Cheong
**Date:** November 03 2025
**Purpose:** Full-Stack Developer Portfolio Project
