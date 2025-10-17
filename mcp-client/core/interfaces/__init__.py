"""
Core interfaces package.

This package contains interface definitions that establish the contracts
between different components of the application.

These interfaces enable:
- Dependency inversion (the "D" in SOLID)
- Loose coupling between components
- Easier testing through mocking
- Pluggable implementations
"""

from core.interfaces.llm_provider import ILLMProvider
from core.interfaces.mcp_client import IMCPClient
from core.interfaces.conversation_repository import IConversationRepository
from core.interfaces.application_service import IApplicationService
from core.interfaces.history_manager import IHistoryManager

__all__ = [
    'ILLMProvider',
    'IMCPClient',
    'IConversationRepository',
    'IApplicationService',
    'IHistoryManager'
]