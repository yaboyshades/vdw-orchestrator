"""Integration test for the complete VDW workflow (Phases 1-5)."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from core.orchestrator import VDWOrchestrator
from core.event_bus import EventBus
from core.memory_store import MemoryStore
from core.models import VDWPhase
from reasoning.mangle_client import MangleClient


class TestFullVDWWorkflow:
    """Test complete VDW workflow from vibe to validation."""

    @pytest.fixture
    async def orchestrator(self):
        """Set up orchestrator with mocked dependencies."""
        # Mock dependencies
        event_bus = MagicMock(spec=EventBus)
        memory_store = AsyncMock(spec=MemoryStore)
        mangle_client = AsyncMock(spec=MangleClient)
        
        # Mock Mangle validation to always allow transitions
        validation_result = MagicMock()
        validation_result.allowed = True
        validation_result.reason = "Test validation passed"
        validation_result.confidence = 0.95
        
        mangle_client.validate_phase_transition.return_value = validation_result
        mangle_client.connect.return_value = None
        
        # Create orchestrator
        orchestrator = VDWOrchestrator(event_bus, memory_store, mangle_client)
        
        return orchestrator

    @pytest.mark.asyncio
    async def test_complete_workflow_happy_path(self, orchestrator):
        """Test complete workflow from Phase 1 through Phase 5."""
        # Start with a vibe
        test_vibe = "Build a minimalist task management app that feels like a breath of fresh air"
        
        # Phase 1: Submit project
        project_id = await orchestrator.submit_new_project(test_vibe)
        assert project_id is not None
        
        # Verify Phase 1 execution
        ctx = orchestrator.get_project_context(project_id)
        assert ctx is not None
        assert ctx.current_phase == VDWPhase.PHASE_1_VALIDATION
        assert ctx.phase_1_output is not None
        
        # Phase 1 → Phase 2: Approve Phase 1
        await orchestrator.approve_phase_1(project_id, "Great mood analysis!")
        
        # Verify Phase 2 execution
        ctx = orchestrator.get_project_context(project_id)
        assert ctx.current_phase == VDWPhase.PHASE_2_VALIDATION
        assert ctx.phase_2_output is not None
        
        # Phase 2 → Phase 3: Approve Phase 2
        await orchestrator.approve_phase_2(project_id, "Architecture looks solid!")
        
        # Verify Phase 3 execution
        ctx = orchestrator.get_project_context(project_id)
        assert ctx.current_phase == VDWPhase.PHASE_3_VALIDATION
        assert ctx.phase_3_output is not None
        
        # Phase 3 → Phase 4: Approve Phase 3
        await orchestrator.approve_phase_3(project_id, "Specifications are detailed!")
        
        # Verify Phase 4 execution
        ctx = orchestrator.get_project_context(project_id)
        assert ctx.current_phase == VDWPhase.PHASE_4_VALIDATION
        assert ctx.phase_4_output is not None
        
        # Phase 4 → Phase 5: Approve Phase 4
        await orchestrator.approve_phase_4(project_id, "Implementation plan is comprehensive!")
        
        # Verify Phase 5 execution
        ctx = orchestrator.get_project_context(project_id)
        assert ctx.current_phase == VDWPhase.PHASE_5_VALIDATION
        assert ctx.phase_5_output is not None
        
        # Phase 5 → Completion: Approve Phase 5
        await orchestrator.approve_phase_5(project_id, "All tests pass, ready for production!")
        
        # Verify project completion
        ctx = orchestrator.get_project_context(project_id)
        assert ctx.current_phase == VDWPhase.COMPLETED
        
        # Verify all artifacts are present
        artifacts = orchestrator.get_project_artifacts(project_id)
        assert artifacts['project_id'] == project_id
        assert artifacts['initial_vibe'] == test_vibe
        assert artifacts['phase_1_output'] is not None
        assert artifacts['phase_2_output'] is not None
        assert artifacts['phase_3_output'] is not None
        assert artifacts['phase_4_output'] is not None
        assert artifacts['phase_5_output'] is not None
        assert len(artifacts['user_feedback']) == 5  # Feedback for all phases

    @pytest.mark.asyncio
    async def test_vibe_preservation_throughout_workflow(self, orchestrator):
        """Test that vibe is preserved throughout the entire workflow."""
        test_vibe = "Create a zen-like coding environment that promotes flow state"
        
        # Execute complete workflow
        project_id = await orchestrator.submit_new_project(test_vibe)
        
        # Approve all phases
        await orchestrator.approve_phase_1(project_id)
        await orchestrator.approve_phase_2(project_id) 
        await orchestrator.approve_phase_3(project_id)
        await orchestrator.approve_phase_4(project_id)
        await orchestrator.approve_phase_5(project_id)
        
        # Verify vibe alignment in each phase
        artifacts = orchestrator.get_project_artifacts(project_id)
        
        # Check Phase 1 captured the vibe
        phase_1 = artifacts['phase_1_output']
        assert 'vibe_analysis' in phase_1
        
        # Check Phase 2 preserved vibe alignment
        phase_2 = artifacts['phase_2_output']
        assert 'vibe_alignment' in phase_2
        assert phase_2['vibe_alignment']['vibe_score'] > 0.8
        
        # Check Phase 3 maintained vibe
        phase_3 = artifacts['phase_3_output']
        assert 'vibe_alignment' in phase_3
        assert phase_3['vibe_alignment']['vibe_score'] > 0.8
        
        # Check Phase 4 preserved aesthetic
        phase_4 = artifacts['phase_4_output']
        assert 'vibe_maintained' in phase_4
        
        # Check Phase 5 final vibe validation
        phase_5 = artifacts['phase_5_output']
        assert 'final_vibe_check' in phase_5
        final_check = phase_5['final_vibe_check']
        assert final_check['original_vibe_preserved'] is True
        assert final_check['final_vibe_score'] > 8.0

    @pytest.mark.asyncio
    async def test_rejection_and_retry_workflow(self, orchestrator):
        """Test rejection and retry functionality."""
        project_id = await orchestrator.submit_new_project("Test vibe")
        
        # Reject Phase 1 initially
        ctx = orchestrator.get_project_context(project_id)
        initial_output = ctx.phase_1_output.copy()
        
        # Reject and provide feedback
        await orchestrator.approve_phase(project_id, VDWPhase.PHASE_1_VALIDATION, 
                                       "Need more detail on user personas", approved=False)
        
        # Should be back in Phase 1 execution with feedback
        ctx = orchestrator.get_project_context(project_id)
        assert ctx.current_phase == VDWPhase.PHASE_1_VALIDATION  # Re-executed and back to validation
        assert VDWPhase.PHASE_1_MOOD in ctx.user_feedback
        assert "user personas" in ctx.user_feedback[VDWPhase.PHASE_1_MOOD]
        
        # New output should be different (re-executed with feedback)
        new_output = ctx.phase_1_output
        # In a real implementation, the agent would incorporate feedback
        # For this test, we just verify the workflow handled the rejection
        assert new_output is not None

    @pytest.mark.asyncio
    async def test_advance_project_api(self, orchestrator):
        """Test the advance_project API endpoint functionality."""
        project_id = await orchestrator.submit_new_project("Test API advancement")
        
        # Try to advance - should indicate awaiting validation
        result = await orchestrator.advance_project(project_id)
        assert result['awaiting_validation'] is True
        assert result['current_phase'] == VDWPhase.PHASE_1_VALIDATION.value
        
        # Approve and advance to next phase
        await orchestrator.approve_phase_1(project_id)
        
        # Now should be in Phase 2 validation
        result = await orchestrator.advance_project(project_id)
        assert result['current_phase'] == VDWPhase.PHASE_2_VALIDATION.value

    @pytest.mark.asyncio
    async def test_artifacts_persistence(self, orchestrator):
        """Test that artifacts are properly stored and retrievable."""
        project_id = await orchestrator.submit_new_project("Test persistence")
        
        # Verify memory store was called for each phase
        memory_store = orchestrator.memory_store
        
        # Should have stored project context and Phase 1 output
        assert memory_store.store_atom.call_count >= 2
        
        # Verify artifact structure
        artifacts = orchestrator.get_project_artifacts(project_id)
        expected_keys = [
            'project_id', 'current_phase', 'initial_vibe',
            'phase_1_output', 'phase_2_output', 'phase_3_output',
            'phase_4_output', 'phase_5_output', 'user_feedback'
        ]
        
        for key in expected_keys:
            assert key in artifacts

    @pytest.mark.asyncio  
    async def test_mangle_integration(self, orchestrator):
        """Test integration with Mangle reasoning engine."""
        project_id = await orchestrator.submit_new_project("Test Mangle integration")
        
        # Verify Mangle client was called for phase validation
        mangle_client = orchestrator.mangle
        assert mangle_client.connect.called
        assert mangle_client.validate_phase_transition.called
        
        # Verify validation was called with correct parameters
        call_args = mangle_client.validate_phase_transition.call_args_list[0]
        assert call_args[0][0] == VDWPhase.IDLE  # from_phase
        assert call_args[0][1] == VDWPhase.PHASE_1_MOOD  # to_phase
        
        # Complete one more phase to verify continued integration
        await orchestrator.approve_phase_1(project_id)
        
        # Should have additional validation calls
        assert mangle_client.validate_phase_transition.call_count >= 2
