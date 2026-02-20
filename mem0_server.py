#!/usr/bin/env python3
"""
Mem0 Server - Memory Management for Hans AI Dashboard

This server provides a RESTful API for managing user memories
using Mem0 with Qdrant as the vector backend.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MEM0_COLLECTION = os.getenv("MEM0_COLLECTION", "user_memories")

# Global memory instance
memory_instance = None


# =============================================================================
# Pydantic Models
# =============================================================================

class MemoryInput(BaseModel):
    """Request model for adding a memory"""
    content: str = Field(..., min_length=1, description="Memory content")
    user_id: str = Field(..., min_length=1, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional metadata for the memory"
    )


class SearchInput(BaseModel):
    """Request model for searching memories"""
    query: str = Field(..., min_length=1, description="Search query")
    user_id: str = Field(..., min_length=1, description="User identifier")
    limit: int = Field(default=5, ge=1, le=100, description="Number of results")


class MemoryUpdate(BaseModel):
    """Request model for updating a memory"""
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class MemoryListResponse(BaseModel):
    """Response for memory list"""
    success: bool
    memories: List[Dict[str, Any]]
    count: int


class SearchResult(BaseModel):
    """Single search result"""
    memory: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response for memory search"""
    success: bool
    results: List[SearchResult]
    count: int


# =============================================================================
# Mem0 Initialization
# =============================================================================

async def initialize_memory() -> None:
    """Initialize Mem0 with Qdrant backend.

    If Qdrant is not available at startup, the service will start anyway
    and memory operations will return appropriate errors. This allows
    the container to pass health checks even when Qdrant is temporarily unavailable.
    """
    global memory_instance

    try:
        from qdrant_client import QdrantClient
        from mem0 import Memory

        logger.info(f"Attempting to connect to Qdrant at {QDRANT_URL}")

        # Create Qdrant client with timeout
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY if QDRANT_API_KEY else None,
            timeout=5.0
        )

        # Configure Mem0
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "client": qdrant_client,
                    "collection_name": MEM0_COLLECTION
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": OPENAI_API_KEY
                }
            }
        }

        memory_instance = Memory.from_config(config)

        logger.info("✅ Mem0 initialized successfully")

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        raise
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize Mem0: {e}")
        logger.warning("⚠️ Memory service will be unavailable until Qdrant becomes available")
        logger.warning(f"⚠️ Please ensure QDRANT_URL is set correctly (current: {QDRANT_URL})")
        # Don't raise - allow the service to start anyway


async def close_memory() -> None:
    """Cleanup Mem0 connection"""
    global memory_instance
    if memory_instance:
        logger.info("Closing Mem0 connection...")
        memory_instance = None
        logger.info("Mem0 connection closed")


# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("🚀 Starting Mem0 Server...")
    await initialize_memory()
    logger.info("✅ Mem0 Server ready! (Patched Version User-Arg-Fix)")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Mem0 Server...")
    await close_memory()
    logger.info("👋 Mem0 Server stopped")


# =============================================================================
# FastAPI Application
# =============================================================================

# Get CORS origins
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

