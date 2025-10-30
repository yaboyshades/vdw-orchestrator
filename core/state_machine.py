"""State machine for VDW phase transitions"""
import logging
from typing import Optional
from core.models import VDWPhase, ProjectContext

logger = logging.getLogger(__name__)

class VDWStateMachine:
    """Manages state transitions between VDW phases"""
    
    # Valid transitions map
    VALID_TRANSITIONS = {
        VDWPhase.IDLE: [VDWPhase.PHASE_1_MOOD],
        VDWPhase.PHASE_1_MOOD: [VDWPhase.PHASE_1_VALIDATION],
        VDWPhase.PHASE_1_VALIDATION: [VDWPhase.PHASE_2_ARCHITECTURE, VDWPhase.PHASE_1_MOOD],
        VDWPhase.PHASE_2_ARCHITECTURE: [VDWPhase.PHASE_2_VALIDATION],
        VDWPhase.PHASE_2_VALIDATION: [VDWPhase.PHASE_3_SPECIFICATION, VDWPhase.PHASE_2_ARCHITECTURE],
        VDWPhase.PHASE_3_SPECIFICATION: [VDWPhase.PHASE_3_VALIDATION],
        VDWPhase.PHASE_3_VALIDATION: [VDWPhase.PHASE_4_IMPLEMENTATION, VDWPhase.PHASE_3_SPECIFICATION],
        VDWPhase.PHASE_4_IMPLEMENTATION: [VDWPhase.PHASE_4_VALIDATION],
        VDWPhase.PHASE_4_VALIDATION: [VDWPhase.PHASE_5_VALIDATION_TESTING, VDWPhase.PHASE_4_IMPLEMENTATION],
        VDWPhase.PHASE_5_VALIDATION_TESTING: [VDWPhase.PHASE_5_VALIDATION],
        VDWPhase.PHASE_5_VALIDATION: [VDWPhase.COMPLETED, VDWPhase.PHASE_5_VALIDATION_TESTING],
        VDWPhase.COMPLETED: [],
        VDWPhase.FAILED: []
    }
    
    def __init__(self, context: ProjectContext, mangle_client=None):
        self.context = context
        self.mangle_client = mangle_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def transition_to(self, target_phase: VDWPhase, reason: str = "") -> bool:
        """
        Attempt to transition to the target phase.
        
        Args:
            target_phase: The phase to transition to
            reason: Reason for the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        current = self.context.current_phase
        
        # Check if transition is valid
        if target_phase not in self.VALID_TRANSITIONS.get(current, []):
            self.logger.warning(
                f"Invalid transition from {current} to {target_phase}. Reason: {reason}"
            )
            return False
        
        # Optionally use Mangle for validation
        if self.mangle_client:
            validation = await self._validate_with_mangle(current, target_phase)
            if not validation:
                self.logger.warning(
                    f"Mangle validation failed for transition {current} -> {target_phase}"
                )
                return False
        
        # Perform the transition
        self.logger.info(
            f"Transitioning from {current} to {target_phase}. Reason: {reason}"
        )
        self.context.current_phase = target_phase
        
        return True
    
    async def _validate_with_mangle(self, from_phase: VDWPhase, to_phase: VDWPhase) -> bool:
        """
        Use Mangle reasoning to validate the transition.
        
        This would check:
        - Are all dependencies satisfied?
        - Are required artifacts present?
        - Is the transition logically sound?
        """
        try:
            # Simplified - in production would make actual gRPC call
            # query = ReasoningQuery(
            #     query_type="transition_validation",
            #     context={
            #         "from_phase": from_phase,
            #         "to_phase": to_phase,
            #         "project_context": self.context.model_dump()
            #     }
            # )
            # result = await self.mangle_client.query(query)
            # return result.get("valid", True)
            return True
        except Exception as e:
            self.logger.error(f"Mangle validation error: {e}")
            return True  # Fail open for now
    
    def can_transition_to(self, target_phase: VDWPhase) -> bool:
        """Check if transition to target phase is allowed"""
        return target_phase in self.VALID_TRANSITIONS.get(self.context.current_phase, [])
    
    def get_next_phases(self) -> list[VDWPhase]:
        """Get list of valid next phases from current state"""
        return self.VALID_TRANSITIONS.get(self.context.current_phase, [])
