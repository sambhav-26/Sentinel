"""Agent Framework Documentation for SentinelOS."""

# Agent Framework

SentinelOS uses an agent-based architecture where specialized agents handle different aspects of security analysis.

## Architecture Overview

```
API Request (POST /api/scans)
    ↓
ScanOrchestrator
    ↓
Agent 1: Scanner → Agent 2: Threat → Agent 3: Attack → Agent 4: Patch → Agent 5: Report
    ↓
Database (Findings, Attacks, Patches, Reports)
    ↓
API Response + Report Download
```

## Base Agent Class

All agents inherit from `BaseAgent` and must implement:

### Required Methods

#### `async process(input_data: AgentInput) -> Dict[str, Any]`
Core processing logic. This is where the agent does its work.

```python
async def process(self, input_data: AgentInput) -> Dict[str, Any]:
    """Run code analysis and return findings."""
    # Get scan from database
    scan = await self.session.get(Scan, input_data.scan_id)
    
    # Do analysis
    results = await self.analyze_code(scan.repository_id)
    
    # Save findings
    for result in results:
        finding = Finding(
            id=generate_id(),
            scan_id=input_data.scan_id,
            vulnerability_type=result['type'],
            severity=result['severity'],
            # ... more fields
        )
        self.session.add(finding)
    
    await self.session.flush()
    
    # Return results
    return {
        "findings_count": len(results),
        "findings": results
    }
```

### Optional Methods (Override for Custom Behavior)

#### `async validate_input(input_data: AgentInput) -> None`
Validate input before processing. Base implementation checks scan_id exists.

```python
async def validate_input(self, input_data: AgentInput):
    """Validate input has required fields."""
    await super().validate_input(input_data)
    
    if not input_data.repository_id:
        raise ValueError("repository_id required")
```

#### `async format_output(data: Dict[str, Any]) -> Dict[str, Any]`
Format raw processing output. Base returns `{"message": "...", "data": data}`.

```python
async def format_output(self, data: Dict[str, Any]):
    """Format output for next agent."""
    return {
        "message": f"Found {data['findings_count']} vulnerabilities",
        "data": {
            "findings": data['findings']
        }
    }
```

## Agent Lifecycle

1. **Input Validation** (`validate_input`)
   - Check required fields
   - Verify scan exists
   - Load necessary data

2. **Processing** (`process`)
   - Execute core logic
   - Save results to database
   - Return structured data

3. **Output Formatting** (`format_output`)
   - Structure results for next agent
   - Include summary messages
   - Pass only needed data

4. **Execution** (`execute`)
   - Calls validate → process → format
   - Wraps with error handling
   - Measures execution time
   - Logs to database

5. **Logging** (`log_execution`)
   - Records to agent_logs table
   - Captures success/failure
   - Stores execution time

## Agent Execution Order

### 1. Scanner Agent
**Input**: scan_id, repository_id
**Output**: findings (list of vulnerabilities)

Runs static analysis tools:
- Bandit (Python security)
- Semgrep (SAST patterns)
- Custom rule engines

Saves to: `findings` table

```python
class ScannerAgent(BaseAgent):
    async def process(self, input_data: AgentInput):
        # Run bandit
        bandit_results = run_bandit(repo_path)
        
        # Run semgrep
        semgrep_results = run_semgrep(repo_path)
        
        # Parse and save findings
        for result in bandit_results + semgrep_results:
            finding = Finding(...)
            self.session.add(finding)
        
        return {"findings": parsed_findings}
```

### 2. Threat Agent
**Input**: findings
**Output**: threat classifications

Analyzes findings and assigns:
- Threat types
- OWASP categories
- CWE mappings
- Risk scores

```python
class ThreatAgent(BaseAgent):
    async def process(self, input_data: AgentInput):
        # Get findings from last step
        findings = await get_findings(input_data.scan_id)
        
        # Analyze threats
        for finding in findings:
            threat_type = classify_threat(finding)
            severity = calculate_severity(finding)
            
            finding.threat_type = threat_type
            finding.severity = severity
        
        return {"threats": threat_analysis}
```

