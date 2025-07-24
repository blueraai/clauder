#!/usr/bin/env python3
import json
import re
import sys

# Define validation rules as a list of (regex pattern, message) tuples
VALIDATION_RULES = [
    # File deletion commands
    (
        r"\brm\b",
        "rm operations are not allowed. Use 'git rm' for tracked files or request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bunlink\b",
        "unlink can delete files. Use 'git rm' for tracked files or request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bshred\b",
        "shred permanently destroys files. This operation is irreversible. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Git destructive operations
    (
        r"\bgit\s+reset\b",
        "git reset can cause data loss. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgit\s+branch\s+[-\w]*\s*-[dD]\b",
        "git branch -d/-D can delete branches. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgit\s+rebase\b",
        "git rebase rewrites history. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgit\s+push\s+[-\w]*\s*--force\b",
        "git push --force can overwrite remote history. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgit\s+push\s+[-\w]*\s*-f\b",
        "git push -f can overwrite remote history. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgit\s+clean\b",
        "git clean can delete untracked files. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgit\s+gc\s+[-\w]*\s*--prune\b",
        "git gc --prune can permanently delete unreferenced objects. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # System destructive commands
    (
        r"\bdd\b",
        "dd can overwrite disk data. This is extremely destructive. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bformat\b",
        "format commands can destroy disk partitions. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bfdisk\b",
        "fdisk can modify disk partitions. This is destructive. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bparted\b",
        "parted can modify disk partitions. This is destructive. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bmkfs\b",
        "mkfs creates new filesystems and destroys existing data. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bchmod\b",
        "chmod changes permissions. This is a security risk. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Process management (potentially destructive)
    (
        r"\bkill\s+[-\w]*\s*-9\b",
        "kill -9 forces process termination. Use regular kill first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bkillall\b",
        "killall can terminate multiple processes. Review which processes will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bpkill\b",
        "pkill can terminate processes by name. Review which processes will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Network and service commands (potentially disruptive)
    (
        r"\bservice\s+[-\w]*\s*stop\b",
        "service stop can disrupt system services. Review which service will be stopped. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bsystemctl\s+[-\w]*\s*stop\b",
        "systemctl stop can disrupt system services. Review which service will be stopped. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bsystemctl\s+[-\w]*\s*disable\b",
        "systemctl disable can prevent services from starting. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Package management (potentially destructive)
    (
        r"\bapt\s+[-\w]*\s*remove\b",
        "apt remove can uninstall packages. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bapt\s+[-\w]*\s*purge\b",
        "apt purge can completely remove packages and configs. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\byum\s+[-\w]*\s*remove\b",
        "yum remove can uninstall packages. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bbrew\s+[-\w]*\s*uninstall\b",
        "brew uninstall can remove packages. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Database operations (potentially destructive)
    (
        r"\bdrop\s+database\b",
        "drop database can permanently delete databases. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+table\b",
        "drop table can permanently delete tables. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\btruncate\s+table\b",
        "truncate table can permanently delete all data. Review first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdelete\s+from\b",
        "delete from can remove rows from tables. Review what will be deleted first. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+policy\b",
        "drop policy can remove security policies. Review which policy will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+role\b",
        "drop role can remove database roles. Review which role will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+user\b",
        "drop user can remove database users. Review which user will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+index\b",
        "drop index can remove database indexes. Review which index will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+view\b",
        "drop view can remove database views. Review which view will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+function\b",
        "drop function can remove database functions. Review which function will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+procedure\b",
        "drop procedure can remove database procedures. Review which procedure will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+trigger\b",
        "drop trigger can remove database triggers. Review which trigger will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+constraint\b",
        "drop constraint can remove database constraints. Review which constraint will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+sequence\b",
        "drop sequence can remove database sequences. Review which sequence will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+type\b",
        "drop type can remove database types. Review which type will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+schema\b",
        "drop schema can remove database schemas. Review which schema will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bdrop\s+extension\b",
        "drop extension can remove database extensions. Review which extension will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bexec\b",
        "exec can execute files or commands. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bexecute\b",
        "execute can run files or commands. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bsource\b",
        "source can execute SQL files. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\.\s*\.\b",
        ".. can execute files in some contexts. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\i\b",
        "\\i can include/execute SQL files. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\ir\b",
        "\\ir can include/execute SQL files. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\include\b",
        "\\include can include/execute SQL files. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\copy\b",
        "\\copy can copy data to/from files. Review what will be copied. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\w\b",
        "\\w can write SQL to files. Review what will be written. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\o\b",
        "\\o can redirect output to files. Review what will be written. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\h\b",
        "\\h can execute shell commands. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\b\\!\b",
        "\\! can execute shell commands. Review what will be executed. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Privacy and information exposure
    (
        r"\bcat\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcat\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bless\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bless\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bmore\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bmore\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bhead\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bhead\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\btail\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\btail\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bstrings\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bstrings\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bhexdump\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bhexdump\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bxxd\s+[-\w]*\s*\.env\b",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bxxd\s+[-\w]*\s*\.env\.",
        "Reading .env files can expose secrets. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # SSH key and credential exposure
    (
        r"\bcat\s+[-\w]*\s*\.ssh/\b",
        "Reading SSH keys can expose credentials. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcat\s+[-\w]*\s*id_rsa\b",
        "Reading private SSH keys can expose credentials. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcat\s+[-\w]*\s*id_ed25519\b",
        "Reading private SSH keys can expose credentials. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcat\s+[-\w]*\s*\.pem\b",
        "Reading .pem files can expose private keys. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcat\s+[-\w]*\s*\.key\b",
        "Reading .key files can expose private keys. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Configuration files that might contain secrets
    (
        r"\bcat\s+[-\w]*\s*config\.",
        "Reading config files can expose sensitive information. Review what you're accessing. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcat\s+[-\w]*\s*\.config\b",
        "Reading .config files can expose sensitive information. Review what you're accessing. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Network commands that might expose information
    (
        r"\bnetstat\s+[-\w]*\s*-a\b",
        "netstat -a can expose network connections. Use more specific options. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bss\s+[-\w]*\s*-a\b",
        "ss -a can expose network connections. Use more specific options. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bifconfig\b",
        "ifconfig can expose network interface information. Use ip command instead. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Process information that might expose sensitive data
    (
        r"\bps\s+[-\w]*\s*-ef\b",
        "ps -ef can expose command line arguments with sensitive data. Use ps aux instead. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bps\s+[-\w]*\s*-e\b",
        "ps -e can expose command line arguments with sensitive data. Use ps aux instead. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # File system operations that might be destructive
    (
        r"\bmv\s+[-\w]*\s*/\b",
        "Moving files to root directory can be destructive. Review the destination. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcp\s+[-\w]*\s*/\b",
        "Copying files to root directory can be destructive. Review the destination. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bln\s+[-\w]*\s*-s\s*/\b",
        "Creating symlinks to root directory can be destructive. Review the destination. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # User and permission management
    (
        r"\buserdel\b",
        "userdel can delete user accounts. Review which user will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bgroupdel\b",
        "groupdel can delete groups. Review which group will be affected. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bpasswd\b",
        "passwd can change passwords. Review which user's password will be changed. Request a human to run this command, clearly highlighting risks.",
    ),
    
    # Cron and scheduled tasks
    (
        r"\bcrontab\s+[-\w]*\s*-r\b",
        "crontab -r can delete all cron jobs. Review what will be removed. Request a human to run this command, clearly highlighting risks.",
    ),
    (
        r"\bcrontab\s+[-\w]*\s*-l\b",
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

# Validate the command
issues = validate_command(command)

if issues:
    output = {
        "continue": True,
        "stopReason": "Unsafe command blocked, requires Human approval.",
        "suppressOutput": False,
        "decision": "block",
        "reason": f"Unsafe command blocked, requires Human approval: {'; '.join(issues)}"
    }
    print(json.dumps(output))
    sys.exit(2)