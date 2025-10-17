"""
Process Query Use Case - Orchestrates query processing with LLM.
"""
from dataclasses import dataclass
from typing import Optional
import logging

from core.services.llm_service import LLMService
from core.services.conversation_service import ConversationService
from core.models.llm_response import LLMResponse


@dataclass
class ProcessQueryRequest:
    """Request for process query use case."""
    query: str
    conversation_id: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 1.0


class ProcessQueryUseCase:
    """
    Use case: Process user query with LLM.
    
    This use case orchestrates the complete flow of:
    1. Get or create conversation
    2. Process query with LLM service
    3. Handle tool calls (delegated to LLM service)
    4. Save conversation
    5. Return response
    
    Responsibilities:
    - Coordinate between services
    - Manage conversation lifecycle
    - Handle errors gracefully
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        conversation_service: ConversationService
    ):
        """
        Initialize use case.
        
        Args:
            llm_service: LLM service for processing queries
            conversation_service: Conversation service for managing history
        """
        self.llm_service = llm_service
        self.conversation_service = conversation_service
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> LLMResponse:
        """
        Execute use case: process query.
        
        Args:
            query: User query text
            conversation_id: Optional conversation ID to continue
            max_tokens: Maximum tokens for LLM response
            temperature: Sampling temperature
            
        Returns:
            LLMResponse with text and metadata
            
        Raises:
            Exception: If query processing fails
        """
        self.logger.info(f"Processing query: {query[:50]}...")
        
        try:
            # Get conversation
            if conversation_id:
                conversation = self.conversation_service.load(conversation_id)
            else:
                conversation = self.conversation_service.get_current()
            
            # Process with LLM service (handles tool calls internally)
            response = await self.llm_service.process_query(
                query=query,
                conversation=conversation,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Save updated conversation
            self.conversation_service.save(conversation)
            
            self.logger.info("Query processed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise
    
    async def execute_batch(
        self,
        queries: list[str],
        **kwargs
    ) -> list[LLMResponse]:
        """
        Execute multiple queries in sequence.
        
        Args:
            queries: List of query strings
            **kwargs: Additional arguments for execute()
            
        Returns:
            List of LLMResponse objects
        """
        responses = []
        
        for query in queries:
            response = await self.execute(query, **kwargs)
            responses.append(response)
        
        return responses
