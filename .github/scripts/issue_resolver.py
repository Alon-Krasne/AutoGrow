#!/usr/bin/env python3
"""
Issue Resolver Agent
Takes an open issue, analyzes it with Claude AI using Agent SDK, implements a fix, and creates a PR
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from github import Github, Auth
import git

# Add src directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'claude-agent'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Import Claude CLI Agent
try:
    from claude_cli_agent import ClaudeAgent
    USE_CLAUDE_CLI = True
except ImportError:
    print("⚠️  claude_cli_agent not available, falling back to anthropic SDK")
    from anthropic import Anthropic
    USE_CLAUDE_CLI = False

# Import validator
from utils.project_brief_validator import validate_project_brief

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
REPO_NAME = os.getenv('REPO_NAME')
SPECIFIC_ISSUE = os.getenv('SPECIFIC_ISSUE')
LABELS_TO_HANDLE = os.getenv('ISSUE_LABELS_TO_HANDLE', 'bug,enhancement').split(',')
LABELS_TO_SKIP = os.getenv('ISSUE_LABELS_TO_SKIP', 'wontfix,duplicate,in-progress').split(',')
MAX_TIME = int(os.getenv('MAX_EXECUTION_TIME', '8')) * 60

start_time = time.time()

print("🤖 Issue Resolver Agent Starting")
print(f"📋 Config:")
print(f"   - Labels to handle: {LABELS_TO_HANDLE}")
print(f"   - Labels to skip: {LABELS_TO_SKIP}")
print(f"   - Supports: features, bugs, documentation, refactoring, tests, performance, security, CI/CD")

# Initialize clients
auth = Auth.Token(GITHUB_TOKEN)
gh = Github(auth=auth)
repo = gh.get_repo(REPO_NAME)
print(f"✅ Connected to repository: {REPO_NAME}")

git_repo = git.Repo('.')


def should_skip_validation(issue_title, issue_body, issue_labels):
    """
    Determine if PROJECT_BRIEF.md validation should be skipped for this issue
    
    Args:
        issue_title: The issue title
        issue_body: The issue body/description
        issue_labels: List of issue label names
        
    Returns:
        bool: True if validation should be skipped
    """
    # Keywords that indicate the issue is about creating/fixing PROJECT_BRIEF.md itself
    skip_keywords = [
        'project_brief',
        'project brief',
        'template',
        'example',
        'documentation',
        'readme',
        'setup',
        'initial',
        'bootstrap'
    ]
    
    # Check if issue is about PROJECT_BRIEF.md or templates
    text_to_check = f"{issue_title} {issue_body}".lower()
    if any(keyword in text_to_check for keyword in skip_keywords):
        return True
    
    # Check labels
    skip_labels = ['documentation', 'setup', 'template']
    if any(label in skip_labels for label in issue_labels):
        return True
    
    return False


def validate_project_brief_if_exists(issue_title="", issue_body="", issue_labels=None):
    """
    Validate PROJECT_BRIEF.md if it exists in the repository
    
    Args:
        issue_title: The issue title (for skip detection)
        issue_body: The issue body (for skip detection)
        issue_labels: List of issue labels (for skip detection)

    Returns:
        Tuple of (is_valid, validation_message)
    """
    issue_labels = issue_labels or []
    
    # Check if we should skip validation for this issue
    if should_skip_validation(issue_title, issue_body, issue_labels):
        print("ℹ️  Skipping PROJECT_BRIEF.md validation (issue is about templates/documentation)")
        return True, None
    
    project_brief_path = Path('PROJECT_BRIEF.md')

    if not project_brief_path.exists():
        print("ℹ️  No PROJECT_BRIEF.md found (optional)")
        return True, None

    print("📋 Validating PROJECT_BRIEF.md...")
    result = validate_project_brief(project_brief_path)

    if result.is_valid:
        print("✅ PROJECT_BRIEF.md validation passed")
        validation_msg = "✅ PROJECT_BRIEF.md validated successfully"

        if result.warnings:
            print(f"⚠️  Validation warnings: {len(result.warnings)}")
            for warning in result.warnings[:3]:  # Show first 3 warnings
                print(f"   - {warning}")
            validation_msg += f"\n\n**Warnings ({len(result.warnings)}):**\n"
            for warning in result.warnings[:5]:
                validation_msg += f"- {warning}\n"

        return True, validation_msg
    else:
        print("❌ PROJECT_BRIEF.md validation failed")
        for error in result.errors[:5]:  # Show first 5 errors
            print(f"   - {error}")

        validation_msg = "❌ PROJECT_BRIEF.md validation failed\n\n**Errors:**\n"
        for error in result.errors[:5]:
            validation_msg += f"- {error}\n"

        if result.warnings:
            validation_msg += f"\n**Warnings:**\n"
            for warning in result.warnings[:3]:
                validation_msg += f"- {warning}\n"

        return False, validation_msg


def resolve_issue():
    """Use Claude CLI Agent to resolve an issue"""
    
    # Select issue
    selected_issue = None
    issue_claimed = False  # Track if we claimed the issue
    
    if SPECIFIC_ISSUE:
        print(f"🎯 Working on specific issue #{SPECIFIC_ISSUE}")
        selected_issue = repo.get_issue(int(SPECIFIC_ISSUE))
    else:
        print("🔍 Searching for issue to resolve...")
        open_issues = repo.get_issues(state='open', sort='created', direction='asc')
        
        for issue in open_issues:
            if issue.pull_request:
                continue
            
            issue_labels = [label.name for label in issue.labels]
            if any(skip_label in issue_labels for skip_label in LABELS_TO_SKIP):
                continue
            
            if LABELS_TO_HANDLE and not any(handle_label in issue_labels for handle_label in LABELS_TO_HANDLE):
                continue
            
            comments = list(issue.get_comments())
            if any('Issue Resolver Agent' in c.body and 'claimed' in c.body.lower() for c in comments):
                continue
            
            selected_issue = issue
            break
    
    if not selected_issue:
        print("ℹ️  No suitable issues found")
        return
    
    print(f"✅ Selected issue #{selected_issue.number}: {selected_issue.title}")
    
    # Claim the issue
    claim_message = f"""🤖 **Issue Resolver Agent**