### 3. Attack Agent
**Input**: findings, threats
**Output**: attack scenarios

Simulates how vulnerabilities could be exploited:
- Attack paths
- Prerequisites
- Impact scores
- MITRE ATT&CK mapping

Saves to: `attacks` table

```python
class AttackAgent(BaseAgent):
    async def process(self, input_data: AgentInput):
        # Get findings
        findings = await get_findings(input_data.scan_id)
        
        # Generate attacks
        for finding in findings:
            attack = simulate_attack(finding)
            
            attack_record = Attack(
                scan_id=input_data.scan_id,
                finding_id=finding.id,
                attack_type=attack['type'],
                success_probability=attack['prob'],
                impact_score=attack['impact'],
                # ...
            )
            self.session.add(attack_record)
        
        return {"attacks": attacks}
```

### 4. Patch Agent
**Input**: findings, attacks
**Output**: code fixes

Generates remediation code:
- Original vulnerable code
- Fixed code
- Explanation
- Applicability

Saves to: `patches` table

```python
class PatchAgent(BaseAgent):
    async def process(self, input_data: AgentInput):
        # Get findings
        findings = await get_findings(input_data.scan_id)
        
        # Generate patches
        for finding in findings:
            patch = generate_patch(finding)
            
            patch_record = Patch(
                scan_id=input_data.scan_id,
                finding_id=finding.id,
                original_code=patch['original'],
                patched_code=patch['fixed'],
                explanation=patch['why'],
                confidence=patch['confidence'],
                can_auto_apply=patch['auto_apply']
            )
            self.session.add(patch_record)
        
        return {"patches": patches}
```

### 5. Report Agent
**Input**: findings, attacks, patches
**Output**: final report

Compiles all data into comprehensive report:
- Executive summary
- Risk scores
- Remediation recommendations
- PDF export

Saves to: `reports` table

```python
class ReportAgent(BaseAgent):
    async def process(self, input_data: AgentInput):
        # Get all data
        findings = await get_findings(input_data.scan_id)
        attacks = await get_attacks(input_data.scan_id)
        patches = await get_patches(input_data.scan_id)
        
        # Generate report
        report = compile_report(findings, attacks, patches)
        
        # Create record
        report_record = Report(
            scan_id=input_data.scan_id,
            title=report['title'],
            overall_risk_score=report['risk_score'],
            # ... all fields
        )
        self.session.add(report_record)
        
        return {"report": report}
```

## ScanOrchestrator

Coordinates agent execution:

```python
from app.services.orchestrator import ScanOrchestrator
from app.agents.scanner_agent import ScannerAgent
from app.agents.threat_agent import ThreatAgent
# ... import other agents

# Create orchestrator
orchestrator = ScanOrchestrator(db_session)

# Register agents in order
orchestrator.register_agent(ScannerAgent(db_session))
orchestrator.register_agent(ThreatAgent(db_session))
orchestrator.register_agent(AttackAgent(db_session))
orchestrator.register_agent(PatchAgent(db_session))
orchestrator.register_agent(ReportAgent(db_session))

# Execute
success = await orchestrator.execute(
    scan_id="uuid-here",
    repository_id="uuid-here"
)

# Get results
results = orchestrator.get_results()
summary = orchestrator.get_result_summary()
```

## Error Handling

BaseAgent provides automatic error handling:

```python
# If validate_input fails:
# ✓ Catches exception
# ✓ Logs to database
# ✓ Returns AgentOutput with error
# ✓ Next agent still executes

# If process fails:
# ✓ Catches exception
# ✓ Logs to database
# ✓ Returns AgentOutput with error
# ✓ Orchestrator continues

# All errors logged to agent_logs table
```

## Database Integration

### Auto-Logging

Agents automatically log execution:

