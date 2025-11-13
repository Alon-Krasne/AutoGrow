# Token Optimization for Integration Tests

Guide for writing token-efficient integration tests that validate behavior without wasting API costs.

## 🎯 Principles

### 1. **Validate Behavior, Not Output**
Test what the agent *does*, not exact wording.

❌ **Bad** (brittle, specific):
```python
assert "The main security issue is division by zero" in result
```

✅ **Good** (flexible, behavior-focused):
```python
security_keywords = ["zero", "division", "error", "check"]
assert any(keyword in result.lower() for keyword in security_keywords)
```

### 2. **Combine Multiple Checks**
Use single queries that test multiple capabilities.

❌ **Bad** (3 API calls, 3x tokens):
```python
review = agent.code_review(file)
fix = agent.fix_code(file, "add error handling")
docs = agent.generate_docs(file)
```

✅ **Good** (1 API call, 1x tokens):
```python
result = agent.query_with_stdin(
    """Analyze this code:
    1. Main issue (one line)
    2. Suggested fix (one line)
    3. Function names (comma-separated)
    Be concise.""",
    code
)
```

### 3. **Use Concise Prompts**
Be specific and brief.

❌ **Bad** (verbose, wastes tokens):
```python
"Please analyze this file and tell me everything about it including what it does, what functions it has, what the purpose is, and any issues you can find"
```

✅ **Good** (concise, clear):
```python
"File purpose (5 words max)"
"Count functions (number only)"
"Main bug (one line)"
```

### 4. **Minimize Test Data**
Use smallest data that validates behavior.

❌ **Bad** (50 functions, large file):
```python
for i in range(50):
    content.append(f"def function_{i}(param): return param * {i}")
```

✅ **Good** (10 functions, sufficient):
```python
content = [f"def func_{i}(): return {i}" for i in range(10)]
```

### 5. **Reuse Context**
Use multi-turn conversations instead of repeated context.

❌ **Bad** (sends code 3 times):
```python
agent.query_with_stdin("Find bugs", code)
agent.query_with_stdin("Suggest fixes", code)
agent.query_with_stdin("List functions", code)
```

✅ **Good** (sends code once, reuses context):
```python
result1 = agent.query_with_stdin("Find bugs", code)
session_id = result1["session_id"]
result2 = agent.continue_conversation("Suggest fixes", session_id)
result3 = agent.continue_conversation("List functions", session_id)
```

## 📊 Token Cost Comparison

### Example: Code Review Test

#### Inefficient Approach
```python
def test_code_review_inefficient(agent, buggy_file):
    # Call 1: Full code review (1000+ tokens)
    review = agent.code_review(buggy_file)
    assert "error" in review["result"]
    
    # Call 2: Fix code (1500+ tokens)
    fix = agent.fix_code(buggy_file, "Add error handling for all functions")
    assert "try" in fix["result"]
    
    # Call 3: Generate docs (1000+ tokens)
    docs = agent.generate_docs(buggy_file)
    assert "function" in docs["result"]
    
    # Total: ~3500+ tokens, 3 API calls, ~$0.10
```

#### Efficient Approach
```python
def test_code_review_efficient(agent, buggy_file):
    # Single combined query (500 tokens)
    result = agent.query_with_stdin(
        """Analyze:
        1. Main bug (one line)
        2. Fix suggestion (one line)
        3. Function names
        Be concise.""",
        open(buggy_file).read()
    )
    
    # Validate all behaviors in one response
    text = result["result"].lower()
    assert any(k in text for k in ["error", "bug", "issue"])
    assert any(k in text for k in ["try", "check", "validate"])
    assert any(k in text for k in ["unsafe_divide", "get_first"])
    
    # Total: ~500 tokens, 1 API call, ~$0.01
```

**Savings**: 85% fewer tokens, 66% fewer API calls, 90% lower cost

## 🎯 Optimization Strategies

### Strategy 1: Structured Prompts

Use numbered lists for multiple requirements:

```python
prompt = """Analyze this code and provide:
1. Security issue (one line)
2. Suggested fix (one line)  
3. Function names (comma-separated)

Be concise."""
```

**Benefits**:
- Clear expectations
- Concise responses
- Easy to parse
- Saves tokens

### Strategy 2: Word Limits

Explicitly limit response length:

```python
"File purpose (5 words max)"
"Main bug (one sentence)"
"Count functions (number only)"
```

**Benefits**:
- Shorter responses
- Faster processing
- Lower costs
- Still validates behavior

### Strategy 3: Batch with Concise Prompts

For batch operations, use minimal prompts:

```python
# Instead of:
"Please analyze this file and describe its purpose, functionality, and any issues"

# Use:
"File purpose (5 words)"
```

**Benefits**:
- Multiplied savings (N files × token reduction)
- Faster batch processing
- Same validation capability

### Strategy 4: Keyword Validation

Test for presence of keywords, not exact matches:

