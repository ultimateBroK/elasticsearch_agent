# 🚀 Elasticsearch Agent Setup Guide

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ (or Bun)
- Docker & Docker Compose
- Google Gemini API Key

## 🔧 Quick Start

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd elasticsearch-agent

# Generate and create all environment files
./scripts/setup-env.sh generate
./scripts/setup-env.sh create

# Edit with your actual API key
nano .env
# Set: GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Validate configuration
./scripts/setup-env.sh validate
```

### 2. Start Infrastructure
```bash
# Start Elasticsearch and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Backend Setup
```bash
cd backend

# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
```bash
cd frontend

# Install Bun (if not installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies
bun install

# Run development server
bun dev
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Elasticsearch**: http://localhost:9200

## 🔧 Environment Management

### Environment Files Structure
```
elasticsearch_agent/
├── .env.template          # Master template (single source of truth)
├── .env                   # Main environment file
├── backend/.env           # Backend-specific variables
└── frontend/.env.local    # Frontend-specific variables
```

### Environment Commands
```bash
# Generate all .env.example files
./scripts/setup-env.sh generate

# Create actual .env files
./scripts/setup-env.sh create

# Validate configuration
./scripts/setup-env.sh validate

# Clean environment files
./scripts/setup-env.sh clean
```

### Required Configuration
Edit `.env` and set:
```bash
# REQUIRED: Get your key from https://ai.google.dev/
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

## 🧪 Testing the Setup

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "elasticsearch": true,
    "redis": true,
    "gemini": true
  }
}
```

### 2. Sample Data
```bash
cd backend
uv run python scripts/ingest_sample_data.py
```

### 3. Test Chat
Open http://localhost:3000 and try:
- "Show me all data"
- "Create a bar chart of sales by region"
- "What's the total revenue?"

## 🚨 Troubleshooting

### Environment Issues
```bash
# Check if all environment files exist
./scripts/setup-env.sh validate

# Regenerate if needed
./scripts/setup-env.sh clean
./scripts/setup-env.sh generate
./scripts/setup-env.sh create
```

### Service Issues
```bash
# Check Docker services
docker-compose ps

# View logs
docker-compose logs elasticsearch
docker-compose logs redis

# Restart services
docker-compose restart
```

### Backend Issues
```bash
# Check backend logs
cd backend
uv run uvicorn main:app --reload --log-level debug

# Test Gemini API
uv run python scripts/test_gemini.py
```

### Frontend Issues
```bash
# Check frontend logs
cd frontend
bun dev

# Clear cache and rebuild
rm -rf .next node_modules
bun install
bun dev
```

## 📚 Additional Resources

- **Environment Guide**: [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)
- **API Documentation**: http://localhost:8000/docs
- **Project Plan**: [plan.md](plan.md)
- **Tech Stack**: [techstack.md](techstack.md)

## 🎉 Success!

If everything is working correctly, you should see:
- ✅ All health checks passing
- ✅ Frontend loading at http://localhost:3000
- ✅ Chat interface responding to queries
- ✅ Charts rendering properly

**Happy querying!** 🚀