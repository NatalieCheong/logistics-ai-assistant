import pytest
from fastapi import status
from unittest.mock import Mock, patch


def test_ai_health_check(client):
    """Test AI health check endpoint"""
    response = client.get("/api/ai/health")
    
    assert response.status_code == status.HTTP_200_OK
    # May fail if OpenAI key not configured, that's ok for tests


@patch('app.ai.agent.LogisticsAIAgent.chat')
async def test_chat_endpoint(mock_chat, client, auth_headers):
    """Test AI chat endpoint"""
    # Mock the AI response
    mock_chat.return_value = {
        "message": "Test response",
        "conversation_id": "test123",
        "tokens_used": 50
    }
    
    response = client.post(
        "/api/ai/chat",
        headers=auth_headers,
        json={
            "message": "What is the status of TRACK123?"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data


def test_chat_without_auth(client):
    """Test chat endpoint requires authentication"""
    response = client.post(
        "/api/ai/chat",
        json={"message": "Hello"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