```python
# Flexible validation
security_keywords = ["zero", "division", "error", "exception", "check"]
has_security = any(k in response.lower() for k in security_keywords)

# Works for various phrasings:
# - "division by zero error"
# - "zero division check needed"
# - "exception for zero values"
```

**Benefits**:
- Robust to response variations
- Tests actual understanding
- No need for exact wording

### Strategy 5: Multi-Turn Efficiency

Reuse conversation context:

```python
# First query with full context
result1 = agent.query_with_stdin("Analyze this code", code)

# Follow-ups without resending code
if "session_id" in result1:
    result2 = agent.continue_conversation(
        "Which function is most critical?",
        result1["session_id"]
    )
```

**Benefits**:
- Code sent once
- Context maintained
- Cheaper follow-ups
- Tests conversation capability

## 📝 Test Writing Checklist

Before writing an integration test, ask:

- [ ] Can I combine multiple checks into one query?
- [ ] Is my prompt as concise as possible?
- [ ] Am I using the smallest test data needed?
- [ ] Can I reuse conversation context?
- [ ] Am I validating behavior, not exact output?
- [ ] Do I have a timeout set?
- [ ] Are my assertions informative?

## 🎯 Real Examples from Our Tests

### Example 1: Complete Workflow Test

**Before** (inefficient):
```python
def test_workflow(agent, buggy_file):
    review = agent.code_review(buggy_file)  # 1000 tokens
    fix = agent.fix_code(buggy_file, "...")  # 1500 tokens
    docs = agent.generate_docs(buggy_file)  # 1000 tokens
    # Total: 3500 tokens
```

**After** (efficient):
```python
@pytest.mark.timeout(120)
def test_workflow(agent, buggy_file):
    result = agent.query_with_stdin(
        """Analyze:
        1. Main issue (one line)
        2. Fix (one line)
        3. Functions (comma-separated)
        Be concise.""",
        open(buggy_file).read()
    )
    # Validate all behaviors from one response
    # Total: 500 tokens (85% savings)
```

### Example 2: Batch Processing Test

**Before** (inefficient):
```python
def test_batch(agent, tmp_path):
    # Large files
    (tmp_path / "f1.py").write_text(large_content_1)
    (tmp_path / "f2.py").write_text(large_content_2)
    (tmp_path / "f3.py").write_text(large_content_3)
    
    # Verbose prompt
    results = agent.batch_process(
        str(tmp_path),
        "Please analyze this file thoroughly and describe everything",
        "*.py"
    )
    # Total: 3000+ tokens
```

**After** (efficient):
```python
@pytest.mark.timeout(90)
def test_batch(agent, tmp_path):
    # Minimal files
    (tmp_path / "f1.py").write_text("def a(): return 1")
    (tmp_path / "f2.py").write_text("def b(): return 2")
    (tmp_path / "f3.py").write_text("def c(): return 3")
    
    # Concise prompt
    results = agent.batch_process(
        str(tmp_path),
        "File purpose (5 words max)",
        "*.py"
    )
    # Total: 300 tokens (90% savings)
```

### Example 3: Large File Test

**Before** (inefficient):
```python
def test_large_file(agent, tmp_path):
    # 50 functions
    content = [f"def func_{i}(param): return param * {i}" 
               for i in range(50)]
    
    result = agent.query_with_stdin(
        "How many functions are in this file?",
        "\n".join(content)
    )
    # Total: 2000+ tokens
```

**After** (efficient):
```python
@pytest.mark.timeout(60)
def test_large_file(agent, tmp_path):
    # 10 functions (sufficient for testing)
    content = [f"def func_{i}(): return {i}" 
               for i in range(10)]
    
    result = agent.query_with_stdin(
        "Count functions (number only)",
        "\n".join(content)
    )
    # Total: 400 tokens (80% savings)
```

## 💰 Cost Estimation

### Token Costs (Approximate)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude Sonnet | $3.00 | $15.00 |
| Claude Haiku | $0.25 | $1.25 |
| Gemini Pro | $0.50 | $1.50 |

### Test Suite Costs

**Inefficient approach** (32 integration tests):
- Average tokens per test: 2000
- Total tokens: 64,000
- Estimated cost: ~$0.50 per run

**Optimized approach** (32 integration tests):
- Average tokens per test: 400
- Total tokens: 12,800
- Estimated cost: ~$0.10 per run

**Savings**: 80% reduction, $0.40 saved per run

**Annual savings** (100 runs): $40

## 🎓 Best Practices Summary

1. **Combine checks** - One query, multiple validations
2. **Be concise** - Short prompts, word limits
3. **Minimize data** - Smallest test files needed
4. **Reuse context** - Multi-turn conversations
5. **Validate behavior** - Keywords, not exact text
6. **Set timeouts** - Prevent hanging tests
7. **Document intent** - Clear test docstrings

## 📚 Additional Resources

- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [Google AI Pricing](https://ai.google.dev/pricing)
- [Token Counting Tools](https://platform.openai.com/tokenizer)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

---

**Remember**: Integration tests should validate behavior efficiently. Every token counts! 💰