I'm working on this issue now.

**Started at:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** In Progress

---
*Automated by GitHub Actions*"""
    
    selected_issue.create_comment(claim_message)
    selected_issue.add_to_labels('in-progress')
    issue_claimed = True  # Mark that we claimed it
    print("📝 Claimed issue")
    
    # Get issue details for validation check
    issue_body = selected_issue.body or "No description provided"
    issue_labels = [label.name for label in selected_issue.labels]

    # Validate PROJECT_BRIEF.md before proceeding (may skip for certain issues)
    is_valid, validation_msg = validate_project_brief_if_exists(
        issue_title=selected_issue.title,
        issue_body=issue_body,
        issue_labels=issue_labels
    )
    if not is_valid:
        print("❌ PROJECT_BRIEF.md validation failed - aborting to save API calls")
        selected_issue.create_comment(
            f"❌ **Pre-flight check failed**\n\n{validation_msg}\n\n"
            "Please fix PROJECT_BRIEF.md validation errors before I can proceed.\n\n"
            "---\n*Issue Resolver Agent*"
        )
        selected_issue.remove_from_labels('in-progress')
        return

    # Add validation success to issue comment if there was a validation
    if validation_msg:
        selected_issue.create_comment(validation_msg)

    # Get context
    try:
        readme = repo.get_readme().decoded_content.decode('utf-8')[:2000]
    except:
        readme = "No README found"
    
    # Build prompt for Claude
    prompt = f"""You are an expert software engineer. Fix this GitHub issue by modifying the necessary files.

Repository: {REPO_NAME}
Issue #{selected_issue.number}: {selected_issue.title}

Description:
{issue_body}

Labels: {', '.join(issue_labels)}

Context from README:
{readme}

Instructions:
1. Analyze the issue carefully
2. Use the Read tool to examine relevant files
3. Use the Write tool to create or modify files with your fixes
4. Make complete, working changes
5. After making changes, summarize what you did

