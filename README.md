# hans-ai-mem0

Memory management server for Hans AI Dashboard using Mem0 with Qdrant backend.

## Features

- Persistent memory storage with Qdrant vector database
- Semantic search capabilities
- User-isolated memory storage
- RESTful API
- Health monitoring
- Docker-ready deployment

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/hans-ai-mem0.git
cd hans-ai-mem0

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# - QDRANT_URL
# - QDRANT_API_KEY
# - OPENAI_API_KEY

# Run with Docker
docker-compose up -d

# Or run directly
pip install -r requirements.txt
uvicorn mem0_server:app --host 0.0.0.0 --port 8002
```

## API Endpoints

### Health Check
```
GET /health
```

### Add Memory
```
POST /memory/add
Content-Type: application/json

{
  "content": "User prefers Python over JavaScript",
  "user_id": "user123",
  "metadata": {
    "source": "chat",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Search Memories
```
POST /memory/search
Content-Type: application/json

{
  "query": "What programming language does the user prefer?",
  "user_id": "user123",
  "limit": 5
}
```

### Get All Memories
```
GET /memory/{user_id}?limit=100
```

### Delete Memory
```
DELETE /memory/{memory_id}
```

### Delete User Memories
```
DELETE /memory/user/{user_id}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QDRANT_URL` | Yes | - | Qdrant instance URL |
| `QDRANT_API_KEY` | No | - | Qdrant API key |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for embeddings |
| `MEM0_COLLECTION` | No | user_memories | Qdrant collection name |
| `MEM0_HOST` | No | 0.0.0.0 | Server host |
| `MEM0_PORT` | No | 8002 | Server port |

## Deployment

### Coolify

1. Create new service from Git repository
2. Configure environment variables
3. Deploy

### Docker

```bash
docker build -t hans-ai-mem0 .
docker run -p 8002:8002 --env-file .env hans-ai-mem0
```

## License

MIT License
