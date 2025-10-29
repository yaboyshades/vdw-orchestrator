"""Advanced Reasoning Components for VDW Orchestrator

This package contains advanced reasoning capabilities:
- Conversation Distillation: Transform unstructured input into structured requirements
- Mangle Client: gRPC client for Mangle deductive reasoning engine
- Self-Reflection: Recursive learning and optimization
"""

from .conversation_distiller import ConversationDistiller

__version__ = "0.1.0"
__all__ = [
    "ConversationDistiller",
    # "MangleClient",  # Will be implemented later
    # "SelfReflection",  # Will be implemented later
]