You have access to Read and Write tools to modify files in the current directory."""

    print(f"📝 Prompt length: {len(prompt)} chars")
    
    # Create branch
    branch_name = f"fix/issue-{selected_issue.number}-{int(time.time())}"
    print(f"🌿 Creating branch: {branch_name}")
    try:
        git_repo.git.checkout('-b', branch_name)
        print(f"✅ Branch created: {branch_name}")
    except Exception as e:
        print(f"❌ Failed to create branch: {e}")
        if issue_claimed:
            selected_issue.create_comment(f"❌ Failed to create branch: {e}")
            selected_issue.remove_from_labels('in-progress')
        return
    
    # Initialize Claude CLI Agent with Read/Write tools
    print("🤖 Starting Claude CLI Agent with Read/Write tools...")
    
    files_modified = []
    summary = ""
    
    try:
        # Create Claude CLI Agent with permission to edit files
        # Use verbose mode for better logging
        agent = ClaudeAgent(
            output_format="text",
            verbose=True,  # Enable verbose logging
            allowed_tools=["Read", "Write", "Bash"],
            permission_mode="acceptEdits"
        )
        
        # Send the query to Claude with streaming output
        print("📤 Sending query to Claude (streaming output)...")
        print("-" * 60)
        result = agent.query(prompt, stream_output=True)
        print("-" * 60)
        
        # Extract the response
        if isinstance(result, dict) and "result" in result:
            summary = result["result"]
        else:
            summary = str(result)
        
        print(f"✅ Claude completed work")
        print(f"📊 Summary length: {len(summary)} chars")
        if len(summary) > 300:
            print(f"📝 Response preview: {summary[:300]}...")
        
    except Exception as e:
        print(f"❌ Claude Agent error: {e}")
        import traceback
        traceback.print_exc()
        if issue_claimed:
            selected_issue.create_comment(f"❌ Failed to generate fix: {e}")
            selected_issue.remove_from_labels('in-progress')
        return
    
    # Check if any files were modified
    if git_repo.is_dirty(untracked_files=True):
        # Get list of changed files
        changed_files = [item.a_path for item in git_repo.index.diff(None)]
        untracked_files = git_repo.untracked_files
        files_modified = changed_files + untracked_files
        
        print(f"📝 Files modified: {len(files_modified)}")
        for f in files_modified:
            print(f"  ✏️  {f}")
        
        # Commit changes
        git_repo.git.add('-A')
        commit_message = f"""Fix: Resolve issue #{selected_issue.number}

{selected_issue.title}

Closes #{selected_issue.number}

---
Generated by Issue Resolver Agent using Claude Agent SDK"""
        
        git_repo.index.commit(commit_message)
        print("✅ Committed changes")
        
        # Push
        origin = git_repo.remote('origin')
        origin.push(branch_name)
        print(f"✅ Pushed branch: {branch_name}")
        
        # Create PR
        pr_title = f"Fix: {selected_issue.title}"
        pr_body = f"""{summary[:500]}

## Changes
{chr(10).join(['- ' + f for f in files_modified[:20]])}

Closes #{selected_issue.number}

---
*Generated by Issue Resolver Agent using Claude Agent SDK*"""
        
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base='main'
        )
        
        print(f"✅ Created PR #{pr.number}")
        
        # Update issue
        selected_issue.create_comment(f"""✅ **Solution Ready**

Pull Request: #{pr.number}

**Changes:**
{chr(10).join(['- ' + f for f in files_modified[:10]])}

---
*Completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*""")
        
        selected_issue.remove_from_labels('in-progress')
        
        print("🎉 Complete!")
        
    else:
        print("⚠️  No files were modified")
        if issue_claimed:
            selected_issue.create_comment("⚠️ No changes were made. The issue may need manual review.")
            selected_issue.remove_from_labels('in-progress')


# Run the function with error handling
try:
    resolve_issue()
except Exception as e:
    print(f"❌ Fatal error in issue resolver: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
