# Mem0 Server API Documentation

## Base URL
```
http://localhost:8002
```

## Authentication
Currently no authentication is implemented. Add API key authentication for production use.

---

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "mem0-server",
  "version": "1.0.0",
  "connections": {
    "qdrant": {
      "url": "http://localhost:6333",
      "status": "connected"
    },
    "collection": "user_memories"
  }
}
```

---

### Add Memory
```http
POST /memory/add
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "User prefers Python over JavaScript",
  "user_id": "user123",
  "metadata": {
    "source": "chat",
    "category": "preference"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Memory added successfully",
  "data": {
    "memory_id": "mem_1234567890"
  }
}
```

---

### Search Memories
```http
POST /memory/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What programming language does the user prefer?",
  "user_id": "user123",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "memory": "User prefers Python over JavaScript",
      "score": 0.95,
      "metadata": {
        "source": "chat",
        "category": "preference"
      }
    }
  ],
  "count": 1
}
```

---

### Get User Memories
```http
GET /memory/{user_id}?limit=100
```

**Response:**
```json
{
  "success": true,
  "memories": [
    {
      "id": "mem_123",
      "memory": "User likes Python",
      "metadata": {}
    }
  ],
  "count": 1
}
```

---

### Delete Memory
```http
DELETE /memory/{memory_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Memory deleted successfully"
}
```

---

### Delete User Memories
```http
DELETE /memory/user/{user_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted 5 memories",
  "data": {
    "deleted_count": 5
  }
}
```

---

## Error Responses

All endpoints may return error responses:

```json
{
  "success": false,
  "error": "Error type",
  "detail": "Detailed error message"
}
```

**Status Codes:**
- `400` - Bad Request
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable
