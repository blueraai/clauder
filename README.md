![clauder](https://fasplnlepuuumfjocrsu.supabase.co/storage/v1/object/public/web-assets//clauder-character.png)

## `> CLAUDER` - a safer and supercharged configuration for Claude Code

<p align="left">
    <a href="https://github.com/blueraai/universal-intelligence/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/blueraai/universal-intelligence.svg?color=00bf48"></a>
    <a href="https://discord.gg/7g9SrEc5yT"><img alt="Discord" src="https://img.shields.io/badge/Join-Discord-7289DA?logo=discord&logoColor=white&color=4911ff"></a>
</p>

> Safer rules and smarter toolkit so Claude Code does not accidentally set the world on fire trying to help 🔥

> [!WARNING]
> While `clauder` helps setting generic guardrails, these are **insufficient to autonomously ensure correctness and safety**. `clauder` is solely meant as a safety net and toolset, and *assumes co-supervision by a human in the loop*.

**Bluera Inc.** https://bluera.ai

## Overview

<details>
<summary><strong style="display: inline; cursor: pointer; margin: 0; padding: 0;">📻 Prefer audio?</strong></summary>
<br>


https://github.com/user-attachments/assets/4de6c270-7b45-497a-80a2-3018d1217168


</details>


This repository contains a comprehensive Claude Code configuration that provides advanced toolkits, safety mechanisms, logging, and best practices for AI-assisted development. Clauder includes:

**🔒 Security & Safety**
- Multi-layered secret detection and prevention
- File protection with immutable and ignore patterns
- Human-in-the-loop approval for sensitive operations
- Git protection against destructive operations
- Environment variable and sensitive data protection

**🔎 Logging & Monitoring**
- Comprehensive audit trail with SQLite database
- Real-time bash command and MCP tool logging
- Web-based tracer app for live monitoring
- Pre and post-operation validation and logging

**⚡ Workflow Automation**
- Automatic git checkpoints before sessions
- Documentation enforcement (HISTORY.md, SPECIFICATIONS.md)
- Audio feedback for task completion
- Automated backup and update management

**🛠️ Advanced Toolset**
- Custom commands for external AI consultation (`/consult`)
- Sub-agent creation and management (`/spawn`)
- Code review automation (`/review`)
- Intelligent agent recruitment (`/recruit`)

**🎯 Domain-Specific Expansion Packs**
- **67 specialized agents** across 8 domains
- **Frontend Development**: React, Vue, Angular, Svelte, TypeScript specialists
- **Backend Development**: API architects, database specialists, security experts
- **Data Science**: ML engineers, data scientists, visualization specialists
- **AI Development**: OpenAI, LangChain, RAG, and LLM security specialists
- **Infrastructure**: Cloud architects, DevOps engineers, SRE specialists
- **Game Development**: Mechanics designers, performance optimizers, audio specialists
- **Desktop Development**: Electron, Tauri, Flutter desktop specialists
- **General Software**: System architects, UX researchers, QA strategists

**💡 Smart Integration**
- Automatic MCP tool detection and utilization
- Automated Clauder updates
- Claude configuration backups and rollback support
- On-Demand expansion packs

Clauder is designed as a safety-first configuration that provides a robust foundation for AI-assisted development while maintaining human oversight and preventing common security pitfalls.

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

This will copy the `.claude` configuration to your project.

Clauder's configuration will automatically:

- Create checkpoint commits before each session
- Protect sensitive files and directories (see `.claude/.ignore` and `.claude/.immutable`)
- Log all actions for live monitoring, or auditing purposes (see `.claude/logs`)
- Enforce history and specifications tracking as you interact with Claude Code (see `HISTORY.md`, `SPECIFICATIONS.md`)
- Provides general guidelines/rules to Claude (see `.claude/rules.md`; Never guaranteed, but does help steering it; Do not solely rely on instructions for policing or workflows)
- Provide audio feedback on completion (optional, supports mac, linux experimental; enabled in `.claude/preferences.md`)
- Define custom commands for advanced workflows (e.g. `/consult` to consult a third party model for specific tasks, `/spawn` to create task specific agents, `/recruit` to recruit relevant agents for your project and needs, `/review` for a general review)
   - *Required MCP servers detailed below.*
- Define custom agents to help the main instance achieve specific tasks

> **Domain specific *expansion packs* available** (including agents, commands, hooks and configurations - see below)


#### How to start a Claude session

> [!IMPORTANT]
> **Opening Claude without interacting is sufficient to index and learn all secrets in the directory. Never keep secrets such as `.env` in the project directory.**
>
> If secrets have been indexed or read by an AI such as Claude, you should consider removing them from the project, invalidating them and renewing them. Production secrets should be stored in a secure vault, unreadable by AI. Keeping secrets out of the working directory prevents auto-indexing, but does not prevent Claude from finding ways to access them through running commands or calling tools. Clauder will try to prevent leaking secrets, potentially destructive, or unrecoverable actions, by detecting unsafe actions and requesting a Human in the loop, but none of it is bulletproof.
>
> **Please make sure to supervise your AI's actions as you grant it access to sensitive or critical systems. It cannot be trusted and will inadvertently make unrecoverable mistakes, which may critically impair the company and its production services. Backup your systems, and sandbox as much as possible through restrictive AI-level access control.** You are responsible for your AI's actions, as you are when using any other tool, or when managing a team.
>
> Prefer closer, slower supervision when working on root/core nodes in your project. Equally, allow faster, lower supervision for faster iterations when working on leaf nodes, or when prototyping.

Once you familiarize yourself with the above, and set your forbidden paths in `.claude/.ignore`, you may start a new Claude Code session with Clauder security checks using:

```bash
clauder
```
> ☕ **`clauder` includes security features, auto-updates, and configuration backups**. All Claude Code arguments supported (e.g. `--continue` to recall the last session)

In Claude, type:
```
/rules
```

This will define the mandatory guidelines for Claude Code.

> [!TIP]
> - If your project includes a `HISTORY.md` file at root level, `clauder` will enforce keeping a history of requests and actions taken, and use it to reason about the next action to take. Comprehensive history tracking may take time.
> - If your project includes a `SPECIFICATIONS.md` file at root level, `clauder` will enforce keeping an updated list of specifications as it takes actions, and use it to reason about the next action to take. When writing code manually, you may ask `clauder` to read the git diffs and backfill the specifications file.  Comprehensive specifications tracking may take time.
> - Define your secret files and folders in `.claude/.ignore` so `clauder` can guard them from being read/written.
> - Define your read-only files and folders in `.claude/.immutable` so `clauder` can guard them from being overwritten.
> - Exclude safe configuration files and folders in `.claude/.exclude_security_checks` so `clauder` can ommit them from safety checks (e.g. secret detection).
> - In `.gitignore`, exclude `.claude/logs`, `.claude/.tmp`, and `.claude-backup` for cleaner commits.
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

> [!TIP]
> Best practices:
> - **Tailor agents to your specific project and needs**, as you would when recruiting people.
> - **Limit the number of agents, prefer smaller teams with clear separation of ownership/expertise.** Lesser communication and orchestration loss.
> - **Leave all core coding to the main Claude instance, and consult other specialized agents for review or unrelated/leaf tasks.** Agents have their own context and do not know about the general history and reasoning for how and why things were done a certain way, or what other agents have said. Relying on communication greatly degrades the signal and often leads to breakage or unintended side effects. These personas are not better at coding than the main instance, they run the same model and backend orchestration. They are good at prioritizing / directing attention to specific areas - which is particularly useful for review, consultation, and leaf-type activities (as opposed to core parts). **Prefer one chef, with a few very good advisors, than too many chefs or too many advisors.**

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

#### Expansion packs (beta)

`clauder` also provides **ready-made agents** for various development projects, **optionally installable as *expansion packs***.

##### Installation

```sh
clauder_activate --expansions <expansion_name> <expansion_name>

# e.g.
# clauder_activate --expansions general-software-dev frontend-dev
```
> Expansions remain installed and auto-updated until `.claude` is removed.

##### Usage 

**All agents are automatically called by the main Claude instance when relevant, for advisory purposes.**

If you'd like to query a sub-agent directly (advisory only by design):

```sh
/task <agent_name> "<query>"

# e.g.
#  /task system-architecture-consultant "Analyze the current system architecture..."
#  /task ux-research-specialist "Research user experience patterns for..."
#  /task qa-strategy-specialist "Develop testing strategy for..."
```

Refer to the expansion details for dedicated hooks and commands.

##### Uninstall

```sh
# Important: backup your configuration before resetting it
rm -rf ./.claude && clauder_activate
```
> If you'd like a more surgical approach, you may delete the corresponding `.claude/.expansion_packs` entry and remove the corresponding agents, commands, hooks and settings for that expansion.

##### Available expansion packs

---
**Frontend Development** (`frontend-dev`)

- Agents 
   - `react-specialist` - Expert consultant for React ecosystem development, providing code review, architecture guidance, and best practices recommendations
   - `vue-specialist` - Specialized consultant for Vue.js development, offering architectural guidance and Vue ecosystem best practices
   - `angular-specialist` - Expert consultant for Angular development, providing framework-specific guidance and architectural recommendations
   - `svelte-specialist` - Specialized consultant for Svelte development, offering modern reactive framework guidance and optimization strategies
   - `typescript-specialist` - Expert consultant for TypeScript implementation, providing type safety guidance and advanced type system recommendations
   - `css-architect` - Specialized consultant for CSS architecture, offering design system guidance and styling best practices
   - `frontend-performance-optimizer` - Expert consultant for frontend performance optimization, providing bundle analysis and rendering optimization strategies
   - `accessibility-specialist` - Specialized consultant for web accessibility (a11y), offering WCAG compliance guidance and inclusive design recommendations
   - `security-reviewer` - Expert consultant for frontend security, providing vulnerability assessment and security best practices
   - `build-engineer` - Specialized consultant for frontend build systems, offering bundler optimization and deployment pipeline guidance
- Commands / Hooks / Configuration
   - N/A

---
**Backend Development** (`backend-dev`)

- Agents 
   - `api-architect` - Expert consultant for REST/GraphQL API design, microservices architecture, and API governance
   - `database-architect` - Specialized consultant for database design, offering schema optimization and data modeling strategies
   - `auth-specialist` - Expert consultant for authentication and authorization systems, providing security pattern guidance
   - `caching-specialist` - Specialized consultant for caching strategies, offering performance optimization and cache management guidance
   - `messaging-specialist` - Expert consultant for message queues and event-driven architectures, providing distributed system guidance
   - `observability-engineer` - Specialized consultant for monitoring and observability, offering logging, metrics, and tracing strategies
   - `backend-security-specialist` - Expert consultant for backend security, providing vulnerability assessment and security hardening guidance
   - `backend-testing-specialist` - Specialized consultant for backend testing strategies, offering test architecture and quality assurance guidance
   - `serverless-specialist` - Expert consultant for serverless architectures, providing cloud-native development and function optimization guidance
- Commands / Hooks / Configuration
   - N/A

---
**Data Science** (`data-science`)

- Agents 
   - `data-scientist` - Expert consultant for data analysis and statistical modeling, providing insights and analytical strategy guidance
   - `data-engineer` - Specialized consultant for data pipeline architecture, offering ETL optimization and data infrastructure guidance
   - `ml-engineer` - Expert consultant for machine learning implementation, providing model deployment and ML pipeline guidance
   - `data-visualization-specialist` - Specialized consultant for data visualization, offering chart design and interactive dashboard guidance
   - `analytics-engineer` - Expert consultant for analytics implementation, providing tracking strategy and data analysis guidance
   - `data-quality-engineer` - Specialized consultant for data quality assurance, offering validation strategies and data governance guidance
   - `statistical-consultant` - Expert consultant for statistical analysis, providing experimental design and hypothesis testing guidance
   - `ml-ethics-advisor` - Specialized consultant for AI ethics and responsible ML, offering bias detection and fairness assessment guidance
- Commands / Hooks / Configuration
   - N/A

---
**AI Development** (`ai-dev`)

- Agents 
   - `openai-api-specialist` - Expert consultant for OpenAI API integration, providing model selection and prompt engineering guidance
   - `openrouter-specialist` - Specialized consultant for OpenRouter integration, offering multi-model API strategy and cost optimization guidance
   - `langchain-specialist` - Expert consultant for LangChain framework, providing chain design and agent development guidance
   - `langgraph-specialist` - Specialized consultant for LangGraph orchestration, offering workflow design and state management guidance
   - `transformers-specialist` - Expert consultant for Hugging Face Transformers, providing model fine-tuning and deployment guidance
   - `vllm-specialist` - Specialized consultant for vLLM inference optimization, offering high-performance model serving guidance
   - `unsloth-specialist` - Expert consultant for Unsloth fine-tuning, providing efficient model training and optimization guidance
   - `rag-specialist` - Specialized consultant for Retrieval-Augmented Generation, offering knowledge base design and retrieval optimization guidance
   - `conversational-ai-specialist` - Expert consultant for conversational AI systems, providing chatbot design and dialogue management guidance
   - `agentic-orchestration-specialist` - Specialized consultant for multi-agent systems, offering agent coordination and workflow orchestration guidance
   - `agent-observability-specialist` - Expert consultant for AI agent monitoring, providing performance tracking and debugging guidance
   - `agent-cost-specialist` - Specialized consultant for AI cost optimization, offering token usage analysis and cost management strategies
   - `mcp-specialist` - Expert consultant for Model Context Protocol, providing tool integration and MCP server development guidance
   - `llm-security-specialist` - Specialized consultant for LLM security, offering prompt injection protection and AI safety guidance
- Commands / Hooks / Configuration
   - N/A

---
**Infrastructure** (`infrastructure`)

- Agents 
   - `cloud-infrastructure-architect` - Expert consultant for cloud infrastructure design, providing multi-cloud strategy and resource optimization guidance
   - `container-orchestration-specialist` - Specialized consultant for Kubernetes and Docker, offering containerization strategy and orchestration guidance
   - `devops-pipeline-engineer` - Expert consultant for CI/CD pipeline design, providing automation strategy and deployment optimization guidance
   - `site-reliability-engineer` - Specialized consultant for SRE practices, offering reliability engineering and incident response guidance
   - `infrastructure-security-specialist` - Expert consultant for infrastructure security, providing security hardening and compliance guidance
   - `infrastructure-cost-optimizer` - Specialized consultant for cloud cost optimization, offering resource management and cost analysis guidance
   - `database-infrastructure-specialist` - Expert consultant for database infrastructure, providing scaling strategies and performance optimization guidance
   - `network-architecture-specialist` - Specialized consultant for network design, offering connectivity strategy and security architecture guidance
- Commands / Hooks / Configuration
   - N/A

---
**Game Development** (`game-dev`)

- Agents 
   - `game-mechanics-designer` - Expert consultant for game mechanics design, providing gameplay balance and system design guidance
   - `game-state-manager` - Specialized consultant for game state management, offering save systems and progression tracking guidance
   - `game-performance-specialist` - Expert consultant for game performance optimization, providing rendering optimization and frame rate guidance
   - `game-input-specialist` - Specialized consultant for game input systems, offering control scheme design and input handling guidance
   - `game-audio-designer` - Expert consultant for game audio design, providing sound implementation and audio engine guidance
   - `level-design-architect` - Specialized consultant for level design, offering world building and spatial design guidance
   - `game-visual-designer` - Expert consultant for game visual design, providing art direction and visual asset optimization guidance
- Commands / Hooks / Configuration
   - N/A

---
**Desktop Development** (`desktop-dev`)

- Agents 
   - `electron-specialist` - Expert consultant for Electron applications, providing cross-platform desktop app development guidance
   - `tauri-specialist` - Specialized consultant for Tauri framework, offering Rust-based desktop app development guidance
   - `flutter-desktop-specialist` - Expert consultant for Flutter desktop development, providing cross-platform UI framework guidance
   - `pwa-specialist` - Specialized consultant for Progressive Web Apps, offering web-to-desktop conversion and offline capability guidance
   - `neutralino-specialist` - Expert consultant for Neutralino framework, providing lightweight desktop app development guidance
   - `lynx-specialist` - Specialized consultant for Lynx framework, offering Tauri alternative desktop development guidance
   - `desktop-security-specialist` - Expert consultant for desktop application security, providing security hardening and vulnerability assessment guidance
- Commands / Hooks / Configuration
   - N/A

---
**General Software Development** (`general-software-dev`)

- Agents 
   - `system-architecture-consultant` - Expert consultant for system architecture design, providing scalable architecture and design pattern guidance
   - `ux-research-specialist` - Specialized consultant for user experience research, offering usability testing and user-centered design guidance
   - `qa-strategy-specialist` - Expert consultant for quality assurance strategy, providing testing methodology and quality management guidance
- Commands / Hooks / Configuration
   - N/A

---

##### Creating expansion packs

Clone `.claude-expansion-packs/example` to get started. The folder name is the name of your expansion. Define your custom `agents`, `commands`, `hooks` (set up in `settings.json`), and configurations.

> Disclaimer: Remember to be specific, to prevent conflicts with the base `clauder` setup.

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
│   └── hooks/                          # Python and shell hooks
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
├── .claude-expansion-packs/              # Expansion packs directory
│   ├── frontend-dev/                     # Frontend development expansion
│   │   ├── agents/                       # Frontend specialist agents
│   │   │   ├── react-specialist.md       # React ecosystem consultant
│   │   │   ├── vue-specialist.md         # Vue.js development consultant
│   │   │   ├── angular-specialist.md     # Angular development consultant
│   │   │   ├── svelte-specialist.md      # Svelte development consultant
│   │   │   ├── typescript-specialist.md  # TypeScript implementation consultant
│   │   │   ├── css-architect.md          # CSS architecture consultant
│   │   │   ├── frontend-performance-optimizer.md # Performance optimization consultant
│   │   │   ├── accessibility-specialist.md # Web accessibility consultant
│   │   │   ├── security-reviewer.md      # Frontend security consultant
│   │   │   └── build-engineer.md         # Build systems consultant
│   │   ├── settings.json                 # Frontend-specific settings
│   │   ├── preferences.json              # Frontend-specific preferences
│   │   ├── .ignore                       # Frontend-specific ignore patterns
│   │   ├── .immutable                    # Frontend-specific immutable files
│   │   ├── .exclude_security_checks      # Frontend-specific security exclusions
│   │   └── requirements-frontend-dev-expansion.md # Frontend requirements
│   ├── backend-dev/                      # Backend development expansion
│   │   ├── agents/                       # Backend specialist agents
│   │   │   ├── api-architect.md          # API design consultant
│   │   │   ├── database-architect.md     # Database design consultant
│   │   │   ├── auth-specialist.md        # Authentication consultant
│   │   │   ├── caching-specialist.md     # Caching strategies consultant
│   │   │   ├── messaging-specialist.md   # Message queues consultant
│   │   │   ├── observability-engineer.md # Monitoring consultant
│   │   │   ├── backend-security-specialist.md # Backend security consultant
│   │   │   ├── backend-testing-specialist.md # Testing strategies consultant
│   │   │   └── serverless-specialist.md  # Serverless architecture consultant
│   │   ├── settings.json                 # Backend-specific settings
│   │   ├── preferences.json              # Backend-specific preferences
│   │   ├── .ignore                       # Backend-specific ignore patterns
│   │   ├── .immutable                    # Backend-specific immutable files
│   │   ├── .exclude_security_checks      # Backend-specific security exclusions
│   │   └── requirements-backend-dev-expansion.md # Backend requirements
│   ├── data-science/                     # Data science expansion
│   │   ├── agents/                       # Data science specialist agents
│   │   │   ├── data-scientist.md         # Data analysis consultant
│   │   │   ├── data-engineer.md          # Data pipeline consultant
│   │   │   ├── ml-engineer.md            # Machine learning consultant
│   │   │   ├── data-visualization-specialist.md # Data visualization consultant
│   │   │   ├── analytics-engineer.md     # Analytics implementation consultant
│   │   │   ├── data-quality-engineer.md  # Data quality consultant
│   │   │   ├── statistical-consultant.md # Statistical analysis consultant
│   │   │   └── ml-ethics-advisor.md      # AI ethics consultant
│   │   ├── settings.json                 # Data science-specific settings
│   │   ├── preferences.json              # Data science-specific preferences
│   │   ├── .ignore                       # Data science-specific ignore patterns
│   │   ├── .immutable                    # Data science-specific immutable files
│   │   ├── .exclude_security_checks      # Data science-specific security exclusions
│   │   └── requirements-data-science-expansion.md # Data science requirements
│   ├── ai-dev/                           # AI development expansion
│   │   ├── agents/                       # AI development specialist agents
│   │   │   ├── openai-api-specialist.md  # OpenAI API consultant
│   │   │   ├── openrouter-specialist.md  # OpenRouter consultant
│   │   │   ├── langchain-specialist.md   # LangChain consultant
│   │   │   ├── langgraph-specialist.md   # LangGraph consultant
│   │   │   ├── transformers-specialist.md # Hugging Face consultant
│   │   │   ├── vllm-specialist.md        # vLLM consultant
│   │   │   ├── unsloth-specialist.md     # Unsloth consultant
│   │   │   ├── rag-specialist.md         # RAG consultant
│   │   │   ├── conversational-ai-specialist.md # Conversational AI consultant
│   │   │   ├── agentic-orchestration-specialist.md # Multi-agent consultant
│   │   │   ├── agent-observability-specialist.md # Agent monitoring consultant
│   │   │   ├── agent-cost-specialist.md  # AI cost optimization consultant
│   │   │   ├── mcp-specialist.md         # MCP consultant
│   │   │   └── llm-security-specialist.md # LLM security consultant
│   │   ├── settings.json                 # AI development-specific settings
│   │   ├── preferences.json              # AI development-specific preferences
│   │   ├── .ignore                       # AI development-specific ignore patterns
│   │   ├── .immutable                    # AI development-specific immutable files
│   │   ├── .exclude_security_checks      # AI development-specific security exclusions
│   │   └── requirements-ai-dev-expansion.md # AI development requirements
│   ├── infrastructure/                   # Infrastructure expansion
│   │   ├── agents/                       # Infrastructure specialist agents
│   │   │   ├── cloud-infrastructure-architect.md # Cloud infrastructure consultant
│   │   │   ├── container-orchestration-specialist.md # Kubernetes consultant
│   │   │   ├── devops-pipeline-engineer.md # CI/CD consultant
│   │   │   ├── site-reliability-engineer.md # SRE consultant
│   │   │   ├── infrastructure-security-specialist.md # Infrastructure security consultant
│   │   │   ├── infrastructure-cost-optimizer.md # Cost optimization consultant
│   │   │   ├── database-infrastructure-specialist.md # Database infrastructure consultant
│   │   │   └── network-architecture-specialist.md # Network design consultant
│   │   ├── settings.json                 # Infrastructure-specific settings
│   │   ├── preferences.json              # Infrastructure-specific preferences
│   │   ├── .ignore                       # Infrastructure-specific ignore patterns
│   │   ├── .immutable                    # Infrastructure-specific immutable files
│   │   ├── .exclude_security_checks      # Infrastructure-specific security exclusions
│   │   └── requirements-infrastructure-expansion.md # Infrastructure requirements
│   ├── game-dev/                         # Game development expansion
│   │   ├── agents/                       # Game development specialist agents
│   │   │   ├── game-mechanics-designer.md # Game mechanics consultant
│   │   │   ├── game-state-manager.md     # Game state management consultant
│   │   │   ├── game-performance-specialist.md # Game performance consultant
│   │   │   ├── game-input-specialist.md  # Game input systems consultant
│   │   │   ├── game-audio-designer.md    # Game audio consultant
│   │   │   ├── level-design-architect.md # Level design consultant
│   │   │   └── game-visual-designer.md   # Game visual design consultant
│   │   ├── settings.json                 # Game development-specific settings
│   │   ├── preferences.json              # Game development-specific preferences
│   │   ├── .ignore                       # Game development-specific ignore patterns
│   │   ├── .immutable                    # Game development-specific immutable files
│   │   ├── .exclude_security_checks      # Game development-specific security exclusions
│   │   └── requirements-game-dev-expansion.md # Game development requirements
│   ├── desktop-dev/                      # Desktop development expansion
│   │   ├── agents/                       # Desktop development specialist agents
│   │   │   ├── electron-specialist.md    # Electron consultant
│   │   │   ├── tauri-specialist.md       # Tauri consultant
│   │   │   ├── flutter-desktop-specialist.md # Flutter desktop consultant
│   │   │   ├── pwa-specialist.md         # PWA consultant
│   │   │   ├── neutralino-specialist.md  # Neutralino consultant
│   │   │   ├── lynx-specialist.md        # Lynx consultant
│   │   │   └── desktop-security-specialist.md # Desktop security consultant
│   │   ├── settings.json                 # Desktop development-specific settings
│   │   ├── preferences.json              # Desktop development-specific preferences
│   │   ├── .ignore                       # Desktop development-specific ignore patterns
│   │   ├── .immutable                    # Desktop development-specific immutable files
│   │   ├── .exclude_security_checks      # Desktop development-specific security exclusions
│   │   └── requirements-desktop-dev-expansion.md # Desktop development requirements
│   ├── general-software-dev/             # General software development expansion
│   │   ├── agents/                       # General software development specialist agents
│   │   │   ├── system-architecture-consultant.md # System architecture consultant
│   │   │   ├── ux-research-specialist.md # UX research consultant
│   │   │   └── qa-strategy-specialist.md # QA strategy consultant
│   │   ├── settings.json                 # General software development-specific settings
│   │   ├── preferences.json              # General software development-specific preferences
│   │   ├── .ignore                       # General software development-specific ignore patterns
│   │   ├── .immutable                    # General software development-specific immutable files
│   │   ├── .exclude_security_checks      # General software development-specific security exclusions
│   │   └── requirements-general-software-dev-expansion.md # General software development requirements
│   └── example/                          # Example expansion pack template
│       ├── agents/                       # Example agents directory
│       ├── settings.json                 # Example settings template
│       ├── preferences.json              # Example preferences template
│       ├── .ignore                       # Example ignore patterns template
│       ├── .immutable                    # Example immutable files template
│       ├── .exclude_security_checks      # Example security exclusions template
│       └── requirements-example-expansion.md # Example requirements template
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
# Make hooks executable
chmod +x .claude/hooks/*.py
chmod +x .claude/hooks/*.sh
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

**.claude/*: [Errno 2] No such file or directory**
```bash
# Claude ran 'cd' and moved to a directory where it cannot find its '.claude' configuration.
# Due to hooks needing to be be set in this '.claude' configuration, it will not be able to find them and will error out when trying to 'cd' back.

# To resolve, stop Claude and run:
clauder --continue 
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

## Thanks

This project is powered by [claude-code](https://github.com/anthropics/claude-code), an intelligent IDE made by [Anthropic](https://github.com/anthropics).

## Support

This software is open source, free for everyone, and lives on thanks to the community's support ☕

If you'd like to support to `clauder` here are a few ways to do so:

- ⭐ Consider leaving a star on this repository to support our team & help with visibility
- 👽 Tell your friends and colleagues
- 📰 Support this project on social medias (e.g. LinkedIn, Youtube, Medium, Reddit)
- ✅ Use `clauder` to make cool things
- 💪 Create your very own `clauder` expansion packs
- 💡 Help surfacing/resolving issues
- 💭 Help shape the next `clauder` versions
- 🔧 Help maintain, test, enhance `clauder`
- ✉️ Email us security concerns
- ❤️ Sponsor this project on Github
- 🤝 [Partner with Bluera](mailto:contact@bluera.ai)

## License

Apache 2.0 - Bluera Inc.

> https://bluera.ai

---

**Remember**: This is a safety-first configuration. Always review changes before applying them to production systems. The AI assistant is a tool that requires supervision and should not be trusted with critical systems without proper oversight.
