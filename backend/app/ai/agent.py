# backend/app/ai/agent.py
"""
LangChain AI Agent for Logistics Assistant
This demonstrates OpenAI API + LangChain integration with custom tools
"""

from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from typing import Dict, Any, Optional
import logging

from app.config import settings
from app.ai.tools import (
    get_shipment_status,
    calculate_shipping_cost,
    find_nearest_warehouse,
    estimate_delivery_time,
    search_shipments
)

logger = logging.getLogger(__name__)


class LogisticsAIAgent:
    """
    Main AI Agent for logistics operations
    
    Features:
    - Natural language understanding of logistics queries
    - Tool usage for real-time data access
    - Conversation memory for context
    - Error handling and fallbacks
    """
    
    def __init__(self):
        """Initialize the AI agent with LLM and tools"""
        
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # Lower for more consistent responses
            api_key=settings.OPENAI_API_KEY,
            streaming=True
        )
        
        # Define available tools
        self.tools = [
            get_shipment_status,
            calculate_shipping_cost,
            find_nearest_warehouse,
            estimate_delivery_time,
            search_shipments
        ]
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Create executor
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            max_execution_time=30,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def _get_system_prompt(self) -> str:
        """
        System prompt defining the agent's behavior
        """
        return """You are an expert AI assistant for a logistics company. Your role is to help users with:

1. **Shipment Tracking**: Check status and location of shipments
2. **Cost Calculation**: Estimate shipping costs based on origin, destination, and weight
3. **Warehouse Information**: Find nearest warehouses and check availability
4. **Delivery Estimates**: Provide estimated delivery times
5. **Search**: Find shipments based on various criteria

**Guidelines:**
- Always be professional, clear, and concise
- Use the available tools to get real-time data
- If you don't have information, say so clearly
- Provide actionable next steps when possible
- Format responses in a user-friendly way
- For tracking numbers, always use the exact format provided
- When discussing costs, include currency (USD)
- For locations, be specific about cities and states

**Available Tools:**
- get_shipment_status: Get current status of a shipment by tracking number
- calculate_shipping_cost: Calculate shipping cost based on route and weight
- find_nearest_warehouse: Find closest warehouse to a location
- estimate_delivery_time: Estimate delivery time for a shipment
- search_shipments: Search for shipments by various criteria

**Response Format:**
- Start with a brief, direct answer
- Provide relevant details from tool calls
- End with helpful next steps or suggestions if appropriate
- Use bullet points for multiple pieces of information

Remember: You're helping people manage their logistics efficiently. Be helpful, accurate, and quick!
"""
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a chat message and return response
        
        Args:
            message: User's input message
            conversation_id: Optional conversation ID for maintaining context
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            logger.info(f"Processing message: {message}")
            
            # Execute agent
            result = await self.executor.ainvoke({
                "input": message
            })
            
            # Extract response
            response = {
                "message": result["output"],
                "conversation_id": conversation_id or "new",
                "tokens_used": None,  # Would need token counting
                "sources": self._extract_sources(result.get("intermediate_steps", []))
            }
            
            logger.info(f"Generated response: {response['message'][:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            return {
                "message": "I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                "conversation_id": conversation_id or "new",
                "error": str(e)
            }
    
    def _extract_sources(self, intermediate_steps: list) -> list:
        """
        Extract source information from intermediate steps
        """
        sources = []
        for step in intermediate_steps:
            if len(step) >= 2:
                action, observation = step[0], step[1]
                sources.append({
                    "tool": action.tool,
                    "input": action.tool_input,
                    "output": str(observation)[:200]  # Truncate for brevity
                })
        return sources
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
