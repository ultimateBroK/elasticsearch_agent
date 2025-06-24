# 🚀 Elasticsearch Agent

> **AI-Powered Elasticsearch Data Analysis & Visualization Platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.3+-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your Elasticsearch data into actionable insights through natural language conversations. This intelligent agent combines the power of **LangGraph**, **Google Gemini AI**, and **modern web technologies** to create an intuitive interface for data exploration and visualization.

![Demo](https://via.placeholder.com/800x400/1f2937/ffffff?text=Elasticsearch+Agent+Demo)

## ✨ Key Features

### 🧠 **Intelligent Query Processing**
- **Natural Language Understanding**: Ask questions in plain English
- **Context-Aware Conversations**: Remembers previous interactions
- **Smart Query Generation**: Automatically creates optimized Elasticsearch queries
- **Semantic Search**: Learns from successful queries for better responses

### 📊 **Advanced Visualizations**
- **Dynamic Chart Generation**: Automatic chart type selection based on data
- **Interactive Dashboards**: Real-time updates with WebSocket connections
- **Multi-Chart Support**: Bar, line, pie, and custom visualizations
- **Smart Field Mapping**: Intelligent axis and data field suggestions

### ⚡ **High Performance**
- **Vector-Based Learning**: ChromaDB for semantic query matching
- **Intelligent Caching**: Redis-powered query and session caching
- **Real-Time Updates**: Live data synchronization via WebSockets
- **Optimized Stack**: UV (10-100x faster Python deps) + Bun (5x faster JS runtime)

### 🔧 **Enterprise Ready**
- **Scalable Architecture**: Microservices with FastAPI backend
- **Error Handling**: Comprehensive error recovery and user feedback
- **Health Monitoring**: Built-in service health checks
- **Development Tools**: Hot reload, comprehensive testing, and debugging

## 🎯 Use Cases

- **📈 Business Analytics**: "Show me sales trends by region this quarter"
- **🔍 Log Analysis**: "Find all errors in the last 24 hours"
- **📊 Data Exploration**: "Create a pie chart of user segments"
- **🚨 Monitoring**: "What's the average response time today?"
- **💡 Insights Discovery**: "Show me the top performing products"

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (or Bun)
- Docker & Docker Compose
- [Google Gemini API Key](https://ai.google.dev/) (Free tier available)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/elasticsearch_agent.git
cd elasticsearch_agent

# Generate environment files
./scripts/setup-env.sh generate
./scripts/setup-env.sh create

# Configure your API key
nano .env
# Set: GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### 2. Start Infrastructure

```bash
# Launch Elasticsearch & Redis
docker-compose up -d

# Verify services
docker-compose ps
```

### 3. Launch Backend

```bash
cd backend

# Install UV (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies & start server
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Launch Frontend

```bash
cd frontend

# Install Bun (if not installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies & start dev server
bun install
bun dev
```

### 5. Access Application

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API Docs**: http://localhost:8000/docs
- 🗄️ **Elasticsearch**: http://localhost:9200

## 🏗️ Architecture

```mermaid
graph TB
    %% Frontend Layer
    User["👤 User"] --> Chat["💬 Chat Interface"]
    Chat --> Store["🏪 Zustand Store"]
    Chat --> WS["🔌 WebSocket Hook"]
    Chat --> API["📡 REST API Client"]
    
    %% Communication Protocols
    WS -.->|Real-time| WSHandler["🔄 WebSocket Handler"]
    API -.->|HTTP/REST| Routes["🛣️ API Routes"]
    
    %% Backend Entry Points
    WSHandler --> DI["💉 Dependency Injection"]
    Routes --> DI
    
    %% Core Services (Managed by DI)
    DI --> Agent["🧠 LangGraph Agent"]
    DI --> ES_Service["🔍 Elasticsearch Service"]
    DI --> Gemini_Service["🤖 Gemini Service"]
    DI --> Redis_Service["💾 Redis Service"]
    DI --> Vector_Service["🧮 Vector DB Service"]
    
    %% Agent Workflow (LangGraph State Machine)
    Agent --> Workflow["⚙️ LangGraph Workflow"]
    Workflow --> GetIndices["📋 Get Indices"]
    GetIndices --> AnalyzeIntent["🎯 Analyze Intent"]
    AnalyzeIntent --> GenerateQuery["📝 Generate Query"]
    GenerateQuery --> ExecuteQuery["⚡ Execute Query"]
    ExecuteQuery --> GenerateResponse["📤 Generate Response"]
    
    %% External Services Integration
    ES_Service --> ES["🗄️ Elasticsearch Cluster"]
    Gemini_Service --> Gemini["🤖 Google Gemini API"]
    Redis_Service --> Redis["💾 Redis Cache"]
    Vector_Service --> Chroma["🧮 ChromaDB Vector Store"]
    
    %% Data Flow within Agent
    AnalyzeIntent -.->|"Semantic Search"| Vector_Service
    GenerateQuery -.->|"Cache Check"| Redis_Service
    AnalyzeIntent -.->|"Intent Analysis"| Gemini_Service
    GenerateQuery -.->|"Query Generation"| Gemini_Service
    ExecuteQuery -.->|"Data Retrieval"| ES_Service
    GenerateResponse -.->|"Response Generation"| Gemini_Service
    
    %% Infrastructure
    ES --> Docker1["🐳 Docker Container"]
    Redis --> Docker2["🐳 Docker Container"]
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef agent fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef infrastructure fill:#fafafa
    
    class User,Chat,Store,WS,API frontend
    class WSHandler,Routes,DI,ES_Service,Gemini_Service,Redis_Service,Vector_Service backend
    class Agent,Workflow,GetIndices,AnalyzeIntent,GenerateQuery,ExecuteQuery,GenerateResponse agent
    class ES,Gemini,Redis,Chroma external
    class Docker1,Docker2 infrastructure
```

### 🔄 **Detailed Flow Explanation**

#### **Frontend Architecture**
- **Chat Interface**: React component managing user interactions
- **Zustand Store**: Client-side state management for messages, sessions, and connection status
- **WebSocket Hook**: Real-time bidirectional communication with auto-reconnection
- **REST API Client**: Fallback HTTP communication with error handling

#### **Backend Architecture**
- **Dependency Injection**: Centralized service management and health monitoring
- **WebSocket Handler**: Real-time message processing with typing indicators
- **API Routes**: RESTful endpoints for HTTP-based operations
- **Service Layer**: Abstracted external service integrations

#### **LangGraph Agent Workflow**
1. **Get Indices**: Retrieve available Elasticsearch indices
2. **Analyze Intent**: 
   - Use ChromaDB for semantic similarity search
   - Leverage conversation context from Redis
   - Analyze user intent with Gemini AI
3. **Generate Query**: 
   - Check Redis cache for similar queries
   - Generate optimized Elasticsearch DSL with Gemini
4. **Execute Query**: Run query against Elasticsearch cluster
5. **Generate Response**: Create user-friendly response with optional chart configuration

#### **Service Integration**
- **Elasticsearch Service**: Direct cluster communication with connection pooling
- **Gemini Service**: AI-powered intent analysis and query generation
- **Redis Service**: Query caching and session management
- **Vector DB Service**: Semantic search and conversation memory using ChromaDB

### 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| **AI Agent** | [LangGraph](https://www.langchain.com/langgraph) | Workflow orchestration |
| **LLM** | [Google Gemini](https://ai.google.dev/) | Natural language processing |
| **Vector DB** | [ChromaDB](https://www.trychroma.com/) | Semantic search & learning |
| **Cache** | [Redis](https://redis.io/) | Query caching & sessions |
| **Search Engine** | [Elasticsearch](https://www.elastic.co/) | Data storage & retrieval |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | API server |
| **Frontend** | [Next.js](https://nextjs.org/) + [TailwindCSS](https://tailwindcss.com/) | Web interface |
| **Charts** | [Apache ECharts](https://echarts.apache.org/) | Data visualization |
| **State** | [Zustand](https://zustand-demo.pmnd.rs/) | Client state management |
| **Package Managers** | [UV](https://github.com/astral-sh/uv) + [Bun](https://bun.sh/) | Ultra-fast dependency management |

## 💬 Example Conversations

**User**: "Show me all data"
**Agent**: *Displays all available data with smart pagination*

**User**: "Create a bar chart of sales by region"
**Agent**: *Generates optimized ES query → Creates interactive bar chart*

**User**: "What's the total revenue this month?"
**Agent**: *Performs aggregation query → Returns formatted result*

**User**: "Show me errors from the last hour"
**Agent**: *Filters logs by timestamp and error level → Displays results*

## 📁 Project Structure

```
elasticsearch_agent/
├── 🖥️ backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/             # LangGraph agents
│   │   ├── services/           # ES, Redis, AI services
│   │   ├── api/               # REST & WebSocket routes
│   │   ├── models/            # Pydantic models
│   │   ├── core/              # Config & dependencies
│   │   └── utils/             # Helper functions
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Test suite
│   └── pyproject.toml         # Python dependencies
├── 🎨 frontend/                # Next.js frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── app/              # Next.js app router
│   │   ├── hooks/            # Custom React hooks
│   │   ├── store/            # Zustand stores
│   │   └── types/            # TypeScript definitions
│   └── package.json          # Node.js dependencies
├── 🗂️ docs/                   # Documentation
├── 🔧 scripts/                # Setup & utility scripts
├── 🐳 docker-compose.yml      # Infrastructure setup
└── 📋 README.md               # This file
```

## 🧪 Testing & Development

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Sample Data
```bash
cd backend
uv run python scripts/ingest_sample_data.py
```

### Run Tests
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
bun test
```

## 🚀 Deployment

### Development
- **Frontend**: `bun dev` (with hot reload)
- **Backend**: `uv run uvicorn main:app --reload`

### Production
- **Frontend**: Deploy to [Vercel](https://vercel.com/)
- **Backend**: Deploy to [Railway](https://railway.app/) or similar
- **Infrastructure**: Managed Elasticsearch + Redis services

## 📈 Performance Benefits

| Tool | Speed Improvement | Benefits |
|------|------------------|----------|
| **UV** | 10-100x faster than Poetry | Lightning-fast Python installs |
| **Bun** | 5x faster than npm | All-in-one JS runtime & bundler |
| **ChromaDB** | Vector similarity search | Intelligent query learning |
| **Redis** | In-memory caching | Sub-millisecond response times |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://www.langchain.com/langgraph) for workflow orchestration
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [Elasticsearch](https://www.elastic.co/) for search and analytics
- [FastAPI](https://fastapi.tiangolo.com/) for the robust API framework
- [Next.js](https://nextjs.org/) for the modern frontend framework

---

<div align="center">

**[🌟 Star this project](https://github.com/yourusername/elasticsearch_agent)** • **[📖 Read the docs](docs/)** • **[🐛 Report issues](https://github.com/yourusername/elasticsearch_agent/issues)**

*Built with ❤️ by [Hieu Nguyen](https://github.com/yourusername)*

</div>
