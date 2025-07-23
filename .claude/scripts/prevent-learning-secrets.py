#!/usr/bin/env python3
"""
Script to check if a project is safe for indexing.
Returns 0 (safe) or 1 (unsafe) based on presence of sensitive files/directories.
"""

import sys
import argparse
import fnmatch
import json
from pathlib import Path
from typing import List, Tuple

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;32m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'  # No Color


def print_status(color: str, message: str) -> None:
    """Print a colored status message."""
    print(f"{color}{message}{Colors.NC}")


class ProjectSafetyChecker:
    """Check if a project directory is safe for indexing."""
    
    def __init__(self):
        # Sensitive patterns to check (from .claude/.ignore)
        self.sensitive_patterns = [
            "secret",
            "private",
            "env",
            ".env",
            ".env.local",
            ".env.example",
            ".env.dev",
            ".env.development",
            ".env.stage",
            ".env.staging",
            ".env.sandbox",
            ".env.preprod",
            ".env.prod",
            ".env.production"
        ]
        
        # Additional patterns that might contain secrets
        self.secret_indicators = [
            "*key*",
            "*password*",
            "*token*",
            "*secret*",
            "*private*",
            "*privk*",
        ]
        
        # Load exclusion patterns (will be loaded when check_project_safety is called)
        self.exclusion_patterns = []
    
    def _load_exclusion_patterns(self, project_path: Path) -> List[str]:
        """Load exclusion patterns from .claude/.exclude_security_checks file."""
        exclusion_file = project_path / ".claude" / ".exclude_security_checks"
        patterns = []
        
        if 'standalone' in sys.argv:  # Debug output only in standalone mode
            print_status(Colors.GRAY, f"DEBUG: Looking for exclusion file at: {exclusion_file}")
            print_status(Colors.GRAY, f"DEBUG: Current working directory: {Path.cwd()}")
            print_status(Colors.GRAY, f"DEBUG: Project path: {project_path}")
        
        if exclusion_file.exists():
            try:
                with open(exclusion_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            patterns.append(line)
                if 'standalone' in sys.argv:  # Debug output only in standalone mode
                    print_status(Colors.GRAY, f"DEBUG: Loaded exclusion patterns: {patterns}")
            except (UnicodeDecodeError, PermissionError, OSError) as e:
                print(f"Warning: Could not read exclusion file {exclusion_file}: {e}")
        else:
            if 'standalone' in sys.argv:  # Debug output only in standalone mode
                print_status(Colors.GRAY, f"DEBUG: Exclusion file not found: {exclusion_file}")
        
        return patterns
    
    def _is_excluded(self, file_path: Path, project_path: Path) -> bool:
        """Check if a file or directory should be excluded from security checks."""
        relative_path = file_path.relative_to(project_path)
        
        for pattern in self.exclusion_patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                # Remove trailing slash for comparison
                dir_pattern = pattern.rstrip('/')
                # Check if the file is inside this directory
                if str(relative_path).startswith(dir_pattern + '/') or str(relative_path) == dir_pattern:
                    if 'standalone' in sys.argv:  # Debug output only in standalone mode
                        print_status(Colors.GRAY, f"DEBUG: Excluded {relative_path} by directory pattern {pattern}")
                    return True
            else:
                # Check if the pattern matches the file/directory name or path
                if fnmatch.fnmatch(str(relative_path), pattern) or fnmatch.fnmatch(file_path.name, pattern):
                    if 'standalone' in sys.argv:  # Debug output only in standalone mode
                        print_status(Colors.GRAY, f"DEBUG: Excluded {relative_path} by pattern {pattern}")
                    return True
                
                # Check if any parent directory matches the pattern
                for parent in relative_path.parents:
                    if fnmatch.fnmatch(str(parent), pattern):
                        if 'standalone' in sys.argv:  # Debug output only in standalone mode
                            print_status(Colors.GRAY, f"DEBUG: Excluded {relative_path} by parent pattern {pattern}")
                        return True
        
        return False
    
    def check_exact_matches(self, project_path: Path) -> List[Tuple[str, str]]:
        """Check for exact matches of sensitive patterns."""
        found_items = []
        
        for pattern in self.sensitive_patterns:
            item_path = project_path / pattern
            if item_path.exists() and not self._is_excluded(item_path, project_path):
                found_items.append((pattern, str(item_path.relative_to(project_path))))
        
        return found_items
    
    def check_pattern_matches(self, project_path: Path) -> List[Tuple[str, str]]:
        """Check for files/directories containing sensitive patterns."""
        found_patterns = []
        
        for pattern in self.sensitive_patterns:
            # Skip exact matches we already checked
            if (project_path / pattern).exists():
                continue
                
            # Search for files/directories containing the pattern
            for item in project_path.rglob(f"*{pattern}*"):
                if (item.is_file() or item.is_dir()) and not self._is_excluded(item, project_path):
                    found_patterns.append((pattern, str(item.relative_to(project_path))))
                    break
        
        return found_patterns
    
    def check_secret_indicators(self, project_path: Path) -> List[Tuple[str, str]]:
        """Check for files that might contain secrets based on naming patterns."""
        found_indicators = []
        
        for indicator in self.secret_indicators:
            for item in project_path.rglob(indicator):
                if (item.is_file() or item.is_dir()) and not self._is_excluded(item, project_path):
                    found_indicators.append((indicator, str(item.relative_to(project_path))))
                    break
        
        return found_indicators
    
    def check_file_contents(self, project_path: Path) -> List[Tuple[str, str, int]]:
        """Check file contents for obvious secret patterns."""
        suspicious_files = []
        
        # Common secret patterns in file contents
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'private\s*=\s*["\'][^"\']+["\']',
            r'privk\s*=\s*["\'][^"\']+["\']',
            r'sk-[a-zA-Z0-9]{20,}',  # OpenAI API key pattern
            r'[a-zA-Z0-9]{32,}',     # Generic long strings
        ]
        
        import re
        
        for file_path in project_path.rglob('*'):
            if not file_path.is_file():
                continue
                
            # Skip excluded files
            if self._is_excluded(file_path, project_path):
                continue
                
            # Skip binary files and large files
            if self._is_binary_file(file_path) or file_path.stat().st_size > 1024 * 1024:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            relative_path = str(file_path.relative_to(project_path))
                            suspicious_files.append((relative_path, pattern, line_num))
                            break
                        
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
        
        return suspicious_files
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is likely binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except (PermissionError, OSError):
            return True
    
    def check_project_safety(self, project_path: Path, standalone: bool = False) -> Tuple[bool, dict]:
        """
        Check if a project is safe for indexing.
        
        Returns:
            Tuple of (is_safe, results_dict)
        """
        if not project_path.exists():
            raise FileNotFoundError(f"Directory '{project_path}' does not exist")
        
        if not project_path.is_dir():
            raise NotADirectoryError(f"'{project_path}' is not a directory")
        
        # Load exclusion patterns
        self.exclusion_patterns = self._load_exclusion_patterns(project_path)
        
        # print_status(Colors.YELLOW, "Checking project safety for indexing...")
        # print(f"Project directory: {project_path.resolve()}")
        
        # Use the standalone parameter passed to the method
        is_standalone = standalone
        
        if self.exclusion_patterns and is_standalone:
            print_status(Colors.GRAY, f"* Excluding {len(self.exclusion_patterns)} patterns from security checks")
            for pattern in self.exclusion_patterns:
                print_status(Colors.GRAY, f"  - {pattern}")
        
        results = {
            'exact_matches': [],
            'pattern_matches': [],
            'secret_indicators': [],
            'suspicious_contents': []  # Will contain tuples of (file_path, pattern, line_num)
        }
        
        # Check exact matches
        results['exact_matches'] = self.check_exact_matches(project_path)
        if is_standalone:
            for pattern, file_path in results['exact_matches']:
                print_status(Colors.RED, f"❌ [Security] Found: {pattern} ({file_path})")
        
        # Check pattern matches
        results['pattern_matches'] = self.check_pattern_matches(project_path)
        if is_standalone:
            for pattern, file_path in results['pattern_matches']:
                print_status(Colors.RED, f"❌ [Security] Found files/directories containing: {pattern} ({file_path})")
        
        # Check secret indicators
        results['secret_indicators'] = self.check_secret_indicators(project_path)
        if is_standalone:
            for indicator, file_path in results['secret_indicators']:
                print_status(Colors.RED, f"⚠️  [Security] Potential secret indicator: {indicator} ({file_path})")
        
        # Check file contents
        results['suspicious_contents'] = self.check_file_contents(project_path)
        if is_standalone:
            for file_path, pattern, line_num in results['suspicious_contents']:
                print_status(Colors.RED, f"🔍 [Security] Suspicious potential secret found in: {file_path} (line {line_num})")
        
        # Determine if project is safe
        is_safe = (len(results['exact_matches']) == 0 and 
                  len(results['pattern_matches']) == 0)
        
        if is_standalone:
            if is_safe:
                print_status(Colors.BLUE, "• No exposed secrets detected. Proceeding..")
            else:
                print_status(Colors.RED, "🚨 [Security] Project is not safe for indexing. Aborting..")
                print_status(Colors.RED, "Found sensitive information in files/directories that should be excluded. If secrets have been indexed or read by an AI, you should consider removing them from the project, invalidating them and renewing them. Opening an AI session without interacting is sufficient to index secrets. Secrets must not be stored in the project itself. Production secrets should be stored in a secure vault, unreadable by AI.")
                
                if results['secret_indicators']:
                    print_status(Colors.YELLOW, "[Security] Note: Additional potential secret indicators found")
                if results['suspicious_contents']:
                    print_status(Colors.YELLOW, "[Security] Note: Files with suspicious content patterns found")
        
        return is_safe, results


