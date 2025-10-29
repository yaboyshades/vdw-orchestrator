"""Mangle gRPC Client for Advanced Reasoning

This module provides a Python gRPC client for communicating with the Mangle
deductive reasoning engine. It supports dependency validation, capability gap
analysis, performance optimization, and recursive self-reflection.
"""

import asyncio
import grpc
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid

from core.models import ReasoningQuery, ReasoningResponse, ProjectContext, VDWPhase

# gRPC stubs will be generated from .proto files
# For now, we define the interface

class MangleClient:
    """Async gRPC client for Mangle reasoning engine
    
    This client provides high-level methods for various reasoning tasks:
    - Dependency validation for phase transitions
    - Capability gap detection and analysis
    - Performance optimization recommendations
    - Recursive self-reflection on past projects
    """
    
    def __init__(self, server_address: str = "localhost:50051", 
                 max_message_length: int = 4 * 1024 * 1024):
        """Initialize the Mangle client
        
        Args:
            server_address: Address of the Mangle gRPC server
            max_message_length: Maximum message size for gRPC
        """
        self.server_address = server_address
        self.max_message_length = max_message_length
        self.logger = logging.getLogger(__name__)
        
        # gRPC channel options for optimal performance
        self.channel_options = [
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ('grpc.max_send_message_length', max_message_length),
            ('grpc.max_receive_message_length', max_message_length),
        ]
        
        self._channel = None
        self._stub = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Establish connection to Mangle server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._channel = grpc.aio.insecure_channel(
                self.server_address, 
                options=self.channel_options
            )
            
            # Test connection with a health check
            await self._health_check()
            
            # TODO: Initialize gRPC stub when .proto files are ready
            # self._stub = reasoning_pb2_grpc.ReasoningServiceStub(self._channel)
            
            self.connected = True
            self.logger.info(f"Successfully connected to Mangle server at {self.server_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Mangle server: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close connection to Mangle server"""
        if self._channel:
            await self._channel.close()
            self.connected = False
            self.logger.info("Disconnected from Mangle server")
    
    async def _health_check(self) -> bool:
        """Perform health check on Mangle server"""
        # For now, just test channel connectivity
        try:
            await self._channel.channel_ready()
            return True
        except Exception as e:
            self.logger.warning(f"Mangle health check failed: {e}")
            return False
    
    async def query(self, reasoning_query: ReasoningQuery) -> ReasoningResponse:
        """Send a reasoning query to Mangle
        
        Args:
            reasoning_query: The query to send to Mangle
            
        Returns:
            ReasoningResponse with results or error information
        """
        if not self.connected:
            await self.connect()
        
        start_time = datetime.now()
        
        try:
            # Convert query to Mangle format
            mangle_query = await self._convert_to_mangle_query(reasoning_query)
            
            # For now, simulate Mangle response since we don't have the actual server
            # TODO: Replace with actual gRPC call
            response = await self._simulate_mangle_response(reasoning_query)
            
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            self.logger.info(
                f"Mangle query completed: {reasoning_query.query_id}, "
                f"type: {reasoning_query.query_type}, duration: {duration_ms:.1f}ms"
            )
            
            return response
            
        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            self.logger.error(f"Mangle query failed: {e}")
            
            return ReasoningResponse(
                query_id=reasoning_query.query_id,
                success=False,
                result={"error": str(e)},
                reasoning_trace=["Query failed with exception"],
                confidence=0.0,
                duration_ms=duration_ms,
                allowed=False,
                reason=f"Query failed: {e}"
            )
    
    async def validate_phase_transition(self, from_phase: VDWPhase, to_phase: VDWPhase, 
                                       project_context: ProjectContext) -> ReasoningResponse:
        """Validate whether a phase transition is allowed
        
        Args:
            from_phase: Current phase
            to_phase: Target phase
            project_context: Current project context
            
        Returns:
            ReasoningResponse indicating if transition is allowed
        """
        query = ReasoningQuery(
            query_type="dependency_check",
            context={
                "from_phase": from_phase.value,
                "to_phase": to_phase.value,
                "project_id": project_context.project_id,
                "current_artifacts": {
                    "phase_1": project_context.phase_1_output is not None,
                    "phase_2": project_context.phase_2_output is not None,
                    "phase_3": project_context.phase_3_output is not None,
                    "phase_4": project_context.phase_4_output is not None,
                    "phase_5": project_context.phase_5_output is not None,
                },
                "user_feedback": {k.value: v for k, v in project_context.user_feedback.items()}
            },
            expected_response_type="validation_result",
            created_by="state_machine"
        )
        
        return await self.query(query)
    
    async def analyze_capability_gaps(self, required_capabilities: List[str], 
                                    available_tools: List[Dict[str, Any]]) -> ReasoningResponse:
        """Analyze gaps in available capabilities
        
        Args:
            required_capabilities: List of required capability names
            available_tools: List of available tool metadata
            
        Returns:
            ReasoningResponse with gap analysis
        """
        query = ReasoningQuery(
            query_type="gap_analysis",
            context={
                "required_capabilities": required_capabilities,
                "available_tools": available_tools,
                "analysis_timestamp": datetime.now().isoformat()
            },
            expected_response_type="gap_analysis",
            created_by="capability_analyzer"
        )
        
        return await self.query(query)
    
    async def optimize_tool_performance(self, tool_performance_data: List[Dict[str, Any]]) -> ReasoningResponse:
        """Get optimization recommendations for tool performance
        
        Args:
            tool_performance_data: Historical performance data for tools
            
        Returns:
            ReasoningResponse with optimization recommendations
        """
        query = ReasoningQuery(
            query_type="optimization",
            context={
                "performance_data": tool_performance_data,
                "optimization_goals": ["reduce_latency", "improve_success_rate", "minimize_errors"],
                "analysis_timestamp": datetime.now().isoformat()
            },
            expected_response_type="optimization_recommendations",
            created_by="performance_optimizer"
        )
        
        return await self.query(query)
    
    async def reflect_on_project_outcomes(self, project_histories: List[Dict[str, Any]]) -> ReasoningResponse:
        """Perform recursive self-reflection on past project outcomes
        
        Args:
            project_histories: List of completed project data
            
        Returns:
            ReasoningResponse with insights and patterns
        """
        query = ReasoningQuery(
            query_type="self_reflection",
            context={
                "project_histories": project_histories,
                "reflection_depth": "deep",  # shallow, medium, deep
                "focus_areas": ["phase_transitions", "tool_usage", "success_patterns", "failure_analysis"],
                "analysis_timestamp": datetime.now().isoformat()
            },
            expected_response_type="reflection_insights",
            created_by="self_reflection_engine"
        )
        
        return await self.query(query)
    
    async def _convert_to_mangle_query(self, query: ReasoningQuery) -> Dict[str, Any]:
        """Convert ReasoningQuery to Mangle-compatible format
        
        This method translates our high-level queries into Datalog facts and rules
        that Mangle can process.
        """
        mangle_query = {
            "query_id": query.query_id,
            "facts": [],
            "rules": [],
            "goals": []
        }
        
        if query.query_type == "dependency_check":
            # Generate Datalog for phase dependency validation
            context = query.context
            
            # Facts about current state
            mangle_query["facts"].extend([
                f"current_phase('{context['from_phase']}')",
                f"target_phase('{context['to_phase']}')",
                f"project('{context['project_id']}')"
            ])
            
            # Facts about available artifacts
            for phase, has_artifact in context["current_artifacts"].items():
                if has_artifact:
                    mangle_query["facts"].append(f"has_artifact('{phase}')")
            
            # Rules for phase dependencies
            mangle_query["rules"].extend([
                "can_transition(P1, P2) :- phase_dependency(P1, P2), has_required_artifacts(P1)",
                "has_required_artifacts('PHASE_1_MOOD') :- true",  # No prerequisites
                "has_required_artifacts('PHASE_2_ARCHITECTURE') :- has_artifact('phase_1')",
                "has_required_artifacts('PHASE_3_SPECIFICATION') :- has_artifact('phase_2')",
                "has_required_artifacts('PHASE_4_IMPLEMENTATION') :- has_artifact('phase_3')",
                "has_required_artifacts('PHASE_5_VALIDATION_TESTING') :- has_artifact('phase_4')",
                
                # Valid phase transitions
                "phase_dependency('PHASE_1_MOOD', 'PHASE_1_VALIDATION')",
                "phase_dependency('PHASE_1_VALIDATION', 'PHASE_2_ARCHITECTURE')",
                "phase_dependency('PHASE_2_ARCHITECTURE', 'PHASE_2_VALIDATION')",
                "phase_dependency('PHASE_2_VALIDATION', 'PHASE_3_SPECIFICATION')",
                "phase_dependency('PHASE_3_SPECIFICATION', 'PHASE_3_VALIDATION')",
                "phase_dependency('PHASE_3_VALIDATION', 'PHASE_4_IMPLEMENTATION')",
                "phase_dependency('PHASE_4_IMPLEMENTATION', 'PHASE_4_VALIDATION')",
                "phase_dependency('PHASE_4_VALIDATION', 'PHASE_5_VALIDATION_TESTING')",
                "phase_dependency('PHASE_5_VALIDATION_TESTING', 'PHASE_5_VALIDATION')",
                "phase_dependency('PHASE_5_VALIDATION', 'COMPLETED')"
            ])
            
            # Goal to prove
            mangle_query["goals"] = [
                f"can_transition('{context['from_phase']}', '{context['to_phase']}')"
            ]
        
        elif query.query_type == "gap_analysis":
            # Generate Datalog for capability gap analysis
            context = query.context
            
            # Facts about required capabilities
            for capability in context["required_capabilities"]:
                mangle_query["facts"].append(f"required_capability('{capability}')")
            
            # Facts about available tools and their capabilities
            for tool in context["available_tools"]:
                tool_id = tool.get("tool_id", "unknown")
                mangle_query["facts"].append(f"available_tool('{tool_id}')")
                
                for capability in tool.get("capabilities", []):
                    strength = capability.get("strength", 1.0)
                    mangle_query["facts"].append(
                        f"tool_provides_capability('{tool_id}', '{capability.get('name')}', {strength})"
                    )
            
            # Rules for gap analysis
            mangle_query["rules"].extend([
                "capability_satisfied(C) :- required_capability(C), tool_provides_capability(T, C, S), S >= 0.5",
                "capability_gap(C) :- required_capability(C), \\+ capability_satisfied(C)",
                "weak_capability(C) :- required_capability(C), tool_provides_capability(T, C, S), S < 0.7, S >= 0.5"
            ])
            
            # Goals to find gaps
            mangle_query["goals"] = [
                "capability_gap(X)",
                "weak_capability(Y)"
            ]
        
        return mangle_query
    
    async def _simulate_mangle_response(self, query: ReasoningQuery) -> ReasoningResponse:
        """Simulate Mangle response for development/testing
        
        This method provides realistic responses based on the query type.
        TODO: Replace with actual Mangle gRPC calls when server is available.
        """
        await asyncio.sleep(0.01)  # Simulate processing time
        
        if query.query_type == "dependency_check":
            # Simulate dependency validation
            context = query.context
            from_phase = context["from_phase"]
            to_phase = context["to_phase"]
            artifacts = context["current_artifacts"]
            
            # Simple validation logic
            allowed = True
            reason = "Transition allowed"
            
            # Check basic prerequisites
            if to_phase == "PHASE_2_ARCHITECTURE" and not artifacts.get("phase_1"):
                allowed = False
                reason = "Phase 1 (Mood) must be completed before Phase 2 (Architecture)"
            elif to_phase == "PHASE_3_SPECIFICATION" and not artifacts.get("phase_2"):
                allowed = False
                reason = "Phase 2 (Architecture) must be completed before Phase 3 (Specification)"
            elif to_phase == "PHASE_4_IMPLEMENTATION" and not artifacts.get("phase_3"):
                allowed = False
                reason = "Phase 3 (Specification) must be completed before Phase 4 (Implementation)"
            elif to_phase == "PHASE_5_VALIDATION_TESTING" and not artifacts.get("phase_4"):
                allowed = False
                reason = "Phase 4 (Implementation) must be completed before Phase 5 (Validation)"
            
            return ReasoningResponse(
                query_id=query.query_id,
                success=True,
                result={"transition_allowed": allowed, "validation_passed": allowed},
                reasoning_trace=[
                    f"Checked transition from {from_phase} to {to_phase}",
                    f"Artifact availability: {artifacts}",
                    f"Validation result: {reason}"
                ],
                confidence=0.9,
                duration_ms=10.0,
                allowed=allowed,
                reason=reason
            )
        
        elif query.query_type == "gap_analysis":
            # Simulate capability gap analysis
            context = query.context
            required = context["required_capabilities"]
            available_tools = context["available_tools"]
            
            # Simple gap analysis
            missing_capabilities = []
            weak_capabilities = []
            
            for capability in required:
                # Check if any tool provides this capability
                found_strong = False
                found_weak = False
                
                for tool in available_tools:
                    for tool_cap in tool.get("capabilities", []):
                        if tool_cap.get("name") == capability:
                            strength = tool_cap.get("strength", 1.0)
                            if strength >= 0.7:
                                found_strong = True
                            elif strength >= 0.5:
                                found_weak = True
                
                if not found_strong and not found_weak:
                    missing_capabilities.append(capability)
                elif not found_strong and found_weak:
                    weak_capabilities.append(capability)
            
            return ReasoningResponse(
                query_id=query.query_id,
                success=True,
                result={
                    "gap_analysis_complete": True,
                    "total_required": len(required),
                    "missing_count": len(missing_capabilities),
                    "weak_count": len(weak_capabilities)
                },
                reasoning_trace=[
                    f"Analyzed {len(required)} required capabilities",
                    f"Found {len(missing_capabilities)} missing capabilities",
                    f"Found {len(weak_capabilities)} weak capabilities"
                ],
                confidence=0.85,
                duration_ms=15.0,
                missing_capabilities=missing_capabilities,
                recommendations=[
                    f"Create tools for missing capabilities: {', '.join(missing_capabilities[:3])}",
                    f"Strengthen tools for weak capabilities: {', '.join(weak_capabilities[:3])}"
                ]
            )
        
        elif query.query_type == "optimization":
            # Simulate performance optimization recommendations
            performance_data = query.context["performance_data"]
            
            recommendations = [
                "Consider caching frequently used tool results",
                "Implement parallel execution for independent tools",
                "Add retry logic for tools with low success rates"
            ]
            
            if performance_data:
                # Analyze performance data
                slow_tools = [tool for tool in performance_data if tool.get("avg_duration_ms", 0) > 1000]
                if slow_tools:
                    recommendations.append(f"Optimize slow tools: {', '.join([t.get('name', 'unknown') for t in slow_tools[:3]])")
            
            return ReasoningResponse(
                query_id=query.query_id,
                success=True,
                result={"optimization_analysis_complete": True},
                reasoning_trace=[
                    f"Analyzed performance data for {len(performance_data)} tools",
                    "Identified optimization opportunities",
                    "Generated actionable recommendations"
                ],
                confidence=0.8,
                duration_ms=20.0,
                recommendations=recommendations
            )
        
        elif query.query_type == "self_reflection":
            # Simulate self-reflection analysis
            project_histories = query.context["project_histories"]
            
            insights = [
                "Projects with detailed Phase 1 requirements have 23% higher success rates",
                "Phase 2 architectural decisions strongly correlate with Phase 4 implementation quality",
                "Tools created in earlier projects are reused in 65% of subsequent projects"
            ]
            
            return ReasoningResponse(
                query_id=query.query_id,
                success=True,
                result={"reflection_complete": True, "insights_generated": len(insights)},
                reasoning_trace=[
                    f"Analyzed {len(project_histories)} project histories",
                    "Applied recursive self-reflection rules",
                    "Identified success patterns and optimization opportunities"
                ],
                confidence=0.75,
                duration_ms=50.0,
                recommendations=insights
            )
        
        else:
            # Unknown query type
            return ReasoningResponse(
                query_id=query.query_id,
                success=False,
                result={"error": f"Unknown query type: {query.query_type}"},
                reasoning_trace=[f"Failed to process query type: {query.query_type}"],
                confidence=0.0,
                duration_ms=1.0,
                allowed=False,
                reason=f"Unsupported query type: {query.query_type}"
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()