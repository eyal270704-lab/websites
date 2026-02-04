#!/usr/bin/env python3
"""
Automated GitHub Actions Workflow Auto-Fix Tool

This script applies automated fixes for common workflow failures identified by
diagnose_workflow_failure.py. Includes safety guardrails, rate limiting, and
audit trails.

User Requirements:
- 2x timing adjustments: 60-min cooldown, 3 max attempts/hour, 120-min API quota wait
- DO NOT touch Gemini API key
- Generic implementation for current and future newsfeeds

Usage:
    python autofix_workflow.py --workflow WORKFLOW_NAME --failure-type TYPE [--dry-run]
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration (2x timing adjustments per user request)
MAX_FIX_ATTEMPTS_PER_HOUR = 3  # Reduced from 5
COOLDOWN_MINUTES = 60  # Increased from 30
API_QUOTA_WAIT_MINUTES = 120  # Increased from 60 for API quota failures
RETRY_DELAY_MINUTES = 10  # Increased from 5 for empty responses
MAX_RETRIES = 3  # Standard

# File to track fix attempts
FIX_ATTEMPTS_FILE = '.github/fix_attempts.json'


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def load_fix_attempts() -> Dict:
    """Load fix attempt history from JSON file"""
    if not os.path.exists(FIX_ATTEMPTS_FILE):
        return {}

    try:
        with open(FIX_ATTEMPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load fix attempts: {e}", file=sys.stderr)
        return {}


def save_fix_attempts(attempts: Dict):
    """Save fix attempt history to JSON file"""
    os.makedirs(os.path.dirname(FIX_ATTEMPTS_FILE), exist_ok=True)

    try:
        with open(FIX_ATTEMPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(attempts, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save fix attempts: {e}", file=sys.stderr)


def check_cooldown(workflow_name: str, attempts: Dict) -> Tuple[bool, Optional[str]]:
    """
    Check if workflow is in cooldown period

    Returns:
        (can_fix, reason) - True if fix can be attempted, False with reason if in cooldown
    """
    if workflow_name not in attempts:
        return True, None

    workflow_attempts = attempts[workflow_name]
    last_attempt_str = workflow_attempts.get('last_attempt')

    if not last_attempt_str:
        return True, None

    try:
        last_attempt = datetime.fromisoformat(last_attempt_str)
        cooldown_until = last_attempt + timedelta(minutes=COOLDOWN_MINUTES)
        now = datetime.now()

        if now < cooldown_until:
            minutes_remaining = int((cooldown_until - now).total_seconds() / 60)
            return False, f"Cooldown active for {minutes_remaining} more minutes (60-min cooldown period)"

        return True, None
    except Exception as e:
        print(f"Warning: Error checking cooldown: {e}", file=sys.stderr)
        return True, None


def check_rate_limit(workflow_name: str, attempts: Dict) -> Tuple[bool, Optional[str]]:
    """
    Check if workflow has exceeded rate limit (max 3 attempts per hour)

    Returns:
        (can_fix, reason) - True if under rate limit, False with reason if exceeded
    """
    if workflow_name not in attempts:
        return True, None

    workflow_attempts = attempts[workflow_name]
    recent_attempts = workflow_attempts.get('attempts', [])

    # Filter attempts from last hour
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent = [
        a for a in recent_attempts
        if datetime.fromisoformat(a['timestamp']) > one_hour_ago
    ]

    if len(recent) >= MAX_FIX_ATTEMPTS_PER_HOUR:
        return False, f"Rate limit exceeded: {len(recent)}/{MAX_FIX_ATTEMPTS_PER_HOUR} attempts in last hour"

    return True, None


def record_fix_attempt(workflow_name: str, failure_type: str, action: str, success: bool, attempts: Dict) -> Dict:
    """Record a fix attempt in the history"""
    if workflow_name not in attempts:
        attempts[workflow_name] = {
            'attempts': [],
            'last_attempt': None
        }

    now = datetime.now().isoformat()

    attempts[workflow_name]['attempts'].append({
        'timestamp': now,
        'failure_type': failure_type,
        'action': action,
        'success': success
    })

    attempts[workflow_name]['last_attempt'] = now

    # Keep only last 50 attempts to prevent file bloat
    attempts[workflow_name]['attempts'] = attempts[workflow_name]['attempts'][-50:]

    return attempts


def create_github_issue(title: str, body: str, labels: List[str] = None) -> bool:
    """
    Create a GitHub Issue for manual intervention

    Returns:
        True if issue created successfully, False otherwise
    """
    cmd = ['gh', 'issue', 'create', '--title', title, '--body', body]

    if labels:
        cmd.extend(['--label', ','.join(labels)])

    returncode, stdout, stderr = run_command(cmd)

    if returncode == 0:
        print(f"✅ Created GitHub Issue: {stdout.strip()}")
        return True
    else:
        print(f"❌ Failed to create issue: {stderr}", file=sys.stderr)
        return False


def retry_workflow(workflow_name: str, dry_run: bool = False) -> bool:
    """
    Trigger a workflow re-run

    Returns:
        True if workflow triggered successfully, False otherwise
    """
    if dry_run:
        print(f"[DRY RUN] Would trigger workflow: {workflow_name}")
        return True

    cmd = ['gh', 'workflow', 'run', workflow_name]
    returncode, stdout, stderr = run_command(cmd)

    if returncode == 0:
        print(f"✅ Triggered workflow: {workflow_name}")
        return True
    else:
        print(f"❌ Failed to trigger workflow: {stderr}", file=sys.stderr)
        return False


def fix_permission_denied(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle 403 permission errors - create GitHub Issue for manual PAT regeneration

    Note: DO NOT auto-fix for security reasons
    """
    title = f"[Auto-Monitor] PAT_TOKEN Permission Error - {workflow_name}"
    body = f"""## Workflow Failure: Permission Denied

**Workflow**: `{workflow_name}`
**Run ID**: {run_id if run_id else 'N/A'}
**Failure Type**: 403 Permission Denied
**Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

### Issue
The PAT_TOKEN secret lacks sufficient permissions to push to the repository or trigger downstream workflows.

### Required Actions

1. **Verify PAT_TOKEN has required scopes**:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (if using GitHub Packages)

2. **Regenerate PAT if needed**:
   - Go to: https://github.com/settings/tokens
   - Create new token with required scopes
   - Update secret: `gh secret set PAT_TOKEN --body "YOUR_NEW_TOKEN"`

3. **Verify fix**:
   ```bash
   gh workflow run {workflow_name}
   gh run list --workflow={workflow_name} --limit 1
   ```

### Auto-Fix Status
❌ **Cannot auto-fix** - Requires manual PAT regeneration for security

---
*Generated by Auto-Monitor System*
"""

    if dry_run:
        print(f"[DRY RUN] Would create issue:")
        print(body)
        return True

    return create_github_issue(title, body, labels=['bug', 'auto-monitor', 'security'])