def main():
    """Main function to handle command line arguments and run the safety check."""
    parser = argparse.ArgumentParser(
        description="Check if a project directory is safe for indexing by looking for sensitive files/directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Check current directory
  %(prog)s /path/to/project   # Check specific directory
  %(prog)s -v                 # Verbose mode with content checking
        """
    )
    
    parser.add_argument(
        'project_directory',
        nargs='?',
        default='.',
        help='Directory to check (default: current directory)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose mode (checks file contents and pattern matches)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--standalone',
        action='store_true',
        help='Run in standalone mode with colored output'
    )
    
    args = parser.parse_args()
    
    try:
        project_path = Path(args.project_directory)
        checker = ProjectSafetyChecker()
        is_safe, results = checker.check_project_safety(project_path, standalone=args.standalone)
        
        # Check if running as a hook vs standalone
        is_hook = not args.standalone
        
        if is_hook:
            # JSON format for hooks
            if is_safe:
                output = {
                    "reason": "No exposed secrets detected. Proceeding."
                }
            else:
                output = {
                    "continue": False,
                    "stopReason": "Security policy violation. Project is not safe for indexing. Found sensitive information in files/directories that should be excluded. If secrets have been indexed or read by an AI, you should consider removing them from the project, invalidating them and renewing them. Opening an AI session without interacting is sufficient to index secrets. Secrets must not be stored in the project itself. Production secrets should be stored in a secure vault, unreadable by AI.",
                    "suppressOutput": True,
                    "decision": "block",
                    "reason": "Security policy violation. Project is not safe for indexing. Found sensitive information in files/directories that should be excluded."
                }
            print(json.dumps(output))
            
        elif args.json:
            # Convert tuples to dictionaries for JSON serialization
            json_results = results.copy()
            
            # Convert exact_matches tuples
            json_results['exact_matches'] = [
                {'pattern': pattern, 'file': file_path}
                for pattern, file_path in results['exact_matches']
            ]
            
            # Convert pattern_matches tuples
            json_results['pattern_matches'] = [
                {'pattern': pattern, 'file': file_path}
                for pattern, file_path in results['pattern_matches']
            ]
            
            # Convert secret_indicators tuples
            json_results['secret_indicators'] = [
                {'indicator': indicator, 'file': file_path}
                for indicator, file_path in results['secret_indicators']
            ]
            
            # Convert suspicious_contents tuples
            json_results['suspicious_contents'] = [
                {'file': file_path, 'pattern': pattern, 'line': line_num}
                for file_path, pattern, line_num in results['suspicious_contents']
            ]
            
            output = {
                'safe': is_safe,
                'project_directory': str(project_path.resolve()),
                'results': json_results
            }
            print(json.dumps(output, indent=2))
        
        sys.exit(0 if is_safe else 2)
        
    except (FileNotFoundError, NotADirectoryError) as e:
        output = {
            "decision": "block",
            "reason": f"Error: {e}"
        }
        print(json.dumps(output))
        sys.exit(1)
    except KeyboardInterrupt:
        output = {
            "decision": "block",
            "reason": "Operation cancelled by user"
        }
        print(json.dumps(output))
        sys.exit(1)
    except Exception as e:
        output = {
            "decision": "block",
            "reason": f"Unexpected error: {e}"
        }
        print(json.dumps(output))
        sys.exit(1)


if __name__ == "__main__":
    main()
