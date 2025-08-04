#!/usr/bin/env python3
import json
import re
import sys
from utils.trace_decision import log_decision

def get_preferences():
    """Read preferences from .claude/preferences.json."""
    try:
        with open('.claude/preferences.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Define validation rules as a list of (regex pattern, message) tuples
VALIDATION_RULES = [
    # File deletion commands
    (
        r"(^|\s&\s)unlink\b",
        "unlink can delete files. Use 'git rm' for tracked files or request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)shred\b",
        "shred permanently destroys files. This operation is irreversible. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Git destructive operations
    (
        r"(^|\s&\s)git\s+reset\b",
        "git reset can cause data loss. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)git\s+branch\s+[-\w]*\s*-[dD]\b",
        "git branch -d/-D can delete branches. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)git\s+rebase\b",
        "git rebase rewrites history. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)git\s+push\s+[-\w]*\s*--force\b",
        "git push --force can overwrite remote history. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)git\s+push\s+[-\w]*\s*-f\b",
        "git push -f can overwrite remote history. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)git\s+clean\b",
        "git clean can delete untracked files. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)git\s+gc\s+[-\w]*\s*--prune\b",
        "git gc --prune can permanently delete unreferenced objects. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # System destructive commands
    (
        r"(^|\s&\s)dd\b",
        "dd can overwrite disk data. This is extremely destructive. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)format\b",
        "format command can destroy data. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)fdisk\b",
        "fdisk can modify disk partitions. This is destructive. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)parted\b",
        "parted can modify disk partitions. This is destructive. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)mkfs\b",
        "mkfs creates new filesystems and destroys existing data. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)chmod\b",
        "chmod changes permissions. This is a security risk. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Process management (potentially destructive)
    (
        r"(^|\s&\s)kill\s+[-\w]*\s*-9\b",
        "kill -9 forces process termination. Use regular kill first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)killall\b",
        "killall can terminate multiple processes. Review which processes will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)pkill\b",
        "pkill can terminate processes by name. Review which processes will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Network and service commands (potentially disruptive)
    (
        r"(^|\s&\s)service\s+[-\w]*\s*stop\b",
        "service stop can disrupt system services. Review which service will be stopped. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)systemctl\s+[-\w]*\s*stop\b",
        "systemctl stop can disrupt system services. Review which service will be stopped. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)systemctl\s+[-\w]*\s*disable\b",
        "systemctl disable can prevent services from starting. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Package management (potentially destructive)
    (
        r"(^|\s&\s)apt\s+[-\w]*\s*remove\b",
        "apt remove can uninstall packages. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)apt\s+[-\w]*\s*purge\b",
        "apt purge can completely remove packages and configs. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)yum\s+[-\w]*\s*remove\b",
        "yum remove can uninstall packages. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)brew\s+[-\w]*\s*uninstall\b",
        "brew uninstall can remove packages. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Database operations (potentially destructive)
    (
        r"(^|\s&\s)drop\s+database\b",
        "drop database can permanently delete databases. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+table\b",
        "drop table can permanently delete tables. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)truncate\s+table\b",
        "truncate table can permanently delete all data. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)delete\s+from\b",
        "delete from can remove rows from tables. Review what will be deleted first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+policy\b",
        "drop policy can remove security policies. Review which policy will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+role\b",
        "drop role can remove database roles. Review which role will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+user\b",
        "drop user can remove database users. Review which user will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+index\b",
        "drop index can remove database indexes. Review which index will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+view\b",
        "drop view can remove database views. Review which view will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+function\b",
        "drop function can remove database functions. Review which function will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+procedure\b",
        "drop procedure can remove database procedures. Review which procedure will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+trigger\b",
        "drop trigger can remove database triggers. Review which trigger will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+constraint\b",
        "drop constraint can remove database constraints. Review which constraint will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+sequence\b",
        "drop sequence can remove database sequences. Review which sequence will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+type\b",
        "drop type can remove database types. Review which type will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+schema\b",
        "drop schema can remove database schemas. Review which schema will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)drop\s+extension\b",
        "drop extension can remove database extensions. Review which extension will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)exec\b",
        "exec can execute files or commands. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)execute\b",
        "execute can run files or commands. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)source\b",
        "source can execute files. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)eval\b",
        "eval can execute files. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Privacy and information exposure
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)less\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)less\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)more\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)more\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)head\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)head\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)tail\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)tail\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)strings\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)strings\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)hexdump\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)hexdump\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)xxd\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)xxd\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # SSH key and credential exposure
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*\.ssh/\b",
        "Reading SSH keys can expose credentials. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*id_rsa\b",
        "Reading private SSH keys can expose credentials. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*id_ed25519\b",
        "Reading private SSH keys can expose credentials. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*\.pem\b",
        "Reading .pem files can expose private keys. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*\.key\b",
        "Reading .key files can expose private keys. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Configuration files that might contain secrets
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*config\.",
        "Reading config files can expose sensitive information. Review what you're accessing. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)cat\s+[-\w]*\s*\.config\b",
        "Reading .config files can expose sensitive information. Review what you're accessing. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Network commands that might expose information
    (
        r"(^|\s&\s)netstat\s+[-\w]*\s*-a\b",
        "netstat -a can expose network connections. Use more specific options. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)ss\s+[-\w]*\s*-a\b",
        "ss -a can expose network connections. Use more specific options. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)ifconfig\b",
        "ifconfig can expose network interface information. Use ip command instead. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Process information that might expose sensitive data
    (
        r"(^|\s&\s)ps\s+[-\w]*\s*-ef\b",
        "ps -ef can expose command line arguments with sensitive data. Use ps aux instead. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)ps\s+[-\w]*\s*-e\b",
        "ps -e can expose command line arguments with sensitive data. Use ps aux instead. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # File system operations that might be destructive
    (
        r"(^|\s&\s)ln\s+[-\w]*\s*-s\s*/\b",
        "Creating symlinks to root directory can be destructive. Review the destination. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # User and permission management
    (
        r"(^|\s&\s)userdel\b",
        "userdel can delete user accounts. Review which user will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)groupdel\b",
        "groupdel can delete groups. Review which group will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)passwd\b",
        "passwd can change passwords. Review which user's password will be changed. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Cron and scheduled tasks
    (
        r"(^|\s&\s)crontab\s+[-\w]*\s*-r\b",
        "crontab -r can delete all cron jobs. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"(^|\s&\s)crontab\s+[-\w]*\s*-l\b",
        "crontab -l can expose scheduled tasks. Review what you're accessing. Request a human to run this command, clearly highlighting risks.",
    ),
]


def validate_command(command: str) -> list[str]:
    # Check for safe commands that should be allowed
    safe_commands = ["say ", "ls "]
    for safe_cmd in safe_commands:
        if command.startswith(safe_cmd):
            return []  # No issues for safe commands
    
    issues = []
    for pattern, message in VALIDATION_RULES:
        if re.search(pattern, command):
            issues.append(message)
    return issues


try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

if tool_name != "Bash" or not command:
    sys.exit(1)

# Check if bash safety checks are enabled
preferences = get_preferences()
bash_safety_checks = preferences.get('bash_safety_checks', {})
if not bash_safety_checks.get('enabled', True):
    print(f"Skipping bash safety checks.")
    sys.exit(0)

# Validate the command
issues = validate_command(command)

if issues:
    output = {
        "continue": True,
        "stopReason": f"Unsafe command blocked, requires Human approval: {'; '.join(issues)}",
        "suppressOutput": False,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": f"Unsafe command blocked, requires Human approval: {'; '.join(issues)}"
        }
    }
    log_decision(output, operation_type="unsafe_command_decision")
    print(json.dumps(output))
    sys.exit(2)