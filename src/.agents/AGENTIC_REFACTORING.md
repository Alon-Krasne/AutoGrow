# Agentic Workflow Refactoring

**Date**: November 13, 2025  
**Type**: Terminology Update & File Rename

## Overview

Renamed `agent_workflow.py` to `agentic_workflow.py` to better reflect the nature of the system. This clarifies the distinction between:

- **Agent**: Autonomous systems that operate independently
- **Agentic**: Role-based workflows that use LLM calls for decision-making

## Changes Made

### 1. File Renames
- `/src/agent_workflow.py` → `/src/agentic_workflow.py`
- `/src/claude-agent/tests/test_agent_workflow.py` → `/src/claude-agent/tests/test_agentic_workflow.py`

### 2. Class Renames
- `AgentWorkflow` → `AgenticWorkflow`
- `TestAgentWorkflow` → `TestAgenticWorkflow`

### 3. Updated Files

#### Source Code
- `/src/agentic_workflow.py`
  - Updated module docstring
  - Renamed class to `AgenticWorkflow`
  - Updated log messages

#### Tests
- `/src/claude-agent/tests/test_agentic_workflow.py`
  - Updated imports
  - Updated class name
  - Updated all patch references

#### Scripts
- `/src/claude-agent/scripts/entrypoint.sh`
  - Updated Python script path
  - Updated log messages

#### Documentation
- `/src/claude-agent/ARCHITECTURE.md`
  - Updated file references
  - Updated class name
  - Updated diagrams

- `/src/claude-agent/WORKFLOW_DIAGRAM.md`
  - Updated file references
  - Updated class name in diagrams
  - Updated timeline references

- `/src/claude-agent/.agents/PROMPT_SYSTEM_SUMMARY.md`
  - Updated file references
  - Updated class name in diagrams

### 4. Cleanup
- Removed `.pytest_cache` directory to clear old test references

## Project Structure

The project now supports multiple agent implementations:

```
src/
├── agentic_workflow.py       # Shared workflow orchestrator
├── config.py                 # Shared configuration
├── prompt_loader.py          # Shared prompt system
├── prompts/                  # Shared prompt templates
│   ├── default.txt
│   ├── minimal.txt
│   └── detailed.txt
├── utils/                    # Shared utilities
│   └── logger.py
├── claude-agent/             # Claude-specific implementation
│   ├── src/                  # Symlinks to shared code
│   ├── tests/
│   ├── scripts/
│   └── [docs]
└── gemini-agent/             # Gemini-specific implementation (future)
```

## Rationale

### Why "Agentic" vs "Agent"?

1. **Accuracy**: The system uses LLM calls within a structured workflow, not autonomous operation
2. **Clarity**: Distinguishes between different AI paradigms
3. **Industry Standard**: "Agentic" is increasingly used to describe LLM-powered role-based systems

### Benefits

- **Clear terminology** that accurately describes the system architecture
- **Better documentation** for future developers
- **Alignment with industry standards** and best practices
- **Easier to explain** the difference between autonomous agents and LLM-guided workflows

## Verification

All references have been updated:
- ✅ Source code files
- ✅ Test files
- ✅ Shell scripts
- ✅ Documentation files
- ✅ Diagrams and examples

## Next Steps

1. Consider similar updates for other agent implementations (Gemini)
2. Update any external documentation or README files
3. Communicate changes to team members
4. Update CI/CD pipelines if they reference the old filenames

## Notes

- The shared code structure allows multiple agent implementations to reuse common components
- Each agent folder (claude-agent, gemini-agent) can have its own specific configuration
- Prompts are shared across all implementations for consistency