# Create FastAPI app
app = FastAPI(
    title="Mem0 Server",
    description="Memory management for Hans AI Dashboard",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") == "true" else None
        }
    )


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint

    Returns the current status of the server and its connections.
    The service returns 200 even if Qdrant is disconnected, allowing
    the container to pass health checks with degraded functionality.
    """
    return {
        "status": "healthy" if memory_instance else "degraded",
        "service": "mem0-server",
        "version": "1.0.0",
        "connections": {
            "qdrant": {
                "url": QDRANT_URL,
                "status": "connected" if memory_instance else "disconnected"
            },
            "collection": MEM0_COLLECTION
        }
    }


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "name": "Mem0 Server",
        "version": "1.0.0",
        "description": "Memory management for Hans AI Dashboard",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "add_memory": "/memory/add",
            "search_memory": "/memory/search",
            "get_memories": "/memory/{user_id}",
            "delete_memory": "/memory/{memory_id}",
            "delete_user_memories": "/memory/user/{user_id}"
        }
    }


# =============================================================================
# Memory Endpoints
# =============================================================================

@app.post("/memory/add", response_model=SuccessResponse, tags=["Memory"])
async def add_memory(memory: MemoryInput) -> SuccessResponse:
    """
    Add a new memory for a user

    - **content**: The memory text to store
    - **user_id**: Unique user identifier
    - **metadata**: Optional additional information
    """
    if not memory_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service not initialized"
        )

    try:
        result = memory_instance.add(
            memory.content,
            user_id=memory.user_id,
            metadata=memory.metadata or {}
        )

        logger.info(f"Memory added for user {memory.user_id}: {result}")

        return SuccessResponse(
            success=True,
            message="Memory added successfully",
            data={"memory_id": result}
        )

    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add memory: {str(e)}"
        )


@app.post("/memory/search", response_model=SearchResponse, tags=["Memory"])
async def search_memory(search: SearchInput) -> SearchResponse:
    """
    Search memories for a user using semantic search

    - **query**: Search query text
    - **user_id**: User to search memories for
    - **limit**: Maximum number of results (default: 5)
    """
    if not memory_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service not initialized"
        )

    try:
        results = memory_instance.search(
            query=search.query,
            user_id=search.user_id,
            limit=search.limit
        )

        logger.info(f"Search for user {search.user_id}: {len(results) if results else 0} results")

        # Format results
        formatted_results = []
        if results:
            for r in results:
                memory_text = ""
                score = 1.0
                metadata = {}

                if isinstance(r, dict):
                    memory_text = r.get("memory", "")
                    score = r.get("score", 0.0)
                    metadata = r.get("metadata")
                elif hasattr(r, "memory"): # It's an object
                    memory_text = getattr(r, "memory", "")
                    score = getattr(r, "score", 0.0)
                    metadata = getattr(r, "metadata", None)
                elif isinstance(r, str): # It's just a string
                    memory_text = r
                
                formatted_results.append(SearchResult(
                    memory=memory_text,
                    score=score,
                    metadata=metadata
                ))

        return SearchResponse(
            success=True,
            results=formatted_results,
            count=len(formatted_results)
        )

    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memory: {str(e)}"
        )


@app.get("/memory/{user_id}", response_model=MemoryListResponse, tags=["Memory"])
async def get_memories(
    user_id: str,
    limit: int = 100
) -> MemoryListResponse:
    """
    Get all memories for a specific user

    - **user_id**: User identifier
    - **limit**: Maximum number of memories to return (default: 100)
    """
    if not memory_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service not initialized"
        )

    try:
        raw = memory_instance.get_all(user_id=user_id, limit=limit)

        # Newer Mem0 returns {'results': [...]} instead of a plain list
        if isinstance(raw, dict) and "results" in raw:
            memories = raw["results"]
        elif isinstance(raw, list):
            memories = raw
        else:
            memories = []

        logger.info(f"Retrieved {len(memories)} memories for user {user_id}")

        return MemoryListResponse(
            success=True,
            memories=memories,
            count=len(memories)
        )

    except Exception as e:
        logger.error(f"Error getting memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories: {str(e)}"
        )


@app.delete("/memory/{memory_id}", response_model=SuccessResponse, tags=["Memory"])
async def delete_memory(memory_id: str) -> SuccessResponse:
    """
    Delete a specific memory by ID

    - **memory_id**: Unique memory identifier
    """
    if not memory_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service not initialized"
        )

    try:
        memory_instance.delete(memory_id)

        logger.info(f"Memory deleted: {memory_id}")

        return SuccessResponse(
            success=True,
            message="Memory deleted successfully"
        )

    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )


@app.delete("/memory/user/{user_id}", response_model=SuccessResponse, tags=["Memory"])
async def delete_user_memories(user_id: str) -> SuccessResponse:
    """
    Delete all memories for a specific user

    - **user_id**: User identifier
    """
    if not memory_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service not initialized"
        )

    try:
        # Get all memories first
        raw = memory_instance.get_all(user_id=user_id)

        # Newer Mem0 returns {'results': [...]} instead of a plain list
        if isinstance(raw, dict) and "results" in raw:
            memories = raw["results"]
        elif isinstance(raw, list):
            memories = raw
        else:
            memories = []

        deleted_count = 0
        if memories:
            for mem in memories:
                mem_id = mem.get("id") if isinstance(mem, dict) else getattr(mem, "id", None)
                if mem_id:
                    memory_instance.delete(mem_id)
                    deleted_count += 1

        logger.info(f"Deleted {deleted_count} memories for user {user_id}")

        return SuccessResponse(
            success=True,
            message=f"Deleted {deleted_count} memories",
            data={"deleted_count": deleted_count}
        )

    except Exception as e:
        logger.error(f"Error deleting user memories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memories: {str(e)}"
        )


# =============================================================================
# Batch Operations
# =============================================================================

class BatchMemoryInput(BaseModel):
    """Request model for batch memory operations"""
    memories: List[MemoryInput] = Field(..., min_items=1, max_items=50)


@app.post("/memory/batch/add", response_model=SuccessResponse, tags=["Memory"])
async def add_memories_batch(batch: BatchMemoryInput) -> SuccessResponse:
    """
    Add multiple memories in a single request

    - **memories**: List of memory objects (max 50)
    """
    if not memory_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service not initialized"
        )

    memory_ids = []
    errors = []

    for i, memory in enumerate(batch.memories):
        try:
            result = memory_instance.add(
                memory.content,
                user_id=memory.user_id,
                metadata=memory.metadata or {}
            )
            memory_ids.append(result)
        except Exception as e:
            errors.append({"index": i, "error": str(e)})

    logger.info(f"Batch add: {len(memory_ids)} successful, {len(errors)} errors")

    return SuccessResponse(
        success=len(errors) == 0,
        message=f"Added {len(memory_ids)} memories",
        data={
            "memory_ids": memory_ids,
            "errors": errors if errors else None
        }
    )


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("MEM0_HOST", "0.0.0.0")
    port = int(os.getenv("MEM0_PORT", "8002"))

    uvicorn.run(
        "mem0_server:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG") == "true",
        log_level=log_level.lower()
    )
