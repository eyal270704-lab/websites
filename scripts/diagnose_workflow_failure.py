#!/usr/bin/env python3
"""
Automated GitHub Actions Workflow Failure Diagnostic Tool

This script automatically discovers and diagnoses failures in GitHub Actions workflows
that use generate_newsfeed.py. It's designed to be generic and work with current and
future newsfeed topics without code modifications.

Usage:
    python diagnose_workflow_failure.py [--workflow WORKFLOW_NAME] [--limit N]
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Failure detection patterns (DO NOT check for Gemini API key issues per user request)
FAILURE_PATTERNS = {
    'permission_denied': {
        'pattern': r'Permission to .* denied|fatal: unable to access.*403|The requested URL returned error: 403',
        'severity': 'high',
        'fixable': False,  # Requires manual PAT regeneration
        'description': 'Git push failed due to insufficient PAT_TOKEN permissions'
    },
    'api_quota': {
        'pattern': r'quota.*exceeded|rate limit|429|Resource has been exhausted',
        'severity': 'medium',
        'fixable': True,  # Can retry with backoff
        'description': 'Gemini API quota exhausted or rate limited'
    },
    'empty_response': {
        'pattern': r'empty response|no content returned|response is None|Response: None',
        'severity': 'low',
        'fixable': True,  # Transient error, can retry
        'description': 'Gemini API returned empty response (transient error)'
    },
    'missing_secret': {
        'pattern': r'(NBA_PROMPT|STOCK_PROMPT|.*_PROMPT).*not set|environment variable.*(NBA_PROMPT|STOCK_PROMPT|.*_PROMPT).*not found',
        'severity': 'high',
        'fixable': False,  # Requires manual secret configuration
        'description': 'Required prompt secret environment variable not set'
    },
    'encoding_error': {
        'pattern': r'UnicodeDecodeError|codec.*decode|\'utf-8\' codec can\'t decode',
        'severity': 'low',
        'fixable': True,  # Already fixed in generate_newsfeed.py lines 28-30
        'description': 'UTF-8 encoding error (should be fixed in latest code)'
    },
    'workflow_config': {
        'pattern': r'Invalid workflow file|syntax error in workflow|yaml.*parse error',
        'severity': 'high',
        'fixable': False,  # Requires manual workflow file fix
        'description': 'Workflow YAML configuration syntax error'
    },
    'git_conflict': {
        'pattern': r'CONFLICT.*merge|failed to push.*rejected|Updates were rejected',
        'severity': 'medium',
        'fixable': True,  # Can retry with pull/rebase
        'description': 'Git merge conflict or rejected push'
    }
}


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


def discover_newsfeed_workflows() -> List[str]:
    """
    Auto-discover all GitHub Actions workflows that generate content for the site.

    This includes:
    - Newsfeed workflows (using generate_newsfeed.py)
    - Trade watcher workflows (using generate_trades.py)

    Returns:
        List of workflow file basenames (e.g., ['nba-news.yml', 'trade-watcher.yml'])
    """
    workflows_dir = '.github/workflows'
    content_workflows = []

    # Scripts that generate site content
    content_scripts = ['generate_newsfeed.py', 'generate_trades.py']

    if not os.path.exists(workflows_dir):
        print(f"Warning: {workflows_dir} not found", file=sys.stderr)
        return []

    for filename in os.listdir(workflows_dir):
        if filename.endswith(('.yml', '.yaml')):
            filepath = os.path.join(workflows_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check if workflow uses any content generation script
                    if any(script in content for script in content_scripts):
                        content_workflows.append(filename)
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return sorted(content_workflows)


def get_recent_failures(workflow_name: str, limit: int = 5) -> List[Dict]:
    """
    Fetch recent workflow runs and identify failures

    Args:
        workflow_name: Workflow filename (e.g., 'nba-news.yml')
        limit: Maximum number of runs to check

    Returns:
        List of failed run dictionaries with keys: run_id, conclusion, created_at, html_url
    """
    cmd = [
        'gh', 'run', 'list',
        '--workflow', workflow_name,
        '--limit', str(limit),
        '--json', 'databaseId,conclusion,createdAt,headBranch,event,displayTitle,url'
    ]

    returncode, stdout, stderr = run_command(cmd)

    if returncode != 0:
        print(f"Error fetching runs for {workflow_name}: {stderr}", file=sys.stderr)
        return []

    try:
        runs = json.loads(stdout)
        # Filter for failed/cancelled runs
        failures = [
            run for run in runs
            if run.get('conclusion') in ['failure', 'cancelled', 'timed_out']
        ]
        return failures
    except json.JSONDecodeError as e:
        print(f"Error parsing run list: {e}", file=sys.stderr)
        return []


def download_run_logs(run_id: int) -> Optional[str]:
    """
    Download logs for a specific workflow run

    Args:
        run_id: GitHub Actions run ID

    Returns:
        Combined log content as string, or None if download failed
    """
    # Use gh run view with --log flag to get logs
    cmd = ['gh', 'run', 'view', str(run_id), '--log']

    returncode, stdout, stderr = run_command(cmd)

    if returncode != 0:
        print(f"Warning: Could not fetch logs for run {run_id}: {stderr}", file=sys.stderr)
        return None

    return stdout


def categorize_failure(log_content: str) -> Dict:
    """
    Analyze log content and categorize the failure type

    Args:
        log_content: Full workflow run logs

    Returns:
        Dictionary with keys: type, severity, fixable, description, matched_text
    """
    if not log_content:
        return {
            'type': 'unknown',
            'severity': 'medium',
            'fixable': False,
            'description': 'Could not retrieve logs to diagnose failure',
            'matched_text': None
        }

    # Check each pattern
    for failure_type, info in FAILURE_PATTERNS.items():
        pattern = info['pattern']
        match = re.search(pattern, log_content, re.IGNORECASE | re.MULTILINE)

        if match:
            return {
                'type': failure_type,
                'severity': info['severity'],
                'fixable': info['fixable'],
                'description': info['description'],
                'matched_text': match.group(0)
            }

    # If no pattern matched, it's an unknown error
    # Try to extract a relevant error message
    error_patterns = [
        r'Error: (.+)',
        r'FATAL: (.+)',
        r'failed with (.+)',
        r'Exception: (.+)'
    ]

    error_snippet = None
    for pattern in error_patterns:
        match = re.search(pattern, log_content, re.IGNORECASE | re.MULTILINE)
        if match:
            error_snippet = match.group(0)[:200]  # Limit to 200 chars
            break

    return {
        'type': 'unknown',
        'severity': 'high',
        'fixable': False,
        'description': 'Unknown failure - requires human review',
        'matched_text': error_snippet
    }


def diagnose_workflow(workflow_name: str, limit: int = 5, quiet: bool = False) -> Dict:
    """
    Comprehensive diagnosis of a workflow's recent failures

    Args:
        workflow_name: Workflow filename
        limit: Number of recent runs to analyze
        quiet: If True, suppress progress messages (for JSON output mode)

    Returns:
        Diagnostic report dictionary
    """
    if not quiet:
        print(f"Diagnosing workflow: {workflow_name}")

    failures = get_recent_failures(workflow_name, limit)

    if not failures:
        return {
            'workflow': workflow_name,
            'status': 'healthy',
            'recent_failures': 0,
            'failures': []
        }

    diagnosed_failures = []

    for run in failures:
        run_id = run['databaseId']
        if not quiet:
            print(f"  Analyzing run {run_id}...", end=' ')

        logs = download_run_logs(run_id)
        diagnosis = categorize_failure(logs)

        diagnosed_failures.append({
            'run_id': run_id,
            'created_at': run['createdAt'],
            'url': run['url'],
            'display_title': run.get('displayTitle', 'N/A'),
            'diagnosis': diagnosis
        })

        if not quiet:
            print(f"{diagnosis['type']} ({diagnosis['severity']})")

    # Calculate failure statistics
    fixable_count = sum(1 for f in diagnosed_failures if f['diagnosis']['fixable'])

    return {
        'workflow': workflow_name,
        'status': 'failing',
        'recent_failures': len(diagnosed_failures),
        'fixable_failures': fixable_count,
        'requires_human': len(diagnosed_failures) - fixable_count,
        'failures': diagnosed_failures
    }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Diagnose GitHub Actions workflow failures'
    )
    parser.add_argument(
        '--workflow',
        help='Specific workflow to diagnose (e.g., nba-news.yml). If not specified, diagnoses all newsfeed workflows.'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of recent runs to check (default: 5)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Discover or use specified workflow
    if args.workflow:
        workflows = [args.workflow]
    else:
        workflows = discover_newsfeed_workflows()

        if not workflows:
            print("No newsfeed workflows found!", file=sys.stderr)
            sys.exit(1)

        if not args.json:
            print(f"Auto-discovered {len(workflows)} newsfeed workflow(s): {', '.join(workflows)}\n")

    # Diagnose each workflow (quiet mode for JSON output)
    results = []
    for workflow in workflows:
        diagnosis = diagnose_workflow(workflow, args.limit, quiet=args.json)
        results.append(diagnosis)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "="*80)
        print("DIAGNOSTIC SUMMARY")
        print("="*80)

        for result in results:
            status_icon = "✅" if result['status'] == 'healthy' else "❌"
            print(f"\n{status_icon} {result['workflow']}: {result['status'].upper()}")

            if result['status'] == 'failing':
                print(f"  Recent failures: {result['recent_failures']}")
                print(f"  Auto-fixable: {result['fixable_failures']}")
                print(f"  Requires human: {result['requires_human']}")

                # Group by failure type
                failure_types = {}
                for failure in result['failures']:
                    ftype = failure['diagnosis']['type']
                    failure_types[ftype] = failure_types.get(ftype, 0) + 1

                print(f"  Failure breakdown:")
                for ftype, count in sorted(failure_types.items(), key=lambda x: x[1], reverse=True):
                    fixable = FAILURE_PATTERNS.get(ftype, {}).get('fixable', False)
                    fix_icon = "🔧" if fixable else "⚠️ "
                    print(f"    {fix_icon} {ftype}: {count}")

    # Exit with appropriate code
    any_failures = any(r['status'] == 'failing' for r in results)
    sys.exit(1 if any_failures else 0)


if __name__ == '__main__':
    main()
