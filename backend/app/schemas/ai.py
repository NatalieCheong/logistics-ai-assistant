# backend/app/schemas/ai.py
"""
Pydantic schemas for AI endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request schema for AI chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = None
    stream: bool = Field(False, description="Enable streaming response")


class ChatResponse(BaseModel):
    """Response schema for AI chat endpoint"""
    message: str
    conversation_id: str
    tokens_used: Optional[int] = None
    sources: Optional[List[Dict[str, Any]]] = None


class DocumentSearchRequest(BaseModel):
    """Request schema for document search (RAG)"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


class DocumentSearchResponse(BaseModel):
    """Response schema for document search"""
    query: str
    results: List[Dict[str, Any]]
    answer: Optional[str] = None


class ShipmentQueryRequest(BaseModel):
    """Request schema for natural language shipment queries"""
    query: str = Field(..., description="Natural language query about shipments")


class ShipmentQueryResponse(BaseModel):
    """Response schema for shipment queries"""
    query: str
    answer: str
    shipments: Optional[List[Dict[str, Any]]] = None
    action_taken: Optional[str] = None
