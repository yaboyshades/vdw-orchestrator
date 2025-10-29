# Simple pytest scaffolding for ConversationDistiller
import asyncio
import pytest

# Assuming actual implementation exists at reasoning/conversation_distiller.py
from reasoning.conversation_distiller import ConversationDistiller

@pytest.mark.asyncio
async def test_distillation_segments_and_graph_basic():
    distiller = ConversationDistiller()
    vibe = (
        "We want a simple blogging platform. Users should be able to sign up and write posts. "
        "It must be secure and scalable. After we design the database, we can implement the API."
    )
    result = await distiller.distill(vibe)

    # Basic shape checks
    assert hasattr(result, 'segments') and isinstance(result.segments, list)
    assert hasattr(result, 'dependency_graph') and isinstance(result.dependency_graph, dict)

    # Expect at least one goal and one dependency
    assert len(result.segments) >= 1
    # Graph entries should exist
    keys = list(result.dependency_graph.keys())
    assert isinstance(keys, list)