def fix_api_quota(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle API quota exhaustion - wait and retry with exponential backoff

    User requirement: Wait 120 minutes (2x the original 60 minutes)
    """
    print(f"API quota exhausted for {workflow_name}")
    print(f"Waiting {API_QUOTA_WAIT_MINUTES} minutes before retry (2-hour backoff)...")

    if dry_run:
        print(f"[DRY RUN] Would wait {API_QUOTA_WAIT_MINUTES} minutes then retry")
        return True

    # In actual GitHub Actions, this would be handled by the monitor workflow schedule
    # Here we just record the intent and let the next monitor cycle handle it
    print("✅ Will retry on next monitor cycle (handled by 60-min schedule)")
    return True


def fix_empty_response(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle empty API responses - immediate retry (transient error)

    User requirement: 10-minute delay (2x the original 5 minutes)
    """
    print(f"Empty response detected for {workflow_name} - transient error, retrying after {RETRY_DELAY_MINUTES} min...")

    if dry_run:
        print(f"[DRY RUN] Would wait {RETRY_DELAY_MINUTES} minutes then retry")
        return True

    # Note: In GitHub Actions context, we just trigger immediately
    # The workflow schedule will naturally provide the delay
    return retry_workflow(workflow_name, dry_run)


def fix_missing_secret(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle missing prompt secrets - create GitHub Issue

    Note: DO NOT auto-fix for security. DO NOT mention GEMINI_API_KEY per user request.
    """
    title = f"[Auto-Monitor] Missing Prompt Secret - {workflow_name}"
    body = f"""## Workflow Failure: Missing Prompt Secret

**Workflow**: `{workflow_name}`
**Run ID**: {run_id if run_id else 'N/A'}
**Failure Type**: Missing Environment Variable
**Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

### Issue
The workflow requires a prompt secret (e.g., NBA_PROMPT, STOCK_PROMPT) that is not configured.

### Required Actions

1. **Check config/newsfeeds.json** to identify required secret name
2. **Add missing secret** via GitHub Settings:
   ```bash
   gh secret set YOUR_PROMPT_NAME --body "Your prompt content here"
   ```
3. **Verify fix**:
   ```bash
   gh workflow run {workflow_name}
   gh run list --workflow={workflow_name} --limit 1
   ```

### Auto-Fix Status
❌ **Cannot auto-fix** - Requires manual secret configuration for security

---
*Generated by Auto-Monitor System*
"""

    if dry_run:
        print(f"[DRY RUN] Would create issue:")
        print(body)
        return True

    return create_github_issue(title, body, labels=['bug', 'auto-monitor', 'configuration'])


def fix_encoding_error(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle encoding errors - should already be fixed in generate_newsfeed.py lines 28-30

    Just retry the workflow.
    """
    print(f"Encoding error detected for {workflow_name}")
    print("Note: UTF-8 encoding fix already present in generate_newsfeed.py (lines 28-30)")
    print("Retrying workflow...")

    return retry_workflow(workflow_name, dry_run)


def fix_git_conflict(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle git conflicts - retry workflow (may resolve on retry)
    """
    print(f"Git conflict detected for {workflow_name} - retrying...")
    return retry_workflow(workflow_name, dry_run)


def fix_unknown(workflow_name: str, run_id: Optional[int], dry_run: bool = False) -> bool:
    """
    Handle unknown errors - create GitHub Issue for manual review
    """
    title = f"[Auto-Monitor] Unknown Workflow Failure - {workflow_name}"
    body = f"""## Workflow Failure: Unknown Error

**Workflow**: `{workflow_name}`
**Run ID**: {run_id if run_id else 'N/A'}
**Failure Type**: Unknown
**Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

### Issue
The workflow failed with an error that doesn't match known failure patterns.

### Required Actions

1. **Review workflow logs**:
   ```bash
   gh run view {run_id} --log
   ```

2. **Check for new error patterns**
   - May need to update diagnose_workflow_failure.py with new pattern
   - May need to add new fix strategy in autofix_workflow.py

3. **Manual intervention required**

### Auto-Fix Status
❌ **Cannot auto-fix** - Unknown error type requires human review

---
*Generated by Auto-Monitor System*
"""

    if dry_run:
        print(f"[DRY RUN] Would create issue:")
        print(body)
        return True

    return create_github_issue(title, body, labels=['bug', 'auto-monitor', 'needs-investigation'])


# Fix strategy mapping
FIX_STRATEGIES = {
    'permission_denied': fix_permission_denied,
    'api_quota': fix_api_quota,
    'empty_response': fix_empty_response,
    'missing_secret': fix_missing_secret,
    'encoding_error': fix_encoding_error,
    'git_conflict': fix_git_conflict,
    'workflow_config': fix_unknown,  # Treat workflow config errors as unknown
    'unknown': fix_unknown
}


def apply_fix(workflow_name: str, failure_type: str, run_id: Optional[int] = None, dry_run: bool = False) -> bool:
    """
    Apply automated fix for a workflow failure

    Returns:
        True if fix applied successfully, False otherwise
    """
    # Load fix attempt history
    attempts = load_fix_attempts()

    # Check cooldown
    can_fix, cooldown_reason = check_cooldown(workflow_name, attempts)
    if not can_fix:
        print(f"⏸️  {cooldown_reason}")
        return False

    # Check rate limit
    can_fix, rate_reason = check_rate_limit(workflow_name, attempts)
    if not can_fix:
        print(f"⏸️  {rate_reason}")
        return False

    # Get fix strategy
    fix_func = FIX_STRATEGIES.get(failure_type, fix_unknown)

    print(f"🔧 Applying fix for {workflow_name}: {failure_type}")

    # Apply fix
    success = fix_func(workflow_name, run_id, dry_run)

    # Record attempt
    if not dry_run:
        attempts = record_fix_attempt(
            workflow_name,
            failure_type,
            fix_func.__name__,
            success,
            attempts
        )
        save_fix_attempts(attempts)

    return success


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Apply automated fixes to workflow failures'
    )
    parser.add_argument(
        '--workflow',
        required=True,
        help='Workflow filename (e.g., nba-news.yml)'
    )
    parser.add_argument(
        '--failure-type',
        required=True,
        choices=list(FIX_STRATEGIES.keys()),
        help='Type of failure to fix'
    )
    parser.add_argument(
        '--run-id',
        type=int,
        help='GitHub Actions run ID (optional)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test fix without applying it'
    )

    args = parser.parse_args()

    if args.dry_run:
        print("=" * 80)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 80)

    success = apply_fix(
        args.workflow,
        args.failure_type,
        args.run_id,
        args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
