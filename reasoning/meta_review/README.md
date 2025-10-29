# Meta-Review and Mental Game Analysis System

**Version 2.0.0** - Comprehensive Implementation

This directory contains a complete meta-cognitive analysis system for evaluating and improving reasoning processes across the VDW lifecycle. This system has evolved from a simple meta-review framework to a comprehensive, self-improving cognitive analysis platform.

## 🚀 **COMPLETED PHASES (5 out of 13)**

### ✅ **Phase 1: Core Meta-Review Framework**
- `core.py` — Core framework with `MetaReviewFramework`, `MentalGameAnalyzer`, data models, scoring, and insight generation
- `perspectives.py` — Modular analyzers for Skeptical, Novice, and Cross-Domain perspectives
- `validators.py` — Quantitative metrics and validation gates for phase transitions
- `integration.py` — High-level helper to run meta-review at VDW phase gates

### ✅ **Phase 7: Temporal and Longitudinal Analysis**
- `temporal.py` — Version control for reasoning, reasoning archaeology, learning curves, and post-mortem analysis
- Recovers deleted reasoning paths and tracks quality evolution over time
- Implements "reasoning archaeology" to find valuable insights in discarded content

### ✅ **Phase 8: Collaborative and Social Meta-Review**
- `collaborative.py` — Multi-reviewer consensus, disagreement resolution, and reviewer calibration
- Consensus engine for calculating agreement across multiple reviewers
- Reviewer calibration system to maintain consistent standards

### ✅ **Phase 9: Meta-Meta Analysis and Recursive Improvement**
- `recursive.py` — Recursive analysis of the review process itself with self-improving systems
- Detects diminishing returns in meta-cognitive analysis
- Automatically implements low-complexity, high-impact improvements

### ✅ **Phase 10: Full VDW Integration**
- `mcp_server.py` — Complete MCP server exposing all capabilities as tools
- `meta_review_agent.py` — Agent for automatic phase validation
- 10 comprehensive MCP tools for all meta-review functions

---

## 🛠️ **Quick Start**

### Basic Meta-Review
```python
from reasoning.meta_review import MetaReviewFramework, ReasoningArtifact, VDWIntegration
from reasoning.meta_review import QualityMetrics, ValidationGates

# Setup
framework = MetaReviewFramework()
integration = VDWIntegration(
    framework=framework,
    gates=ValidationGates(min_score=7.5, min_breadth=3),
    metrics=QualityMetrics(),
)

# Review reasoning content
result = integration.review_phase_output(
    title="Phase 2 Architecture Review",
    content="""Architecture details with evidence, examples, and counterpoints.
    This content should include sufficient depth to avoid skeptical analysis penalties.
    """,
    phase="phase2",
    author="architect",
)

print(f"Score: {result['result']['overall_score']:.1f}/10")
if integration.should_advance_phase(result):
    print("✅ Phase can advance")
else:
    print("❌ Hold phase:", result["validation_errors"])
```

### Temporal Analysis
```python
from reasoning.meta_review import ReasoningVersionControl, ReasoningArtifact

# Track reasoning evolution
version_control = ReasoningVersionControl()

# Create and track versions
artifact = ReasoningArtifact(title="Design Doc", content="Initial version...")
version1 = version_control.commit_version(artifact)

# Update and track changes
artifact.content = "Revised version with more evidence..."
version2 = version_control.commit_version(artifact)

# Analyze evolution
evolution = version_control.analyze_evolution(artifact.id)
print(f"Versions: {evolution['version_count']}")
print(f"Recovered insights: {len(evolution['recovered_insights'])}")
```

### Collaborative Review
```python
from reasoning.meta_review import CollaborativeMetaReview, Reviewer, ReviewerExpertise

# Setup collaborative system
collaborative = CollaborativeMetaReview()

# Add reviewers
expert_reviewer = Reviewer(
    reviewer_id="expert_1",
    name="Senior Architect",
    expertise_level=ReviewerExpertise.EXPERT,
    domain_specializations=["architecture", "scalability"]
)

# Start collaborative review
review_id = collaborative.initiate_collaborative_review(artifact)
result = collaborative.get_collaborative_result(review_id)
```

