# Elasticsearch Agent Backend

## 🏗️ Architecture

The backend is built with modern Python patterns and follows clean architecture principles:

```
backend/
├── app/
│   ├── core/                 # Core application components
│   │   ├── config.py        # Configuration management with Pydantic
│   │   ├── constants.py     # Application constants and enums
│   │   ├── dependencies.py  # Dependency injection system
│   │   ├── exceptions.py    # Custom exception classes
│   │   └── middleware.py    # Custom middleware
│   ├── services/            # External service integrations
│   │   ├── elasticsearch.py # Elasticsearch operations
│   │   ├── gemini.py       # Google Gemini LLM integration
│   │   └── redis.py        # Redis caching and sessions
│   ├── agents/             # LangGraph AI agents
│   │   └── elasticsearch_agent.py
│   ├── api/                # FastAPI routes and WebSocket
│   │   ├── routes.py       # REST API endpoints
│   │   └── websocket.py    # WebSocket handlers
│   ├── models/             # Pydantic data models
│   │   └── schemas.py      # Request/response schemas
│   └── utils/              # Utility functions
│       ├── logging.py      # Logging configuration
│       └── sample_data.py  # Test data utilities
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/              # End-to-end tests
└── scripts/               # Utility scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager
- Docker (for Elasticsearch and Redis)

### Setup
```bash
# Install dependencies
uv sync

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start infrastructure
docker-compose up -d

# Run the application
uv run uvicorn main:app --reload
```

## 🔧 Configuration

Configuration is managed through Pydantic settings in `app/core/config.py`:

```python
from app.core.config import settings

# Access configuration
print(settings.elasticsearch_url)
print(settings.google_api_key)
```

## 🏛️ Design Patterns

### Dependency Injection
Services are injected through FastAPI's dependency system:

```python
@router.get("/health")
async def health_check(
    es_service: ElasticsearchService = Depends(get_elasticsearch_service)
):
    return await es_service.health_check()
```

### Exception Handling
Custom exceptions with proper HTTP status codes:

```python
from app.core.exceptions import ValidationError

if not data:
    raise ValidationError("Data is required")
```

### Service Layer
All external integrations are abstracted through service classes:

```python
# Elasticsearch operations
result = await es_service.simple_search(index="logs", query=query)

# Redis caching
await redis_service.cache_query_result(hash, result)

# Gemini LLM
response = await gemini_service.generate_content(prompt)
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## 📊 API Endpoints

### Health Check
- `GET /api/v1/health` - Service health status

### Elasticsearch
- `GET /api/v1/elasticsearch/info` - Cluster information
- `GET /api/v1/elasticsearch/indices` - List indices
- `POST /api/v1/elasticsearch/query` - Execute query

### Chat
- `POST /api/v1/chat` - Chat with AI agent
- `GET /api/v1/session/{id}` - Get session data
- `DELETE /api/v1/session/{id}` - Delete session

### WebSocket
- `WS /ws` - Real-time chat communication

## 🔍 Monitoring

The application includes comprehensive logging and health checks:

```python
# Health check all services
GET /api/v1/health

# Response
{
  "status": "healthy",
  "services": {
    "elasticsearch": true,
    "redis": true,
    "gemini": true
  }
}
```

## 🛠️ Development

### Adding New Services
1. Create service class in `app/services/`
2. Add to dependency injection in `app/core/dependencies.py`
3. Use in routes with `Depends(get_your_service)`

### Adding New Routes
1. Add route function in `app/api/routes.py`
2. Use dependency injection for services
3. Add proper error handling and validation

### Environment Variables
All configuration is managed through environment variables:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional (with defaults)
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
```