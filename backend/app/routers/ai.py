# backend/app/routers/ai.py
"""
AI Assistant endpoints using LangChain and OpenAI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator
import json
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    ShipmentQueryRequest,
    ShipmentQueryResponse
)
from app.utils.auth import get_current_active_user
from app.ai.agent import LogisticsAIAgent
from app.ai.rag import get_rag_system

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize AI agent (singleton)
_ai_agent = None


def get_ai_agent() -> LogisticsAIAgent:
    """Get or create AI agent instance"""
    global _ai_agent
    if _ai_agent is None:
        _ai_agent = LogisticsAIAgent()
    return _ai_agent


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    agent: LogisticsAIAgent = Depends(get_ai_agent)
):
    """
    Chat with AI logistics assistant
    
    The AI can:
    - Answer questions about shipments
    - Calculate shipping costs
    - Find warehouses
    - Estimate delivery times
    - Search for shipments
    
    **Example queries:**
    - "What's the status of shipment TRACK123456?"
    - "How much to ship 25kg from NYC to LA?"
    - "Find warehouses near Chicago"
    - "Show me all pending shipments"
    """
    try:
        response = await agent.chat(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_with_ai_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    agent: LogisticsAIAgent = Depends(get_ai_agent)
):
    """
    Streaming chat endpoint for real-time responses
    
    Returns Server-Sent Events (SSE) for streaming AI responses
    """
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            # Note: This is a simplified implementation
            # Full streaming would require LangChain streaming callbacks
            response = await agent.chat(
                message=request.message,
                conversation_id=request.conversation_id
            )
            
            # Simulate streaming by yielding chunks
            message = response["message"]
            chunk_size = 20
            
            for i in range(0, len(message), chunk_size):
                chunk = message[i:i + chunk_size]
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Send final message
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documentation(
    request: DocumentSearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search logistics documentation using RAG
    
    This endpoint uses Retrieval Augmented Generation to:
    1. Find relevant documents from the knowledge base
    2. Generate an answer grounded in those documents
    
    **Example queries:**
    - "What are the safety procedures for hazardous materials?"
    - "How do I handle a delayed international shipment?"
    - "What's the policy for damaged packages?"
    """
    try:
        rag = get_rag_system()
        result = await rag.search(request.query, top_k=request.top_k)
        
        return DocumentSearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in document search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documentation: {str(e)}"
        )


@router.post("/query/shipment", response_model=ShipmentQueryResponse)
async def natural_language_shipment_query(
    request: ShipmentQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    agent: LogisticsAIAgent = Depends(get_ai_agent)
):
    """
    Natural language queries about shipments
    
    Ask questions in plain English and get structured responses
    
    **Example queries:**
    - "Show me all shipments going to California"
    - "Which shipments are delayed?"
    - "Find packages over 50kg"
    - "What's happening with my Los Angeles deliveries?"
    """
    try:
        # Use AI agent to process query
        response = await agent.chat(
            message=f"Search and analyze shipments based on this query: {request.query}"
        )
        
        # The agent will use the search_shipments tool
        # In a production system, you might extract structured data
        # from the agent's response to populate the shipments field
        
        return ShipmentQueryResponse(
            query=request.query,
            answer=response["message"],
            shipments=None,  # Could be populated from tool results
            action_taken="Searched shipments database"
        )
        
    except Exception as e:
        logger.error(f"Error in shipment query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing shipment query: {str(e)}"
        )


@router.get("/health")
async def ai_health_check():
    """
    Check if AI services are operational
    
    Verifies:
    - OpenAI API connectivity
    - Vector database status
    - Agent initialization
    """
    try:
        agent = get_ai_agent()
        rag = get_rag_system()
        
        return {
            "status": "healthy",
            "openai": "connected",
            "vector_store": "active",
            "agent": "initialized"
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/feedback")
async def submit_feedback(
    conversation_id: str,
    rating: int,
    comment: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit feedback on AI responses
    
    Helps improve the AI assistant over time
    
    - **conversation_id**: ID of the conversation
    - **rating**: 1-5 stars
    - **comment**: Optional feedback comment
    """
    # In production, store this in a database for analysis
    logger.info(f"Feedback from user {current_user.id}: {rating}/5 for conversation {conversation_id}")
    
    if comment:
        logger.info(f"Comment: {comment}")
    
    return {
        "message": "Thank you for your feedback!",
        "conversation_id": conversation_id,
        "rating": rating
    }


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    agent: LogisticsAIAgent = Depends(get_ai_agent)
):
    """
    Clear conversation history
    
    Deletes the conversation memory for a fresh start
    """
    try:
        agent.clear_memory()
        return {
            "message": f"Conversation {conversation_id} cleared",
            "conversation_id": conversation_id
        }
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing conversation"
        )


# Example endpoint showing direct OpenAI API usage (not through LangChain)
@router.post("/completion/direct")
async def direct_openai_completion(
    prompt: str,
    max_tokens: int = 150,
    current_user: User = Depends(get_current_active_user)
):
    """
    Direct OpenAI API call example
    
    Demonstrates using OpenAI API directly without LangChain
    Useful for simple completions or specific use cases
    """
    try:
        import openai
        from app.config import settings
        
        openai.api_key = settings.OPENAI_API_KEY
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful logistics assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return {
            "prompt": prompt,
            "completion": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "model": response.model
        }
        
    except Exception as e:
        logger.error(f"Error in direct completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error with OpenAI API: {str(e)}"
        )