```python
# In app/models/agent_logs table:
{
    "agent_name": "ScannerAgent",
    "agent_step": 1,
    "log_level": "INFO",
    "message": "Scanner completed: found 12 vulnerabilities",
    "execution_time_ms": 4532,
    "timestamp": "2026-05-28T14:23:45"
}
```

### Session Management

```python
# Agents get AsyncSession from orchestrator
class MyAgent(BaseAgent):
    async def process(self, input_data):
        # Use self.session for all database operations
        scan = await self.session.get(Scan, input_data.scan_id)
        
        # Add records
        self.session.add(new_record)
        await self.session.flush()
        
        # Query
        findings = await self.session.execute(select(Finding))
```

## Dependency Chain Example

```
Agent 1 Output:
{
    "message": "Found 12 vulnerabilities",
    "data": {
        "findings": [
            {"id": "f1", "type": "SQL Injection", "severity": "critical"},
            ...
        ]
    }
}

                    ↓

Agent 2 Input (AgentInput object):
{
    "scan_id": "s1",
    "repository_id": "r1",
    "findings": [...],           # From Agent 1's data
    "findings_count": 12         # From Agent 1's data
}

                    ↓

Agent 2 Process:
# Can access input_data.findings
threat_analysis = analyze(input_data.findings)
```

## Example: Complete Agent Implementation

```python
from app.agents.base import BaseAgent, AgentInput
from typing import Dict, Any

class MyAgent(BaseAgent):
    """Custom agent for specific analysis."""
    
    async def validate_input(self, input_data: AgentInput):
        """Validate input."""
        await super().validate_input(input_data)
        
        if not input_data.repository_id:
            raise ValueError("repository_id required")
    
    async def process(self, input_data: AgentInput) -> Dict[str, Any]:
        """Execute agent logic."""
        self.logger.info(f"Processing scan {input_data.scan_id}")
        
        # Get scan
        scan = await self.session.get(Scan, input_data.scan_id)
        if not scan:
            raise ValueError(f"Scan not found: {input_data.scan_id}")
        
        # Do work
        results = await self.do_analysis(scan)
        
        # Save results
        for result in results:
            record = MyModel(...)
            self.session.add(record)
        
        await self.session.flush()
        
        return {"results": results}
    
    async def format_output(self, data: Dict[str, Any]):
        """Format for next agent."""
        count = len(data.get("results", []))
        return {
            "message": f"Analysis complete: {count} items",
            "data": {
                "results": data["results"]
            }
        }
```

## Async Patterns

All agent operations are async:

```python
# ✓ Correct
async def process(self, input_data):
    findings = await self.session.execute(query)
    return {"findings": findings}

# ✗ Wrong - never block
async def process(self, input_data):
    time.sleep(10)  # BLOCKS! Don't do this
    return {}

# ✓ Use async sleep
import asyncio
async def process(self, input_data):
    await asyncio.sleep(10)  # Non-blocking
    return {}
```

## Testing

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.mark.asyncio
async def test_my_agent():
    # Create test session
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = AsyncSession(engine)
    
    # Create agent
    agent = MyAgent(async_session)
    
    # Execute
    output = await agent.execute(AgentInput(scan_id="test"))
    
    # Assert
    assert output.success
    assert output.data is not None
```

## Next Steps

1. **Implement Specific Agents**:
   - Refactor existing scanner_agent.py to inherit from BaseAgent
   - Implement threat_agent.py, attack_agent.py, patch_agent.py, report_agent.py
   - Test each agent independently

2. **Integrate with API**:
   - Create /api/scans POST endpoint
   - Instantiate orchestrator in route handler
   - Pass async session from FastAPI dependency injection
   - Return scan ID for polling

3. **Background Jobs**:
   - Use Celery to run scans in background
   - Return 202 Accepted immediately
   - Use WebSocket for real-time progress updates

4. **Progress Tracking**:
   - Orchestrator updates scan.progress after each agent
   - Frontend polls /api/scans/{id} for progress
   - Frontend displays agent names and completion status
