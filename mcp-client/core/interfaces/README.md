# Core Interfaces

This directory contains interfaces that define the contracts between different components of the application.

## Purpose

Interfaces provide abstraction boundaries that:

1. **Decouple Components**: Allow components to interact without knowing the concrete implementations
2. **Enable Dependency Inversion**: High-level modules depend on abstractions, not details
3. **Facilitate Testing**: Make it easier to substitute mock implementations for testing
4. **Support Multiple Implementations**: Allow for different implementations to be swapped in as needed

## Interfaces Overview

| Interface | Purpose |
|-----------|---------|
| `ILLMProvider` | Abstracts interaction with different LLM providers (Claude, OpenAI, etc.) |
| `IMCPClient` | Defines how the application interacts with MCP (Model Context Protocol) servers |
| `IConversationRepository` | Specifies how conversations are stored and retrieved |
| `IApplicationService` | High-level application operations that orchestrate domain services |
| `IHistoryManager` | Manages conversation history storage and retrieval |

## Design Principles

These interfaces follow these principles:

1. **Interface Segregation**: Each interface has a focused, cohesive purpose
2. **Dependency Inversion**: High-level components depend on these abstractions
3. **Command-Query Separation**: Methods either perform actions or return data, not both
4. **Minimal Coupling**: Interfaces depend only on domain models, not other components

## Implementation Notes

When implementing these interfaces:

- Implementations should be placed in the appropriate infrastructure layer
- Each implementation should follow the Single Responsibility Principle
- Unit tests should verify conformance to the interface contract
- Consider using the Strategy Pattern for swappable implementations