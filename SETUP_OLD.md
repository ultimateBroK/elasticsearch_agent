# 🚀 Elasticsearch Agent Setup Guide

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Google Gemini API Key

## ⚙️ Backend Setup

### 1. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_SCHEME=http

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Google Gemini API Configuration
GOOGLE_API_KEY=your_actual_api_key_here

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

### 2. Get Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### 3. Start Infrastructure Services

```bash
# Start Elasticsearch and Redis
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
curl http://localhost:9200/_cluster/health
```

### 4. Install Backend Dependencies

```bash
cd backend

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the backend
uv run python main.py
```

Backend will be available at: http://localhost:8000

## 🎨 Frontend Setup

```bash
cd frontend

# Install Bun (if not already installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies
bun install

# Start development server
bun dev
```

Frontend will be available at: http://localhost:3000

## 🗃️ Setup Sample Data

### Option 1: Via API

```bash
curl -X POST http://localhost:8000/api/v1/setup-sample-data
```

### Option 2: Via Python Script

```bash
cd backend
uv run python -m app.utils.sample_data
```

## 🧪 Test the Application

### Environment Variables Setup

**Frontend (.env.local):**
```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws" >> .env.local
```

### Testing Endpoints

1. **Health Check**: http://localhost:8000/api/v1/health
2. **API Docs**: http://localhost:8000/docs
3. **Frontend**: http://localhost:3000

### **🔗 WebSocket Testing**

```bash
# Test WebSocket connection in browser console:
const ws = new WebSocket('ws://localhost:8000/ws')
ws.onopen = () => console.log('🟢 WebSocket Connected')
ws.onmessage = (e) => console.log('📨 Message:', JSON.parse(e.data))
ws.send(JSON.stringify({type: 'message', message: 'Hello!', timestamp: new Date().toISOString()}))
```

### **🤖 Gemini API Testing**

```bash
# Test Gemini connection & setup
curl http://localhost:8000/api/v1/gemini/test

# Expected response:
{
  "status": "success",
  "message": "Gemini API connection successful",
  "api_key_prefix": "AIzaSyB...",
  "test_response": "Hello World",
  "model": "gemini-1.5-flash",
  "features_available": [
    "Intent Analysis",
    "Query Generation", 
    "Response Generation",
    "Vietnamese Support"
  ]
}

# Test intent analysis
curl -X POST http://localhost:8000/api/v1/gemini/analyze
```

### Sample Queries to Try:

- "Show me the latest sales data"
- "What are the top selling products?"
- "Create a chart of sales by region"
- "Show me error logs from last week"
- "Count total orders"

## 🎯 Features

### ✅ Currently Available:

- **Chat Interface**: Modern UI with real-time messaging
- **AI Agent**: LangGraph workflow with Google Gemini
- **Query Intelligence**: Natural language to Elasticsearch translation
- **Sample Data**: Sales and logs data for testing
- **Caching**: Redis-based query result caching
- **Health Monitoring**: Service status tracking

### 🚧 Coming Soon (Phase 2):

- **Chart Visualization**: ECharts integration
- **Advanced Queries**: Complex aggregations
- **Memory**: Conversation context
- **Chart Recommendations**: ML-based suggestions

## 🐛 Troubleshooting

### Backend Issues:

```bash
# Check logs
cd backend && uv run python main.py

# Test Elasticsearch
curl http://localhost:9200/_cluster/health

# Test Redis
redis-cli ping
```

### Frontend Issues:

```bash
# Clear cache and restart
cd frontend
rm -rf .next node_modules
bun install
bun dev
```

### Docker Issues:

```bash
# Restart services
docker-compose down
docker-compose up -d

# View logs
docker-compose logs elasticsearch
docker-compose logs redis
```

## 📁 Project Structure

```
elasticsearch_agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agents
│   │   ├── services/        # ES, Redis, Gemini services
│   │   ├── api/            # FastAPI routes
│   │   ├── models/         # Pydantic schemas
│   │   └── utils/          # Sample data & helpers
│   ├── main.py             # FastAPI application
│   └── pyproject.toml      # Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── store/         # Zustand state
│   │   └── lib/           # API client
│   └── package.json
├── docker-compose.yml      # Infrastructure
└── plan.md                # Development roadmap
```

## 🔧 Development

### Add New Query Patterns:

1. Update prompts in `app/services/gemini.py`
2. Extend agent logic in `app/agents/elasticsearch_agent.py`
3. Add new endpoints in `app/api/routes.py`

### Extend Sample Data:

1. Modify `app/utils/sample_data.py`
2. Add new indices and mappings
3. Generate relevant test data

---

**🎉 You're all set! Start chatting with your Elasticsearch data!** 