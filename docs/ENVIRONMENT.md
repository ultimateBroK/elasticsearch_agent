# 🔧 Environment Configuration Guide

## 📋 Overview

This project uses a **centralized environment management system** to avoid duplication and ensure consistency across all components.

## 🏗️ Environment File Structure

```
elasticsearch_agent/
├── .env.template          # 📝 Master template (single source of truth)
├── .env.example          # 📄 Generated from template
├── .env                  # 🔒 Your actual environment (gitignored)
├── backend/
│   ├── .env.example      # 📄 Generated backend-specific variables
│   └── .env              # 🔒 Backend environment (gitignored)
├── frontend/
│   ├── .env.example      # 📄 Generated frontend-specific variables
│   └── .env.local        # 🔒 Frontend environment (gitignored)
└── scripts/
    └── setup-env.sh      # 🛠️ Environment management script
```

## 🚀 Quick Start

### 1. Generate Environment Files
```bash
# Generate all .env.example files from master template
./scripts/setup-env.sh generate

# Create actual .env files from examples
./scripts/setup-env.sh create
```

### 2. Configure Your Environment
```bash
# Edit the main environment file
nano .env

# Set your Google Gemini API key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Validate Configuration
```bash
# Check if all environment files are properly configured
./scripts/setup-env.sh validate
```

## 🔧 Environment Management Commands

### Generate Files
```bash
./scripts/setup-env.sh generate
```
- Regenerates all `.env.example` files from `.env.template`
- Use this when you update the master template

### Create Environment Files
```bash
./scripts/setup-env.sh create
```
- Creates actual `.env` files from examples (if they don't exist)
- Safe to run multiple times (won't overwrite existing files)

### Validate Configuration
```bash
./scripts/setup-env.sh validate
```
- Checks if all required environment files exist
- Warns about missing API keys or configuration issues

### Clean Environment Files
```bash
./scripts/setup-env.sh clean
```
- Removes generated `.env.example` files
- Optionally removes actual `.env` files

## 📝 Environment Variables Reference

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSy...` |

### Infrastructure
| Variable | Description | Default |
|----------|-------------|---------|
| `ELASTICSEARCH_HOST` | Elasticsearch hostname | `localhost` |
| `ELASTICSEARCH_PORT` | Elasticsearch port | `9200` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |

### Application
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `PORT` | Backend server port | `8000` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

### Frontend (Next.js)
| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

## 🔒 Security Best Practices

### 1. Never Commit Secrets
```bash
# These files are gitignored:
.env
backend/.env
frontend/.env.local
```

### 2. Use Different Keys for Different Environments
```bash
# Development
GOOGLE_API_KEY=dev_key_here

# Production  
GOOGLE_API_KEY=prod_key_here
```

### 3. Validate Environment on Startup
The application automatically validates required environment variables on startup.

## 🌍 Environment-Specific Configuration

### Development
```bash
NODE_ENV=development
LOG_LEVEL=INFO
DEBUG=true
```

### Production
```bash
NODE_ENV=production
LOG_LEVEL=WARNING
DEBUG=false
ELASTICSEARCH_SCHEME=https
```

## 🛠️ Troubleshooting

### Missing Environment Files
```bash
# Regenerate all files
./scripts/setup-env.sh generate
./scripts/setup-env.sh create
```

### Configuration Issues
```bash
# Check for problems
./scripts/setup-env.sh validate

# Common issues:
# 1. Missing GOOGLE_API_KEY
# 2. Wrong API URLs
# 3. Missing .env files
```

### Backend Can't Find Variables
```bash
# Make sure backend/.env exists
ls -la backend/.env

# Check if variables are set
grep GOOGLE_API_KEY backend/.env
```

### Frontend Can't Find Variables
```bash
# Make sure frontend/.env.local exists
ls -la frontend/.env.local

# Check NEXT_PUBLIC_ prefix
grep NEXT_PUBLIC frontend/.env.local
```

## 📚 Advanced Usage

### Custom Environment Templates
You can modify `.env.template` to add new variables:

```bash
# 1. Edit the master template
nano .env.template

# 2. Regenerate all files
./scripts/setup-env.sh generate

# 3. Update your actual .env files
nano .env
```

### Environment Inheritance
Variables flow from root to specific environments:
```
.env.template → .env.example → .env
              ↓
              backend/.env.example → backend/.env
              ↓  
              frontend/.env.example → frontend/.env.local
```

### Docker Compose Integration
The root `.env` file is automatically loaded by Docker Compose:

```yaml
# docker-compose.yml
services:
  backend:
    env_file:
      - .env
      - backend/.env
```

## 🎯 Benefits of This Approach

1. **Single Source of Truth**: All environment variables defined in one place
2. **No Duplication**: Eliminates inconsistencies between files
3. **Easy Maintenance**: Update template once, regenerate all files
4. **Environment Separation**: Clear separation between dev/prod configs
5. **Validation**: Built-in validation and error checking
6. **Documentation**: Self-documenting with comments and examples