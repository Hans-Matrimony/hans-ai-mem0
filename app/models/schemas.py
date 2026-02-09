"""
Pydantic schemas for request/response validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Memory Schemas
# ============================================================================

class MemoryBase(BaseModel):
    """Base memory schema"""
    content: str = Field(..., min_length=1, max_length=10000)


class MemoryCreate(MemoryBase):
    """Schema for creating a memory"""
    user_id: str = Field(..., min_length=1, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class MemoryUpdate(BaseModel):
    """Schema for updating a memory"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(MemoryBase):
    """Schema for memory response"""
    id: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    score: Optional[float] = None


class MemoryListItem(BaseModel):
    """Schema for memory list item"""
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Search Schemas
# ============================================================================

class MemorySearch(BaseModel):
    """Schema for memory search"""
    query: str = Field(..., min_length=1, max_length=500)
    user_id: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None


class SearchResultItem(BaseModel):
    """Schema for search result item"""
    memory: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    memory_id: Optional[str] = None


# ============================================================================
# Batch Schemas
# ============================================================================

class BatchMemoryCreate(BaseModel):
    """Schema for batch memory creation"""
    memories: List[MemoryCreate] = Field(..., min_length=1, max_length=50)


class BatchMemoryResponse(BaseModel):
    """Schema for batch operation response"""
    success_count: int
    error_count: int
    memory_ids: List[str]
    errors: List[Dict[str, Any]]


# ============================================================================
# Response Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    version: str
    connections: Dict[str, Any]


class SuccessResponse(BaseModel):
    """Schema for success response"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Schema for error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
