# Integration Tests Guide

Complete guide for running integration tests with real API calls and CLI usage.

## 📋 Overview

Integration tests verify the actual functionality of AI agents by making real API calls and using real CLI tools. Unlike unit tests which use mocks, integration tests ensure everything works end-to-end.

## 🎯 Test Coverage

### GeminiAgent Integration Tests
**File**: `tests/integration/test_gemini_agent_integration.py`

**Test Categories**:
1. **Basic Integration** (2 tests)
   - Real query to Gemini API
   - Query with specific model

2. **File Operations** (4 tests)
   - Query with file input
   - Code review
   - Documentation generation
   - Log analysis

3. **Batch Processing** (1 test)
   - Process multiple files

4. **Options** (3 tests)
   - YOLO mode
   - Debug mode
   - JSON format

5. **Error Handling** (3 tests)
   - Invalid API key
   - File not found
   - Empty prompt

6. **End-to-End** (2 tests)
   - Complete workflow
   - Multi-file analysis

**Total**: 15 integration tests

### ClaudeAgent Integration Tests
**File**: `tests/integration/test_claude_cli_agent_integration.py`

**Test Categories**:
1. **Basic Integration** (3 tests)
   - Real query to Claude CLI
   - Query with system prompt
   - Text format output

2. **File Operations** (4 tests)
   - Query with stdin
   - Code review
   - Documentation generation
   - Code fixing

3. **Batch Processing** (2 tests)
   - Process multiple files
   - Handle errors in batch

4. **Conversations** (1 test)
   - Multi-turn conversations

5. **Tool Control** (2 tests)
   - Allowed tools
   - Disallowed tools

6. **Error Handling** (2 tests)
   - File not found
   - Invalid files in batch

7. **End-to-End** (2 tests)
   - Complete improvement workflow
   - Multi-file project analysis

8. **Performance** (1 test)
   - Large file handling

**Total**: 17 integration tests

## 🔑 Prerequisites

### Required API Keys

#### Gemini Tests
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

Get your key from: https://makersuite.google.com/app/apikey

#### Claude Tests (Optional)
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Note: Claude CLI tests use the installed CLI, not the API directly.

### Required CLI Tools

#### Gemini CLI
```bash
# Install via npm
npm install -g @google/generative-ai-cli

# Or via Homebrew (macOS)
brew install gemini-cli
```

#### Claude CLI
```bash
# Install via Homebrew (macOS)
brew install --cask claude-code

# Or download from
# https://code.claude.com/
```

## 🚀 Running Integration Tests

### Using Make (Recommended)

```bash
# Run all integration tests
make test-integration

# Run specific agent tests
cd tests
python3 -m pytest integration/test_gemini_agent_integration.py -v
python3 -m pytest integration/test_claude_cli_agent_integration.py -v
```

### Using pytest Directly

```bash
cd tests

# Run all integration tests
pytest integration/ -v -m integration

# Run only Gemini integration tests
pytest integration/test_gemini_agent_integration.py -v

# Run only Claude integration tests
pytest integration/test_claude_cli_agent_integration.py -v

# Run specific test class
pytest integration/test_gemini_agent_integration.py::TestGeminiAgentIntegrationBasic -v

# Run specific test
pytest integration/test_gemini_agent_integration.py::TestGeminiAgentIntegrationBasic::test_real_query -v
```

### With Environment Variables

```bash
# Set API keys
export GEMINI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"  # Optional

# Run tests
make test-integration
```

## 📊 Test Markers

Integration tests use pytest markers:

```python
@pytest.mark.integration  # Marks as integration test
@pytest.mark.slow         # Marks as slow test (API calls)
```

### Filter by Markers

```bash
# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Run integration but not slow
pytest -m "integration and not slow"

# Skip integration tests
pytest -m "not integration"
```

## 🎯 Test Structure

### Example Integration Test

```python
@pytest.mark.integration
@pytest.mark.slow
def test_real_code_review(self, agent, temp_python_file):
    """Test real code review"""
    result = agent.code_review(temp_python_file)
    
    assert result is not None
    response_text = str(result).lower()
    assert any(word in response_text for word in [
        "code", "function", "review", "quality"
    ])
```

### Fixtures

**Common Fixtures**:
- `api_key` - Gets API key from environment
- `agent` - Creates real agent instance
- `temp_python_file` - Creates temporary test file
- `temp_buggy_file` - Creates file with bugs
- `tmp_path` - pytest built-in temporary directory

