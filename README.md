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
- Protect sensitive files and directories (see `.claude/.ignore` and `.claude/.immutable`)
- Log all actions for live monitoring, or auditing purposes (see `.claude/logs`)
- Enforce history and specifications tracking as you interact with Claude Code (see `HISTORY.md`, `SPECIFICATIONS.md`)
- Provides general guidelines/rules to Claude (see `.claude/rules.md`; Never guaranteed, but does help steering it; Do not solely rely on instructions for policing or workflows)
- Provide audio feedback on completion (optional, supports mac, linux experimental; enabled in `.claude/preferences.md`)
- Define custom commands for advanced workflows (e.g. `/consult` to consult a third party model for specific tasks, `/spawn` to create task specific agents)
   - *Required MCP servers detailed below.*

#### How to start a Claude session

> [!IMPORTANT]
> **Opening Claude without interacting is sufficient to index and learn all secrets in the directory. Never keep secrets such as `.env` in the project directory.**
>
> If secrets have been indexed or read by an AI such as Claude, you should consider removing them from the project, invalidating them and renewing them. Production secrets should be stored in a secure vault, unreadable by AI. Keeping secrets out of the working directory prevents auto-indexing, but does not prevent Claude from finding ways to access them through running commands or calling tools. Clauder will try to prevent leaking secrets, potentially destructive, or unrecoverable actions, by detecting unsafe actions and requesting a Human in the loop, but none of it is bulletproof.
>
> **Please make sure to supervise your AI's actions as you grant it access to sensitive or critical systems. It cannot be trusted and will inadvertently make unrecoverable mistakes, which may critically impair the company and its production services. Backup your systems, and sandbox as much as possible through restrictive AI-level access control.** You are responsible for your AI's actions, as you are when using any other tool, or when managing a team.

Once you familiarize yourself with the above, and set your forbidden paths in `.claude/.ignore`, you may start a new Claude Code session with Clauder security checks using:

```bash
clauder # a safer way to start 'claude' to prevent exposing secrets
```

In Claude, type:
```
/rules
```

This will define the mandatory guidelines for Claude Code.

