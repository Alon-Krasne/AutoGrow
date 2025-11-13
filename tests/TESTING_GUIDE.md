# Testing Guide

Complete guide for running and writing tests for the AI Project Template.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r tests/requirements.txt
```

### 2. Run Tests
```bash
cd tests
./run_tests.sh
```

That's it! The tests will run and show you the results.

## 📊 Test Results

After running tests, you'll see output like:
```
🧪 Running Tests
==================================================

Running: pytest -m 'not integration'

======================== test session starts =========================
collected 31 items

tests/unit/test_gemini_agent.py::TestGeminiAgentInitialization::test_init_with_api_key PASSED
tests/unit/test_gemini_agent.py::TestGeminiAgentInitialization::test_init_with_env_var PASSED
...

======================== 31 passed in 2.34s ==========================

✅ All tests passed!
```

## 🎯 Test Commands

### Basic Commands
```bash
# Run all unit tests
./run_tests.sh

# Run with verbose output
./run_tests.sh --verbose

# Run specific test file
./run_tests.sh unit/test_gemini_agent.py

# Run specific test class
pytest unit/test_gemini_agent.py::TestGeminiAgentQuery

# Run specific test method
pytest unit/test_gemini_agent.py::TestGeminiAgentQuery::test_query_basic
```

### Coverage
```bash
# Run with coverage report
./run_tests.sh --coverage

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Integration Tests
```bash
# Run including integration tests (requires API key)
export GEMINI_API_KEY="your-key"
./run_tests.sh --integration
```

## 📝 Current Tests

### GeminiAgent Tests (31 tests)

**Location**: `tests/unit/test_gemini_agent.py`

#### Test Classes

1. **TestGeminiAgentInitialization** (7 tests)
   - Validates proper initialization
   - Tests API key handling
   - Checks configuration options

2. **TestGeminiAgentInstallationCheck** (3 tests)
   - Verifies gemini-cli detection
   - Tests error handling

3. **TestGeminiAgentQuery** (10 tests)
   - Tests basic query functionality
   - Validates command construction
   - Tests error scenarios

4. **TestGeminiAgentQueryWithFile** (3 tests)
   - Tests file input handling
   - Validates file reading

5. **TestGeminiAgentCodeReview** (1 test)
   - Tests code review functionality

6. **TestGeminiAgentGenerateDocs** (1 test)
   - Tests documentation generation

7. **TestGeminiAgentAnalyzeLogs** (2 tests)
   - Tests log analysis

8. **TestGeminiAgentBatchProcess** (3 tests)
   - Tests batch file processing

9. **TestGeminiAgentIntegration** (1 test)
   - Real API integration test

## ✍️ Writing New Tests

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestYourFeature:
    """Test description"""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        return {"key": "value"}
    
    def test_basic_functionality(self, setup_data):
        """Test basic case"""
        result = your_function(setup_data)
        assert result == expected
    
    def test_error_handling(self):
        """Test error case"""
        with pytest.raises(ValueError):
            your_function(invalid_input)
```

### Best Practices

1. **Use descriptive names**
   ```python
   # Good
   def test_query_with_invalid_api_key_raises_error(self):
   
   # Bad
   def test_query_error(self):
   ```

2. **One assertion per test** (when possible)
   ```python
   # Good
   def test_returns_correct_response(self):
       assert result["response"] == expected
   
   def test_includes_stats(self):
       assert "stats" in result
   
   # Acceptable for related assertions
   def test_response_structure(self):
       assert "response" in result
       assert "stats" in result
   ```

3. **Use fixtures for setup**
   ```python
   @pytest.fixture
   def agent(self):
       with patch.object(GeminiAgent, '_is_gemini_installed', return_value=True):
           return GeminiAgent(api_key="test-key")
   
   def test_something(self, agent):
       result = agent.query("test")
       assert result is not None
   ```

4. **Mock external dependencies**
   ```python
   @patch('subprocess.run')
   def test_query(self, mock_run, agent):
       mock_run.return_value = Mock(stdout='{"response": "test"}')
       result = agent.query("test")
       assert result["response"] == "test"
   ```

5. **Test edge cases**
   ```python
   def test_empty_input(self):
       """Test with empty input"""
   
   def test_none_input(self):
       """Test with None input"""
   
   def test_large_input(self):
       """Test with large input"""
   ```

## 🏷️ Test Markers

Use markers to categorize tests:

```python
@pytest.mark.integration
def test_real_api_call(self):
    """Test with real API"""

@pytest.mark.slow
def test_long_running_process(self):
    """Test that takes a while"""

@pytest.mark.requires_api_key
def test_with_api(self):
    """Test requiring API key"""
```

Run specific markers:
```bash
# Run only integration tests
pytest -m integration

# Skip integration tests
pytest -m "not integration"

# Run multiple markers
pytest -m "integration or slow"
```

## 🔧 Fixtures

### Built-in Fixtures (conftest.py)

```python
def test_with_project_root(project_root):
    """Use project root path"""
    assert (project_root / "README.md").exists()

def test_with_mock_env(mock_env_vars):
    """Mock environment variables"""
    mock_env_vars(GEMINI_API_KEY="test-key")
    # Test code here

def test_with_clean_env(clean_env):
    """Start with clean environment"""
    # No API keys in environment
```

### Custom Fixtures

```python
@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return str(file_path)

def test_with_temp_file(temp_file):
    """Use temporary file"""
    with open(temp_file) as f:
        content = f.read()
    assert content == "test content"
```

## 🐛 Debugging Tests

### Run with verbose output
```bash
pytest -vv
```

### Show print statements
```bash
pytest -s
```

### Stop on first failure
```bash
pytest -x
```

### Run last failed tests
```bash
pytest --lf
```

### Drop into debugger on failure
```bash
pytest --pdb
```

### Show local variables on failure
```bash
pytest -l
```

## 📈 Coverage Goals

- **Unit Tests**: Aim for 80%+ coverage
- **Critical Paths**: 100% coverage
- **Error Handling**: All error paths tested

Check coverage:
```bash
./run_tests.sh --coverage
open htmlcov/index.html
```

## 🔄 CI/CD Integration

Tests run automatically in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r tests/requirements.txt
    cd tests
    ./run_tests.sh --coverage
```

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)

## 💡 Tips

1. **Run tests frequently** - Catch issues early
2. **Write tests first** - TDD approach
3. **Keep tests fast** - Mock external calls
4. **Test behavior, not implementation** - Focus on what, not how
5. **Use descriptive assertions** - Make failures clear

## 🆘 Troubleshooting

### Tests not found
```bash
# Make sure you're in the tests directory
cd tests
./run_tests.sh
```

### Import errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

### Mock not working
```python
# Make sure to patch the right location
# Patch where it's used, not where it's defined
@patch('gemini_agent.subprocess.run')  # Correct
@patch('subprocess.run')  # May not work
```

### Fixture not found
```python
# Make sure conftest.py is in the right location
# tests/conftest.py for all tests
# tests/unit/conftest.py for unit tests only
```

---

**Happy Testing! 🧪**