## ⚠️ Important Notes

### API Costs
Integration tests make real API calls which may incur costs:
- **Gemini API**: Check pricing at https://ai.google.dev/pricing
- **Claude CLI**: Uses your Claude Code subscription

### Rate Limits
- Tests include delays to avoid rate limiting
- Some tests are marked as `slow`
- Run integration tests sparingly

### Test Data
- Tests use temporary files (auto-cleaned)
- No sensitive data in test files
- Tests are idempotent (can run multiple times)

## 🔧 Configuration

### pytest.ini

```ini
[pytest]
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow running (deselect with '-m "not slow"')
```

### Skip Tests Without API Keys

Tests automatically skip if API keys are not set:

```python
@pytest.fixture
def api_key():
    """Get API key from environment"""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key
```

## 📈 CI/CD Integration

### GitHub Actions

Integration tests can run in CI with secrets:

```yaml
- name: Run integration tests
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: make test-integration
```

### Manual Trigger

```bash
# In GitHub Actions UI
# Workflow: Test AI Agents
# Enable: "Run integration tests"
```

## 🐛 Troubleshooting

### Tests Skipped

**Issue**: All integration tests skipped

**Solutions**:
1. Check API key is set: `echo $GEMINI_API_KEY`
2. Export in current shell: `export GEMINI_API_KEY="your-key"`
3. Add to shell profile: `~/.zshrc` or `~/.bashrc`

### CLI Not Found

**Issue**: `gemini: command not found` or `claude: command not found`

**Solutions**:
1. Install CLI: `make install-gemini` or `make install-claude`
2. Check PATH: `which gemini` or `which claude`
3. Verify installation: `make verify`

### API Errors

**Issue**: API returns errors

**Solutions**:
1. Verify API key is valid
2. Check API quota/limits
3. Check network connectivity
4. Review API status page

### Test Failures

**Issue**: Integration tests fail

**Solutions**:
1. Check API key is correct
2. Verify CLI is installed
3. Check network connectivity
4. Review test output for specific errors
5. Run with verbose: `pytest -vv`

## 📝 Writing New Integration Tests

### Template

```python
@pytest.mark.integration
@pytest.mark.slow
def test_my_integration(self, agent, temp_file):
    """Test description"""
    # Arrange
    # ... setup test data
    
    # Act
    result = agent.some_method(temp_file)
    
    # Assert
    assert result is not None
    assert "expected" in str(result).lower()
```

### Best Practices

1. **Use Fixtures**: Leverage existing fixtures for setup
2. **Mark Appropriately**: Use `@pytest.mark.integration` and `@pytest.mark.slow`
3. **Handle Errors**: Expect and handle API errors gracefully
4. **Clean Up**: Use temporary files that auto-clean
5. **Be Specific**: Assert on specific expected outcomes
6. **Document**: Add clear docstrings
7. **Minimize Calls**: Combine assertions to reduce API calls

## 📚 Examples

### Run Specific Test Suite

```bash
# Gemini basic tests
pytest integration/test_gemini_agent_integration.py::TestGeminiAgentIntegrationBasic -v

# Claude file operations
pytest integration/test_claude_cli_agent_integration.py::TestClaudeAgentIntegrationFiles -v

# End-to-end tests
pytest integration/ -k "end_to_end" -v
```

### Run with Output

```bash
# Show print statements
pytest integration/ -v -s

# Show full diff
pytest integration/ -v --tb=long

# Stop on first failure
pytest integration/ -v -x
```

### Generate Report

```bash
# HTML report
pytest integration/ --html=report.html --self-contained-html

# JUnit XML
pytest integration/ --junitxml=report.xml

# Coverage report
pytest integration/ --cov=../src --cov-report=html
```

## 🎓 Summary

- **Unit Tests**: Fast, mocked, run always
- **Integration Tests**: Slow, real APIs, run selectively
- **Use Make**: `make test-unit` or `make test-integration`
- **Set API Keys**: Required for integration tests
- **Mark Tests**: Use `@pytest.mark.integration`
- **CI/CD**: Can run with secrets in GitHub Actions

---

**For more information**:
- Unit tests: See `tests/README.md`
- Test guide: See `tests/TESTING_GUIDE.md`
- Makefiles: See `Makefile.macos` or `Makefile.linux`