> [!TIP]
> - If your project includes a `HISTORY.md` file at root level, `clauder` will enforce keeping a history of requests and actions taken, and use it to reason about the next action to take. 
> - If your project includes a `SPECIFICATIONS.md` file at root level, `clauder` will enforce keeping an updated list of specifications as it takes actions, and use it to reason about the next action to take. When writing code manually, you may ask `clauder` to read the git diffs and backfill the specifications file.
> - Define your secret files and folders in `.claude/.ignore` so `clauder` can guard them from being read/written.
> - Define your read-only files and folders in `.claude/.immutable` so `clauder` can guard them from being overwritten.
> - In `.gitignore`, exclude `.claude/logs` and `.claude/.tmp` for cleaner commits.
> - Check `.claude/requirements.md` for prerequisites, and recommended [MCP tools](https://docs.anthropic.com/en/docs/claude-code/mcp). `clauder` will *automatically* take advantage of those tools should you have added them to Claude Code.
> - Check [Claude Code's best practices](https://www.anthropic.com/engineering/claude-code-best-practices) for better results.

#### How to ask Claude to for a general review

You may ask for a general purpose code review using:

```sh
/review
```

or about something specific:

```sh
/review Assess the responsiveness of this application
```

> Create custom commands or sub-agents for project specic-reviews.

#### How to ask Claude to consult a different model

While Claude's models are performant for general coding, for particular tasks, such as ones requiring extensive context, or specialized training, requiring help from a different model may lead to better results.

If the [consult7](https://github.com/szeider/consult7) MCP tool is added to Claude Code, with a valid [OpenRouter](https://openrouter.ai) key, `clauder` will allow you to consult any supported model via the following command (default: `google/gemini-2.5-pro`, 1M token context):

```sh
/consult <user query>
```

e.g.

```sh
/consult Review the security of this application
```

> Note:
> - Files and directories listed in `.claude/.ignore` will not be passed as context.
> - Third party models consulted in the cloud do not have access to Claude Code's tools.

#### How to create specialized agents

Claude may create dedicated agents for specific tasks. They are called [Sub-Agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) and report to the main `Claude` instance. These agents have their own system prompts, tools subsets (inherit all tools by default), and context window (unaware of other chats). They are helpful in creating and recalling task-specific personas and context.

`clauder` includes a `agent-builder` agent, which helps you define and craft performant agents for your specific needs. Should the [context7](https://github.com/upstash/context7) and [consult7](https://github.com/szeider/consult7) MCP tools be set in Claude Code, it will automatically use them to help enhance the new agent's workflows, best practices, and toolsets. For better results, please be specific and detailed when creating specialized agents.

You may create a new agent simply by asking for it:

```sh
Create a new agent to help review my code, it should.. 
```

or using the `/spawn` command explicitly.

```sh
/spawn Create a new agent to help review my code, it should.. 
```

The resulting agent instructions will be define in `.claude/agents/<agent-name>.md`. You may review, and edit this file to further refine your new sub-agent. You may dismiss a sub-agent at any time, by deleting `.claude/agents/<agent-name>.md`.

**New agents become available/unavailable on start of a new Claude Code session**. Creating or deleting an agent will not apply to current sessions. Start a new `clauder` session to use your newly created agent.

##### Looking to recruit new sub agents?

`clauder` includes a command to recommend sub-agents for your project.

You may ask for general project-specific recommendations using:

```sh
/recruit
```

or about something specific:

```sh
/recruit I want to make this web app..
```

#### How to trace & audit Claude

Every event and automated `clauder` intervention is locally logged in a SQLite database for auditing and live monitoring Claude.

That database is available at `.claude/logs/trace.sqlite`, once the first event has been logged.

Additionally, all `bash` commands ran and MCP tool calls are duplicated as text logs for easy inspection at `.claude/logs/bash-logs.txt` and `.claude/logs/mcp-logs.txt`.

##### Real-time monitoring with Clauder Tracer

You may use or build any monitoring app you'd like to inspect that SQLite database. For convenience, a lightweight tracer app is also shipped with `clauder`.

You may run the tracer app in a parallel termimal at any time, new events will be live streamed to it:

###### Install

```bash
# install (using conda, in project directory)
conda create -n clauder_trace python=3.11 -y && conda activate clauder_trace && pip install -r ./.claude/tracer/requirements.txt

# install (without conda, in project directory)
pip install -r ./.claude/tracer/requirements.txt
```

###### Run

```bash
# run (using conda, in project directory)
conda activate clauder_trace && clauder_trace

# run (without conda, in project directory)
clauder_trace
```

Access the tracer app at `http://localhost:4441` in your browser.

![tracer-preview](https://fasplnlepuuumfjocrsu.supabase.co/storage/v1/object/public/web-assets//tracer-preview@0.5x.png)

> [!TIP]
> You may set any of the supported themes: `green`, `blue`, `gray`, `dark`
> 
> Run in browser console: `localStorage.setItem('clauder.tracer.theme', 'dark'); location.reload();`

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
- **Bash command logging**: All shell commands logged to `.claude/logs/bash-logs.txt`
- **MCP operation logging**: All MCP tool calls logged to `.claude/logs/mcp-logs.txt`
- **Audit trail**: Complete history of all operations for security review in local SQLite database at `.claude/logs/trace.sqlite`
- **Tracer app**: A lightweight web app can be ran in parallel to audit and monitor Claude (see `clauder_trace`)

#### **Real-time Monitoring**
- **Pre-tool validation**: Validates operations before execution
- **Post-tool logging**: Records all completed operations
- **Error tracking**: Captures and logs all errors and warnings

### ⚡ Workflow Automation

#### **Git Integration**
- **Automatic checkpoints**: Creates commits before each Claude session
- **Commit enforcement**: Requires proper commit messages with `[claude]` prefix
- **Repository validation**: Ensures `.git/` directory exists before operations

#### **Documentation Enforcement**
- **HISTORY.md updates**: Automatically enforces change tracking, **if `HISTORY.md` exists at root level**
- **SPECIFICATIONS.md updates**: Enforces specification documentation, **if `SPECIFICATIONS.md` exists at root level**
- **Completion checks**: Validates documentation before session end

### 🛠️ Agentic Toolset

#### **Custom Commands**
- **Consult third party models**: Ask any supported OpenRouter model for a particular tasks (see `/consult` above)
- **Create specialized sub-agents**: Create advanced specialized agent to work on specific tasks (see `/spawn` above)
- **Code review**: Request a comprehensive code review of the project or specific files (see `/review` above)
- **Sub-agent recruitment**: Get recommendations for specialized sub-agents based on project needs (see `/recruit` above)


#### **MCP Tooling Detection**
- **Automatic Optimatization**: Automatically utilizes the available MCP tools to enhance the above commands

### 🎵 Audio Feedback

#### **Cross-platform Support**
- **macOS**: Uses `say` command for text-to-speech
- **Linux**: Uses `espeak` for text-to-speech (experimental)
- **Configurable**: Can be enabled/disabled via preferences

#### **Smart Notifications**
- **Task completion**: Audio summary when tasks are completed
- **Error alerts**: Audio notifications for critical issues
- **Customizable messages**: Configurable audio feedback content


### 🔄 Automated Maintenance

#### **Automated Backups**
- **Periodic snapshots**: Creates backups of `.claude` configurations
- **Versioned storage**: Maintains backup history with timestamps
- **Rollback support**: Maintains ability to revert problematic updates

#### **Automated Updates**
- **Version checking**: Automated version checks on running `clauder`
- **Auto-install**: Automatically installs the latest `clauder` when a new version is available

## File Structure

```
clauder/
├── README.md                             # This file - project documentation
├── CODE_OF_CONDUCT.md                    # Community guidelines and behavior standards
├── LICENSE                               # Apache 2.0 license file
├── SECURITY.md                           # Security policy and vulnerability reporting
├── clauder_activate.sh                   # Project activation script
├── clauder_install.sh                    # Installation script
├── clauder_security_check.sh             # Security validation script
├── clauder_update_check.sh               # Update checking and management script
├── assets/                               # Externalized assets and messages
│   ├── clauder_banner.txt                # ASCII art banner displayed before clauder
│   └── clauder_footer.txt                # Footer message with links and reminders
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
│   │   ├── spawn.md                      # Spawn command for creating sub-agents
│   │   └── rules.md                      # Rules enforcement command
│   ├── agents/                           # Sub-agent definitions
│   │   └── agent-builder.md              # Agent builder for creating specialized agents
│   ├── logs/                             # Generated logs (created at runtime)
│   │   ├── bash-logs.txt                 # Bash command history
│   │   ├── mcp-logs.txt                  # MCP tool call history
│   │   └── trace.sqlite                  # SQLite database for trace events
│   ├── .tmp/                             # Temporary files (created at runtime)
│   ├── tracer/                           # Trace viewer web application
│   │   ├── app.py                        # Flask web server for trace viewer
│   │   ├── requirements.txt              # Python dependencies for tracer
│   │   └── templates/                    # HTML templates
│   │       └── index.html                # Main trace viewer interface
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
│       ├── audio-summary.py              # Audio feedback script
│       ├── trace-event.py                # General event logging script
│       └── utils/                        # Utility modules
│           └── trace_decision.py         # Trace decision logging module
```

### Key Configuration Files

#### **`.claude/settings.json`**

Defines hooks and permissions.

#### **`.claude/.ignore`**

Files and directories to ignore (forbidden read & write).

> [!NOTE]
> As of July 2025, there is no possible way to prevent Claude from automatically & silently learning every change made to the codebase, including secrets. These are only meant as a best effort to prevent retrieving them.

#### **`.claude/.immutable`**

Files and directories that cannot be modified (read-only).

> [!NOTE]
> The immutable file list is strictly enforced and cannot be overridden, even with explicit user permission.

#### **`.claude/.exclude_security_checks`**

Files and directories to skip in security scans.

#### **`.claude/rules.md`**

Behavioral guidelines.

> [!NOTE]
> Rules can never be enforced, they are used to steer the AI in a desired direction.

#### **`.claude/preferences.md`**

User preferences and customization settings.

#### **`.claude/requirements.md`**

Clauder dependencies and recommended MCP servers.

## Security Best Practices

### **Environment Secrets**
- **Never store in project**: Keep secrets outside the working directory
- **Secure vaults**: Use dedicated secret management systems
- **AI isolation**: Ensure AI cannot access production secrets
- **Regular rotation**: Rotate secrets if accidentally exposed

### **Supervision Requirements**
- **Human oversight**: Always supervise AI operations
- **Backup systems**: Maintain regular backups of critical systems
- **Sandboxing**: Use isolated environments for AI testing
- **Access limits**: Restrict AI access to sensitive systems

## Troubleshooting

### **Common Issues**

**Clauder crashes my terminal**
```bash
# Clauder will exit for safety purposes when detecting potential secrets, so they do not get indexed by Claude.
# For details about problematic files, run:

clauder_security_check & echo done
```

**New agent not found**
```bash
# New agents become available/unavailable on start of a new Claude Code session.
# Creating or deleting an agent will not apply to current sessions. 
# Start a new session to use your newly created agent.

clauder
```

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

**Safe commands blocked**
```bash
# You may choose to disable unsafe command detection in `.claude/preferences.json` at your own risk
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

# Alternatively, you may choose to disable secret pattern detection in `.claude/preferences.json`
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