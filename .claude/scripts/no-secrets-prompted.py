#!/usr/bin/env python3
import json
import sys
import re
import base64

def is_likely_secret(text):
    """Check if text looks like a secret based on various heuristics."""
    if not text or len(text.strip()) < 10:
        return False
    
    text = text.strip()
    
    # Check for common secret patterns
    secret_patterns = [
        # API keys and tokens
        r'^[a-zA-Z0-9]{32,}$',  # Long alphanumeric strings
        r'^sk_[a-zA-Z0-9]{24,}$',  # Stripe secret keys
        r'^pk_[a-zA-Z0-9]{24,}$',  # Stripe public keys
        r'^ghp_[a-zA-Z0-9]{36}$',  # GitHub personal access tokens
        r'^gho_[a-zA-Z0-9]{36}$',  # GitHub OAuth tokens
        r'^ghu_[a-zA-Z0-9]{36}$',  # GitHub user-to-server tokens
        r'^ghs_[a-zA-Z0-9]{36}$',  # GitHub server-to-server tokens
        r'^ghr_[a-zA-Z0-9]{36}$',  # GitHub refresh tokens
        r'^[a-zA-Z0-9]{40}$',  # SHA-1 hashes (like git commit hashes)
        r'^[a-zA-Z0-9]{64}$',  # SHA-256 hashes
        r'^[a-zA-Z0-9]{128}$',  # SHA-512 hashes
        
        # JWT tokens
        r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$',
        
        # Base64 encoded strings (likely secrets)
        r'^[A-Za-z0-9+/]{20,}={0,2}$',
        
        # UUIDs (might be secrets)
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        
        # Private keys (PEM format)
        r'^-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        r'^-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
        r'^-----BEGIN\s+DSA\s+PRIVATE\s+KEY-----',
        r'^-----BEGIN\s+EC\s+PRIVATE\s+KEY-----',
        
        # SSH keys
        r'^ssh-rsa\s+[A-Za-z0-9+/]+',
        r'^ssh-ed25519\s+[A-Za-z0-9+/]+',
        r'^ssh-dss\s+[A-Za-z0-9+/]+',
        
        # Database connection strings
        r'^(postgresql|mysql|mongodb|redis)://[^@]+@[^:]+:\d+',
        r'^mongodb\+srv://[^@]+@[^/]+',
        
        # AWS credentials
        r'^AKIA[0-9A-Z]{16}$',  # AWS access key ID
        r'^[A-Za-z0-9/+=]{40}$',  # AWS secret access key
        
        # Email addresses (might contain sensitive info)
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        
        # Phone numbers
        r'^\+?[1-9]\d{1,14}$',
        
        # Credit card numbers (basic pattern)
        r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$',
    ]
    
    for pattern in secret_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    
    # Check for high entropy (random-looking strings)
    if len(text) > 20:
        # Count character types
        has_upper = bool(re.search(r'[A-Z]', text))
        has_lower = bool(re.search(r'[a-z]', text))
        has_digit = bool(re.search(r'\d', text))
        has_special = bool(re.search(r'[^A-Za-z0-9]', text))
        
        # If it has multiple character types and is long, it might be a secret
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        if char_types >= 3 and len(text) > 30:
            return True
    
    return False

def check_quoted_content(text):
    """Check for secrets in quoted content."""
    # Find all quoted strings
    quoted_patterns = [
        r'"([^"]{10,})"',  # Double quoted strings
        r"'([^']{10,})'",  # Single quoted strings
        r'`([^`]{10,})`',  # Backtick quoted strings
    ]
    
    for pattern in quoted_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if is_likely_secret(match):
                return True
    
    return False

def check_for_sensitive_keywords(text):
    """Check for sensitive keywords that might indicate secrets."""
    sensitive_keywords = [
        r'(?i)\b(password|secret|key|token|private|pwd|encrypt|enc)\s*[:=]',
        r'(?i)\b(api_key|access_key|secret_key|private_key)\s*[:=]',
        r'(?i)\b(auth|authentication|authorization)\s*[:=]',
        r'(?i)\b(credential|cred)\s*[:=]',
        r'(?i)\b(login|username|user)\s*[:=]',
        r'(?i)\b(database|db|connection)\s*[:=]',
        r'(?i)\b(host|port|endpoint|url)\s*[:=]',
        r'(?i)\b(session|cookie)\s*[:=]',
        r'(?i)\b(signature|sign)\s*[:=]',
        r'(?i)\b(hash|digest|checksum)\s*[:=]',
    ]
    
    for pattern in sensitive_keywords:
        if re.search(pattern, text):
            return True
    
    return False

# Load input from stdin
try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

prompt = input_data.get("prompt", "")

# Check for sensitive keywords
if check_for_sensitive_keywords(prompt):
    output = {
        "continue": False,
        "stopReason": "Security policy violation: Prompt contains sensitive keywords. Please rephrase your request without sensitive information.",
        "suppressOutput": True,
        "decision": "block",
        "reason": "Security policy violation: Prompt contains sensitive keywords. Please rephrase your request without sensitive information."
    }
    print(json.dumps(output))
    sys.exit(2)

# Check for secrets in quoted content
if check_quoted_content(prompt):
    output = {
        "continue": False,
        "stopReason": "Security policy violation: Quoted content contains potential secrets. Please rephrase your request without sensitive information.",
        "suppressOutput": True,
        "decision": "block",
        "reason": "Security policy violation: Quoted content contains potential secrets. Please rephrase your request without sensitive information."
    }
    print(json.dumps(output))
    sys.exit(2)

# Check for long strings that might be secrets
words = prompt.split()
for word in words:
    if is_likely_secret(word):
        output = {
            "continue": False,
            "stopReason": "Security policy violation: Prompt contains potential secret values. Please rephrase your request without sensitive information.",
            "suppressOutput": True,
            "decision": "block",
            "reason": "Security policy violation: Prompt contains potential secret values. Please rephrase your request without sensitive information."
        }
        print(json.dumps(output))
        sys.exit(2)

# Allow the prompt to proceed
output = {
    "reason": "No sensitive information detected in prompt. Proceeding."
}
print(json.dumps(output))
sys.exit(0)