"""Temporal and Longitudinal Analysis for Meta-Review System.

Phase 7: Version control for reasoning, reasoning archaeology, and temporal tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path

from .core import ReasoningArtifact, MetaReviewResult, ReviewInsight


@dataclass
class ReasoningVersion:
    """Represents a versioned snapshot of a reasoning artifact."""
    version_id: str
    artifact_id: str
    content: str
    metadata: Dict
    timestamp: datetime
    parent_version: Optional[str] = None
    diff_summary: Optional[str] = None
    
    @classmethod
    def from_artifact(cls, artifact: ReasoningArtifact, parent_version: Optional[str] = None):
        """Create version from artifact."""
        content_hash = hashlib.sha256(artifact.content.encode()).hexdigest()[:12]
        version_id = f"{artifact.id}_{content_hash}_{int(datetime.now().timestamp())}"
        
        return cls(
            version_id=version_id,
            artifact_id=artifact.id,
            content=artifact.content,
            metadata=artifact.metadata.copy(),
            timestamp=datetime.now(),
            parent_version=parent_version
        )


@dataclass
class ReasoningChange:
    """Represents a change between reasoning versions."""
    change_type: str  # "addition", "deletion", "modification", "restructure"
    location: str  # Line numbers or section identifier
    old_content: str
    new_content: str
    confidence: float  # How confident we are this change was intentional
    semantic_impact: str  # "low", "medium", "high"


class ReasoningArchaeologist:
    """Reconstructs implicit reasoning steps and recovers deleted reasoning paths."""
    
    def __init__(self):
        self.deleted_patterns = [
            "TODO:", "FIXME:", "NOTE:", "QUESTION:", "CONSIDER:",
            "maybe", "perhaps", "not sure", "need to think"
        ]
        
    def extract_implicit_steps(self, content: str) -> List[str]:
        """Identify implicit reasoning steps not explicitly documented."""
        implicit_steps = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines[:-1]):
            current = line.strip()
            next_line = lines[i + 1].strip()
            
            # Look for logical jumps
            if self._has_conclusion_words(next_line) and not self._has_evidence_words(current):
                implicit_steps.append(f"Line {i+1}-{i+2}: Missing evidence bridge between '{current}' and '{next_line}'")
            
            # Look for unexplained transitions
            if self._is_topic_shift(current, next_line):
                implicit_steps.append(f"Line {i+1}-{i+2}: Abrupt topic shift without transition explanation")
        
        return implicit_steps
    
    def recover_deleted_reasoning(self, versions: List[ReasoningVersion]) -> List[str]:
        """Recover valuable insights from deleted reasoning attempts."""
        if len(versions) < 2:
            return []
        
        recovered_insights = []
        
        # Compare consecutive versions to find deleted content
        for i in range(len(versions) - 1):
            older = versions[i]
            newer = versions[i + 1]
            
            deleted_sections = self._find_deleted_content(older.content, newer.content)
            
            for section in deleted_sections:
                if self._contains_valuable_insight(section):
                    recovered_insights.append({
                        "deleted_from": older.version_id,
                        "content": section,
                        "recovery_reason": self._assess_deletion_reason(section),
                        "value_assessment": self._assess_insight_value(section)
                    })
        
        return recovered_insights
    
    def _has_conclusion_words(self, text: str) -> bool:
        conclusion_words = ["therefore", "thus", "hence", "consequently", "so"]
        return any(word in text.lower() for word in conclusion_words)
    
    def _has_evidence_words(self, text: str) -> bool:
        evidence_words = ["because", "since", "given", "evidence", "data", "research"]
        return any(word in text.lower() for word in evidence_words)
    
    def _is_topic_shift(self, current: str, next_line: str) -> bool:
        """Simple heuristic for topic shifts - could be enhanced with NLP."""
        current_words = set(current.lower().split())
        next_words = set(next_line.lower().split())
        
        if len(current_words) == 0 or len(next_words) == 0:
            return False
        
        # If less than 20% word overlap, consider it a topic shift
        overlap = len(current_words.intersection(next_words))
        total_unique = len(current_words.union(next_words))
        
        return overlap / total_unique < 0.2 if total_unique > 0 else False
    
    def _find_deleted_content(self, old_content: str, new_content: str) -> List[str]:
        """Simple diff to find deleted sections."""
        old_lines = set(old_content.split('\n'))
        new_lines = set(new_content.split('\n'))
        
        deleted_lines = old_lines - new_lines
        return [line for line in deleted_lines if line.strip()]
    
    def _contains_valuable_insight(self, content: str) -> bool:
        """Assess if deleted content contains valuable insights."""
        value_indicators = [
            "insight", "pattern", "principle", "lesson", "observation",
            "discovered", "realized", "found", "noticed", "important"
        ]
        return any(indicator in content.lower() for indicator in value_indicators)
    
    def _assess_deletion_reason(self, content: str) -> str:
        """Guess why content was deleted."""
        if any(pattern in content.lower() for pattern in self.deleted_patterns):
            return "temporary_note_cleanup"
        elif len(content) < 20:
            return "too_brief"
        elif "error" in content.lower() or "wrong" in content.lower():
            return "correction"
        else:
            return "unknown_refactoring"
    
    def _assess_insight_value(self, content: str) -> str:
        """Assess the potential value of deleted insight."""
        if len(content) > 100 and self._contains_valuable_insight(content):
            return "high"
        elif self._contains_valuable_insight(content):
            return "medium"
        else:
            return "low"


class ReasoningVersionControl:
    """Manages versioning and temporal analysis of reasoning artifacts."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path(".reasoning_history")
        self.storage_path.mkdir(exist_ok=True)
        
        self.versions: Dict[str, List[ReasoningVersion]] = {}
        self.review_history: Dict[str, List[MetaReviewResult]] = {}
        self.archaeologist = ReasoningArchaeologist()
    
    def commit_version(self, artifact: ReasoningArtifact) -> ReasoningVersion:
        """Create and store a new version of the reasoning artifact."""
        if artifact.id not in self.versions:
            self.versions[artifact.id] = []
        
        parent_version = self.versions[artifact.id][-1].version_id if self.versions[artifact.id] else None
        version = ReasoningVersion.from_artifact(artifact, parent_version)
        
        # Calculate diff if there's a parent
        if parent_version and self.versions[artifact.id]:
            previous_content = self.versions[artifact.id][-1].content
            version.diff_summary = self._calculate_diff_summary(previous_content, artifact.content)
        
        self.versions[artifact.id].append(version)
        self._persist_version(version)
        
        return version
    
    def get_version_history(self, artifact_id: str) -> List[ReasoningVersion]:
        """Get all versions of an artifact."""
        return self.versions.get(artifact_id, [])
    
    def analyze_evolution(self, artifact_id: str) -> Dict:
        """Analyze how reasoning has evolved over time."""
        versions = self.get_version_history(artifact_id)
        if len(versions) < 2:
            return {"error": "Need at least 2 versions for evolution analysis"}
        
        # Calculate metrics over time
        evolution_metrics = {
            "version_count": len(versions),
            "time_span": (versions[-1].timestamp - versions[0].timestamp).total_seconds() / 3600,  # hours
            "content_growth": len(versions[-1].content) - len(versions[0].content),
            "iteration_frequency": [],
            "quality_trajectory": [],
            "implicit_reasoning_gaps": [],
            "recovered_insights": []
        }
        
        # Calculate iteration frequency
        for i in range(1, len(versions)):
            time_diff = (versions[i].timestamp - versions[i-1].timestamp).total_seconds() / 60  # minutes
            evolution_metrics["iteration_frequency"].append(time_diff)
        
        # Analyze implicit reasoning gaps
        for version in versions:
            gaps = self.archaeologist.extract_implicit_steps(version.content)
            evolution_metrics["implicit_reasoning_gaps"].append({
                "version": version.version_id,
                "gaps": gaps,
                "gap_count": len(gaps)
            })
        
        # Recover deleted insights
        evolution_metrics["recovered_insights"] = self.archaeologist.recover_deleted_reasoning(versions)
        
        return evolution_metrics
    
    def get_learning_curve(self, artifact_id: str) -> Dict:
        """Analyze learning progression through reasoning iterations."""
        versions = self.get_version_history(artifact_id)
        reviews = self.review_history.get(artifact_id, [])
        
        learning_curve = {
            "improvement_rate": 0.0,
            "plateau_detection": False,
            "breakthrough_moments": [],
            "regression_points": [],
            "mastery_indicators": []
        }
        
        if len(reviews) >= 3:
            scores = [review.overall_score for review in reviews]
            
            # Calculate improvement rate (slope of best fit line)
            n = len(scores)
            sum_x = sum(range(n))
            sum_y = sum(scores)
            sum_xy = sum(i * score for i, score in enumerate(scores))
            sum_x2 = sum(i * i for i in range(n))
            
            if n * sum_x2 - sum_x * sum_x != 0:
                learning_curve["improvement_rate"] = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Detect plateaus (3+ consecutive reviews with < 0.5 point improvement)
            plateau_threshold = 0.5
            consecutive_small_improvements = 0
            
            for i in range(1, len(scores)):
                improvement = scores[i] - scores[i-1]
                if improvement < plateau_threshold:
                    consecutive_small_improvements += 1
                else:
                    consecutive_small_improvements = 0
                
                if consecutive_small_improvements >= 2:
                    learning_curve["plateau_detection"] = True
                    break
            
            # Detect breakthroughs (1.5+ point jumps)
            for i in range(1, len(scores)):
                improvement = scores[i] - scores[i-1]
                if improvement >= 1.5:
                    learning_curve["breakthrough_moments"].append({
                        "version_index": i,
                        "improvement": improvement,
                        "new_score": scores[i]
                    })
                elif improvement <= -1.0:
                    learning_curve["regression_points"].append({
                        "version_index": i,
                        "regression": improvement,
                        "new_score": scores[i]
                    })
        
        return learning_curve
    
    def conduct_post_mortem(self, artifact_id: str, failure_threshold: float = 6.0) -> Dict:
        """Analyze failed reasoning attempts for learning opportunities."""
        reviews = self.review_history.get(artifact_id, [])
        failed_reviews = [r for r in reviews if r.overall_score < failure_threshold]
        
        if not failed_reviews:
            return {"message": "No failed reasoning attempts found"}
        
        post_mortem = {
            "failure_count": len(failed_reviews),
            "common_failure_patterns": {},
            "recovery_strategies": [],
            "lessons_learned": []
        }
        
        # Analyze common failure patterns
        for review in failed_reviews:
            for insight in review.insights:
                if insight.category not in post_mortem["common_failure_patterns"]:
                    post_mortem["common_failure_patterns"][insight.category] = []
                post_mortem["common_failure_patterns"][insight.category].append(insight.insight)
        
        # Generate recovery strategies based on patterns
        for category, insights in post_mortem["common_failure_patterns"].items():
            if len(insights) >= 2:  # Recurring pattern
                if "evidence" in category:
                    post_mortem["recovery_strategies"].append(
                        "Implement systematic evidence collection checklist"
                    )
                elif "accessibility" in category:
                    post_mortem["recovery_strategies"].append(
                        "Add glossary and examples for technical concepts"
                    )
                elif "reasoning_gaps" in category:
                    post_mortem["recovery_strategies"].append(
                        "Use explicit logical connectors (because, therefore, since)"
                    )
        
        return post_mortem
    
    def _calculate_diff_summary(self, old_content: str, new_content: str) -> str:
        """Calculate a summary of changes between versions."""
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        added = len(new_lines) - len(old_lines)
        
        if added > 0:
            return f"Added {added} lines"
        elif added < 0:
            return f"Removed {-added} lines"
        else:
            return "Modified content (same length)"
    
    def _persist_version(self, version: ReasoningVersion):
        """Persist version to storage."""
        version_file = self.storage_path / f"{version.version_id}.json"
        
        version_data = {
            "version_id": version.version_id,
            "artifact_id": version.artifact_id,
            "content": version.content,
            "metadata": version.metadata,
            "timestamp": version.timestamp.isoformat(),
            "parent_version": version.parent_version,
            "diff_summary": version.diff_summary
        }
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
