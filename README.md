![clauder](https://fasplnlepuuumfjocrsu.supabase.co/storage/v1/object/public/web-assets//clauder-character.png)

## `> CLAUDER` - a safer base configuration for Claude Code

> Safer rules so Claude Code does not accidentally set the world on fire trying to help 🔥

> [!WARNING]
> While `clauder` helps setting generic guardrails, these are **insufficient to autonomously ensure correctness and safety**. `clauder` is solely meant as a safety net and toolset, and *assumes co-supervision by a human in the loop*.

**Bluera Inc.** https://bluera.ai

## Overview

This repository contains a base Claude Code configuration that provides safety mechanisms, logging, and best practices for AI-assisted development. It includes file protection, command validation, audio feedback, and automated documentation enforcement.

## Get Started

### Installation

```bash
# Clone repository
git clone <repository-url>
cd clauder

# Install (must be run from the `clauder` dir)
source ./clauder_install.sh
```

### Usage

#### Activate Clauder in your project

> [!IMPORTANT]
> Activating Clauder may override any existing `.claude` configuration.

Run in your project directory:

```bash
clauder_activate

# or you may activate it from anywhere else by providing a path to the project
# clauder_activate ./project_path
```

> ☕ **Activation needs to be re-run on any `clauder` update** if and where you wish to propagate them.

This will copy the `.claude` configuration to your project.

Clauder's configuration will automatically:

- Create checkpoint commits before each session
- Protect sensitive files and directories
- Log all actions
- Enforce documentation updates
- Provides general guidelines/rules to Claude (never enforced, but does help steering it - Do not solely rely on instructions for policing or workflows)
- Provide audio feedback on completion (optional, supports mac, linux experimental)

#### How to start a Claude session

> [!IMPORTANT]
> **Opening Claude without interacting is sufficient to index and learn all secrets in the directory. Never keep secrets such as `.env` in the project directory.**
>
> If secrets have been indexed or read by an AI such as Claude, you should consider removing them from the project, invalidating them and renewing them. Production secrets should be stored in a secure vault, unreadable by AI. Keeping secrets out of the working directory prevents auto-indexing, but does not prevent Claude from finding ways to access them through running commands or calling tools. Clauder will try to prevent leaking secrets, potentially destructive, or unrecoverable actions, by detecting unsafe actions and requesting a Human in the loop, but none of it is bulletproof.
>
> **Please make sure to supervise your AI's actions as you grant it access to sensitive or critical systems. It cannot be trusted and will inadvertently make unrecoverable mistakes, which may critically impair the company and its production services. Backup your systems, and sandbox as much as possible through restrictive AI-level access control.** You are responsible for your AI's actions, as you are when using any other tool, or when managing a team.

Once you familiarize yourself with the above, you may start a new Claude Code session with Clauder security checks using:

```bash
clauder # a safer way to start 'claude' to prevent exposing secrets
```

In Claude, type:
```
/rules
```

This will define the mandatory guidelines for Claude Code.

## Features

> [!IMPORTANT]
> Although better than having no guardrails at all, **`clauder` can miss critical security threats**. It is meant as a basic safety net and a tool for human supervision. **Do not leave Claude unsupervised**, as it will make critical mistakes and/or learn to escape the guardrails.

### 🔒 Security & Safety

#### **Secret Detection & Prevention**
- **Multi-layered scanning**: Checks file names, patterns, and contents for secrets
- **Exclusion support**: Configurable exclusions via `.claude/.exclude_security_checks`
- **Pattern matching**: Detects API keys, passwords, tokens, and other sensitive data
- **Line-level reporting**: Shows exact file and line numbers for vulnerabilities
- **Content analysis**: Scans file contents for secret patterns (verbose mode)
- **Binary file detection**: Automatically skips binary and large files

#### **File Protection**
- **Immutable files**: Protects critical configuration files from modification
- **Environment protection**: Blocks access to `.env*` files and environment variables
- **Git protection**: Prevents destructive git operations (`rm .git`, `git reset`, etc.)
- **Permission-based**: Denies read/write access to sensitive directories

#### **Human-in-the-Loop**
- **MCP tool approval**: Requires approval for Supabase, Stripe, GitHub, Cloudflare operations
- **Destructive operation prevention**: Blocks potentially harmful commands
- **Environment variable protection**: Prevents commands containing env var names

### 📊 Logging & Monitoring

#### **Comprehensive Logging**
- **Bash command logging**: All shell commands logged to `~/.claude/bash-logs.txt`
- **MCP operation logging**: All MCP tool calls logged to `~/.claude/mcp-logs.txt`
- **Audit trail**: Complete history of all operations for security review
- **Structured logging**: JSON format for programmatic analysis

#### **Real-time Monitoring**
- **Pre-tool validation**: Validates operations before execution
- **Post-tool logging**: Records all completed operations
- **Error tracking**: Captures and logs all errors and warnings

### 🔄 Workflow Automation

#### **Git Integration**
- **Automatic checkpoints**: Creates commits before each Claude session
- **Commit enforcement**: Requires proper commit messages with `[claude]` prefix
- **Repository validation**: Ensures `.git/` directory exists before operations

#### **Documentation Enforcement**
- **HISTORY.md updates**: Automatically enforces change tracking, **if `HISTORY.md` exists at root level**
- **SPECIFICATIONS.md updates**: Enforces specification documentation, **if `SPECIFICATIONS.md` exists at root level**
- **Completion checks**: Validates documentation before session end

### 🎵 Audio Feedback

#### **Cross-platform Support**
- **macOS**: Uses `say` command for text-to-speech
- **Linux**: Uses `espeak` for text-to-speech (experimental)
- **Configurable**: Can be enabled/disabled via preferences

#### **Smart Notifications**
- **Task completion**: Audio summary when tasks are completed
- **Error alerts**: Audio notifications for critical issues
- **Customizable messages**: Configurable audio feedback content

### 🛠️ Tool Management

#### **Required Tools Validation**
- **Git**: Ensures git is available and repository is initialized
- **jq**: Validates JSON processing tool availability
- **Python**: Checks Python availability for script execution
- **Automatic detection**: Validates tools before each session

#### **Script Management**
- **Executable permissions**: Automatically sets proper permissions
- **Path resolution**: Smart path detection for cross-platform compatibility
- **Error handling**: Graceful failure with helpful error messages

### 🔧 Configuration Management

#### **Flexible Configuration**
- **Project-specific**: Each project can have its own `.claude` configuration
- **Inheritance**: Base configuration with project-specific overrides
- **Environment-aware**: Adapts to different development environments

#### **Exclusion Patterns**
- **Pattern-based**: Supports glob patterns for file/directory exclusions
- **Comment support**: Allows comments in exclusion files
- **Dynamic loading**: Loads exclusions at runtime

## File Structure

```
clauder/
├── README.md                             # This file - project documentation
├── clauder_activate.sh                   # Project activation script
├── clauder_install.sh                    # Installation script
├── clauder_security_check.sh             # Security validation script
├── .claude/                              # Claude configuration directory
│   ├── settings.json                     # Main Claude settings and hooks
│   ├── preferences.json                  # User preferences (audio, etc.)
│   ├── rules.md                          # Project-specific rules and guidelines
│   ├── requirements.md                   # Project requirements documentation
│   ├── .ignore                           # Files to ignore during operations
│   ├── .immutable                        # Files that should never be modified
│   ├── .exclude_security_checks          # Security check exclusions
│   ├── commands/                         # Custom command definitions
│   │   ├── consult.md                    # Consult command for external AI assistance
│   │   └── rules.md                      # Rules enforcement command
│   ├── logs/                             # Generated logs (created at runtime)
│   │   ├── bash-logs.txt                 # Bash command history
│   │   └── mcp-logs.txt                  # MCP tool call history
│   ├── .tmp/                             # Temporary files (created at runtime)
│   └── scripts/                          # Python and shell scripts
│       ├── check-ignore-patterns.py      # Pre-tool use ignore pattern checker
│       ├── check-immutable-patterns.py   # Pre-tool use immutable pattern checker
│       ├── check-required-tools.py       # User prompt tools validation
│       ├── git-checkpoint.py             # User prompt git checkpoint creation
│       ├── log-bash-commands.py          # Post-tool use bash command logging
│       ├── log-mcp-commands.py           # Post-tool use MCP command logging
│       ├── prevent-learning-secrets.py   # Main security checker (Python)
│       ├── prevent-unsafe-commands.py    # Git protection script
│       ├── require-human-approval.py     # Human approval for sensitive operations
│       ├── no-secrets-prompted.py        # Prompt validation for secrets
│       ├── enforce-completion-checks.py  # Documentation enforcement
│       └── audio-summary.py              # Audio feedback script
```

### Key Configuration Files

#### **`.claude/settings.json`**
- **Hooks**: Pre/Post tool use, user prompt, stop events
- **Permissions**: Read/write restrictions for sensitive files
- **Tool validation**: Required tools and repository checks
- **MCP protection**: Human approval for critical external service operations

#### **`.claude/.ignore`**
- **Pattern matching**: Files and directories to ignore
- **Environment files**: All `.env*` variations
- **Build artifacts**: `dist/`, `build/`, `node_modules/`
- **Version control**: `.git/` directory protection

> [!NOTE]
> As of July 2025, there is no possible way to prevent Claude from automatically & silently learning every change made to the codebase, including secrets. These are only meant as a best effort to prevent retrieving them.

#### **`.claude/.exclude_security_checks`**
- **Security exclusions**: Files/directories to skip in security scans
- **Glob patterns**: Supports wildcard patterns
- **Comment support**: Lines starting with `#` are ignored
- **Dynamic loading**: Loaded at runtime for each check

#### **`.claude/rules.md`**
- **Project guidelines**: Specific rules for the project
- **Best practices**: Development and security guidelines
- **Workflow instructions**: Step-by-step processes
- **Safety reminders**: Important security considerations

> [!NOTE]
> Rules can never be enforced, they are used to steer the AI in a desired direction.

### Scripts Overview

#### **`clauder_activate.sh`**
- **Project setup**: Copies `.claude` configuration to target project
- **Validation**: Checks project safety before activation
- **Backup**: Creates backups of existing configurations
- **Cross-platform**: Works on macOS, Linux, and Windows (WSL)

#### **`clauder_security_check.sh`**
- **Comprehensive scanning**: Multi-layered secret detection
- **Exclusion support**: Respects `.exclude_security_checks`
- **Verbose mode**: Detailed scanning with content analysis
- **JSON output**: Structured output for programmatic use
- **Line-level reporting**: Exact file and line number locations

#### **`clauder_install.sh`**
- **Shell detection**: Automatically detects zsh/bash configuration
- **Alias management**: Creates and manages shell aliases and variables
   * i.e. `clauder`, `clauder_activate`, `clauder_security_check`, and required configurations
- **Auto-sourcing**: Sources configuration after changes
- **Backup creation**: Creates backups before modifications

## Security Best Practices

### **Environment Secrets**
- **Never store in project**: Keep secrets outside the working directory
- **Secure vaults**: Use dedicated secret management systems
- **AI isolation**: Ensure AI cannot access production secrets
- **Regular rotation**: Rotate secrets if accidentally exposed

### **File Protection**
- **Immutable files**: Protect critical configuration files
- **Environment isolation**: Keep `.env` files separate from code
- **Git safety**: Never commit secrets to version control
- **Access control**: Use restrictive permissions for sensitive files

### **Supervision Requirements**
- **Human oversight**: Always supervise AI operations
- **Backup systems**: Maintain regular backups of critical systems
- **Sandboxing**: Use isolated environments for AI testing
- **Access limits**: Restrict AI access to sensitive systems

## Troubleshooting

### **Common Issues**

**Missing required tools**
```bash
# Install required tools
brew install git jq  # macOS
sudo apt install git jq  # Ubuntu/Debian
```

**Git repository not initialized**
```bash
# Initialize git repository
git init
```

**Permission denied errors**
```bash
# Make scripts executable
chmod +x .claude/scripts/*.py
chmod +x .claude/scripts/*.sh
```

**Audio not working**
```bash
# Check audio preferences
cat .claude/preferences.json
# Ensure "audio_summary.enabled" is true
```

### **Configuration Issues**

**Aliases not working**
```bash
# Re-run alias setup (Important: Run from the `clauder` directory)
source ./clauder_install.sh
# Or restart your shell
```

**Security checks failing**
```bash
# Check exclusion patterns (Important: Do not exclude actual secrets)
cat .claude/.exclude_security_checks
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

> Hooks documentation: https://docs.anthropic.com/en/docs/claude-code/hooks 
>
> **Tips:** Hooks are dedupped and run in parallel. They rely on strict interpretation from the console output for decision making. Make sure never to print anything other than the expected specifications for Claude Code to parse it correctly, any offset will cause Claude Code to omit the decision entirely. Beware of infinite loop, particularly when blocking a 'Stop' event to inject an extra step, as the 'Stop' event will retrigger once that step completes. By default, Claude Code will continue unless set to 'False'. A 'block' decision only blocks a given interaction with a 'reason', at which point Claude Code may decide to take a different action or find a way to bypass it. Use `claude --debug` to enable debug logs when working on hooks, as they are hidden by default. When developing, never test `Clauder` changes on a real project as bugs may have irreparable consequences - use a test project instead.

## License

Apache 2.0 - Bluera Inc.

> https://bluera.ai

---

**Remember**: This is a safety-first configuration. Always review changes before applying them to production systems. The AI assistant is a tool that requires supervision and should not be trusted with critical systems without proper oversight.