### MCP Server Usage
```python
from reasoning.meta_review import MetaReviewMCPServer

# Initialize MCP server
server = MetaReviewMCPServer()

# Use as MCP tools
tools = server.list_tools()  # Get available tools
result = server.call_tool("conduct_meta_review", {
    "title": "Analysis Document",
    "content": "Content to analyze...",
    "phase": "phase3",
    "depth": "deep"
})
```

### CLI Usage
```bash
# Basic meta-review
python -m reasoning.meta_review.cli --file reasoning/document.md --phase phase2

# With custom thresholds
python -c "
from reasoning.meta_review import MetaReviewMCPServer
server = MetaReviewMCPServer()
result = server.call_tool('validate_phase_gate', {
    'title': 'Test',
    'content': 'Content with evidence and examples for validation.',
    'phase': 'phase2',
    'min_score': 8.0
})
print(result['gate_decision'])
"
```

---

## 🏗️ **Architecture Overview**

```
reasoning/meta_review/
├── core.py                 # Core framework & mental games
├── perspectives.py         # Modular perspective analyzers
├── validators.py           # Quality metrics & validation gates
├── integration.py          # VDW integration helper
├── temporal.py             # Version control & archaeology
├── collaborative.py        # Multi-reviewer consensus
├── recursive.py            # Self-improving meta-analysis
├── mcp_server.py          # Complete MCP server
├── cli.py                 # Command-line interface
└── README.md              # This file
```

### Integration Points
- **VDW Agents**: `agents/meta_review_agent.py` automatically validates phase outputs
- **MCP Tools**: 10 tools exposed for external integration
- **Version Control**: Persistent storage of reasoning evolution
- **Collaborative**: Multi-reviewer consensus and calibration

---

## 📊 **Key Features Implemented**

### 🔍 **Multi-Perspective Analysis**
- **Skeptical**: Looks for evidence gaps, cherry-picking, reasoning holes
- **Novice**: Checks accessibility, jargon density, need for examples
- **Cross-Domain**: Evaluates transferability and universal principles

### 📈 **Temporal Intelligence**
- **Version Control**: Track all reasoning iterations with diffs
- **Reasoning Archaeology**: Recover valuable insights from deleted content
- **Learning Curves**: Measure improvement velocity and detect plateaus
- **Post-Mortem**: Analyze failed attempts for pattern recognition

### 👥 **Collaborative Consensus**
- **Multi-Reviewer**: Aggregate insights from multiple perspectives
- **Disagreement Resolution**: Structured approaches to resolve conflicts
- **Calibration**: Maintain reviewer consistency through baseline alignment
- **Expertise Weighting**: Weight contributions based on demonstrated expertise

### 🔄 **Recursive Self-Improvement**
- **Meta-Meta Analysis**: Review the review process itself
- **Diminishing Returns**: Detect when additional analysis provides minimal value
- **Auto-Implementation**: Automatically apply low-risk, high-impact improvements
- **System Evolution**: Track how the meta-review system improves over time

### 🛠️ **Production Ready**
- **MCP Integration**: 10 comprehensive tools for external use
- **Validation Gates**: Automatic phase advancement decisions
- **Metrics Dashboard**: Quantitative tracking of review quality
- **Error Handling**: Graceful degradation and failure recovery

---

## 🎯 **Remaining TODO (Phases 6, 11-13)**

### **Phase 6: Synthesis and Integration of Meta-Insights**
- Cross-pattern analysis mapping
- Adaptive review protocols
- Context-sensitive checklists

### **Phase 11: Quantitative Validation and Metrics**
- A/B testing frameworks
- Statistical validation models
- Performance baselines and benchmarks

### **Phase 12: Documentation & Knowledge Transfer**
- Comprehensive methodology guide
- Training materials and certification
- Case study libraries

### **Phase 13: Continuous Calibration**
- Community of practice
- Regular meta-meta-reviews
- Quality assurance protocols

---

## 📋 **Current Status: ~38% Complete**

**Completed**: 5 out of 13 phases  
**Status**: Production-ready core system with advanced capabilities  
**Next Priority**: Phase 11 (Quantitative Validation) or Phase 6 (Synthesis)

The system is now sophisticated enough for production use while continuing evolution toward full meta-cognitive analysis capabilities.
