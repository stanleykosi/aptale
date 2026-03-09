Directory structure:
└── docs/
    ├── index.md
    ├── developer-guide/
    │   ├── _category_.json
    │   ├── adding-tools.md
    │   ├── architecture.md
    │   ├── contributing.md
    │   ├── creating-skills.md
    │   └── environments.md
    ├── getting-started/
    │   ├── _category_.json
    │   ├── installation.md
    │   ├── quickstart.md
    │   └── updating.md
    ├── reference/
    │   ├── _category_.json
    │   ├── cli-commands.md
    │   └── environment-variables.md
    └── user-guide/
        ├── _category_.json
        ├── cli.md
        ├── configuration.md
        ├── security.md
        ├── sessions.md
        ├── features/
        │   ├── _category_.json
        │   ├── batch-processing.md
        │   ├── browser.md
        │   ├── code-execution.md
        │   ├── context-files.md
        │   ├── cron.md
        │   ├── delegation.md
        │   ├── honcho.md
        │   ├── hooks.md
        │   ├── image-generation.md
        │   ├── mcp.md
        │   ├── memory.md
        │   ├── personality.md
        │   ├── provider-routing.md
        │   ├── rl-training.md
        │   ├── skills.md
        │   ├── tools.md
        │   ├── tts.md
        │   └── vision.md
        └── messaging/
            ├── _category_.json
            ├── discord.md
            ├── homeassistant.md
            ├── index.md
            ├── slack.md
            ├── telegram.md
            └── whatsapp.md

================================================
FILE: website/docs/index.md
================================================
---
slug: /
sidebar_position: 0
title: "Hermes Agent Documentation"
description: "The self-improving AI agent built by Nous Research. A built-in learning loop that creates skills from experience, improves them during use, and remembers across sessions."
hide_table_of_contents: true
---

# Hermes Agent

The self-improving AI agent built by [Nous Research](https://nousresearch.com). The only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, and builds a deepening model of who you are across sessions.

<div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap'}}>
  <a href="/docs/getting-started/installation" style={{display: 'inline-block', padding: '0.6rem 1.2rem', backgroundColor: '#FFD700', color: '#07070d', borderRadius: '8px', fontWeight: 600, textDecoration: 'none'}}>Get Started →</a>
  <a href="https://github.com/NousResearch/hermes-agent" style={{display: 'inline-block', padding: '0.6rem 1.2rem', border: '1px solid rgba(255,215,0,0.2)', borderRadius: '8px', textDecoration: 'none'}}>View on GitHub</a>
</div>

## What is Hermes Agent?

It's not a coding copilot tethered to an IDE or a chatbot wrapper around a single API. It's an **autonomous agent** that gets more capable the longer it runs. It lives wherever you put it — a $5 VPS, a GPU cluster, or serverless infrastructure (Daytona, Modal) that costs nearly nothing when idle. Talk to it from Telegram while it works on a cloud VM you never SSH into yourself. It's not tied to your laptop.

## Quick Links

| | |
|---|---|
| 🚀 **[Installation](/docs/getting-started/installation)** | Install in 60 seconds on Linux, macOS, or WSL2 |
| 📖 **[Quickstart Tutorial](/docs/getting-started/quickstart)** | Your first conversation and key features to try |
| ⚙️ **[Configuration](/docs/user-guide/configuration)** | Config file, providers, models, and options |
| 💬 **[Messaging Gateway](/docs/user-guide/messaging)** | Set up Telegram, Discord, Slack, or WhatsApp |
| 🔧 **[Tools & Toolsets](/docs/user-guide/features/tools)** | 40+ built-in tools and how to configure them |
| 🧠 **[Memory System](/docs/user-guide/features/memory)** | Persistent memory that grows across sessions |
| 📚 **[Skills System](/docs/user-guide/features/skills)** | Procedural memory the agent creates and reuses |
| 🔌 **[MCP Integration](/docs/user-guide/features/mcp)** | Connect to any MCP server for extended capabilities |
| 📄 **[Context Files](/docs/user-guide/features/context-files)** | Project context files that shape every conversation |
| 🔒 **[Security](/docs/user-guide/security)** | Command approval, authorization, container isolation |
| 🏗️ **[Architecture](/docs/developer-guide/architecture)** | How it works under the hood |
| 🤝 **[Contributing](/docs/developer-guide/contributing)** | Development setup and PR process |

## Key Features

- **A closed learning loop** — Agent-curated memory with periodic nudges, autonomous skill creation, skill self-improvement during use, FTS5 cross-session recall with LLM summarization, and [Honcho](https://github.com/plastic-labs/honcho) dialectic user modeling
- **Runs anywhere, not just your laptop** — 6 terminal backends: local, Docker, SSH, Daytona, Singularity, Modal. Daytona and Modal offer serverless persistence — your environment hibernates when idle, costing nearly nothing
- **Lives where you do** — CLI, Telegram, Discord, Slack, WhatsApp, all from one gateway
- **Built by model trainers** — Created by [Nous Research](https://nousresearch.com), the lab behind Hermes, Nomos, and Psyche. Works with [Nous Portal](https://portal.nousresearch.com), [OpenRouter](https://openrouter.ai), OpenAI, or any endpoint
- **Scheduled automations** — Built-in cron with delivery to any platform
- **Delegates & parallelizes** — Spawn isolated subagents for parallel workstreams. Programmatic Tool Calling via `execute_code` collapses multi-step pipelines into single inference calls
- **Open standard skills** — Compatible with [agentskills.io](https://agentskills.io). Skills are portable, shareable, and community-contributed via the Skills Hub
- **Full web control** — Search, extract, browse, vision, image generation, TTS
- **MCP support** — Connect to any MCP server for extended tool capabilities
- **Research-ready** — Batch processing, trajectory export, RL training with Atropos. Built by [Nous Research](https://nousresearch.com) — the lab behind Hermes, Nomos, and Psyche models



================================================
FILE: website/docs/developer-guide/_category_.json
================================================
{
  "label": "Developer Guide",
  "position": 3,
  "link": {
    "type": "generated-index",
    "description": "Contribute to Hermes Agent — architecture, tools, skills, and more."
  }
}



================================================
FILE: website/docs/developer-guide/adding-tools.md
================================================
---
sidebar_position: 2
title: "Adding Tools"
description: "How to add a new tool to Hermes Agent — schemas, handlers, registration, and toolsets"
---

# Adding Tools

Before writing a tool, ask yourself: **should this be a [skill](creating-skills.md) instead?**

Make it a **Skill** when the capability can be expressed as instructions + shell commands + existing tools (arXiv search, git workflows, Docker management, PDF processing).

Make it a **Tool** when it requires end-to-end integration with API keys, custom processing logic, binary data handling, or streaming (browser automation, TTS, vision analysis).

## Overview

Adding a tool touches **3 files**:

1. **`tools/your_tool.py`** — handler, schema, check function, `registry.register()` call
2. **`toolsets.py`** — add tool name to `_HERMES_CORE_TOOLS` (or a specific toolset)
3. **`model_tools.py`** — add `"tools.your_tool"` to the `_discover_tools()` list

## Step 1: Create the Tool File

Every tool file follows the same structure:

```python
# tools/weather_tool.py
"""Weather Tool -- look up current weather for a location."""

import json
import os
import logging

logger = logging.getLogger(__name__)


# --- Availability check ---

def check_weather_requirements() -> bool:
    """Return True if the tool's dependencies are available."""
    return bool(os.getenv("WEATHER_API_KEY"))


# --- Handler ---

def weather_tool(location: str, units: str = "metric") -> str:
    """Fetch weather for a location. Returns JSON string."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not configured"})
    try:
        # ... call weather API ...
        return json.dumps({"location": location, "temp": 22, "units": units})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Schema ---

WEATHER_SCHEMA = {
    "name": "weather",
    "description": "Get current weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates (e.g. 'London' or '51.5,-0.1')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (default: metric)",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}


# --- Registration ---

from tools.registry import registry

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool(
        location=args.get("location", ""),
        units=args.get("units", "metric")),
    check_fn=check_weather_requirements,
    requires_env=["WEATHER_API_KEY"],
)
```

### Key Rules

:::danger Important
- Handlers **MUST** return a JSON string (via `json.dumps()`), never raw dicts
- Errors **MUST** be returned as `{"error": "message"}`, never raised as exceptions
- The `check_fn` is called when building tool definitions — if it returns `False`, the tool is silently excluded
- The `handler` receives `(args: dict, **kwargs)` where `args` is the LLM's tool call arguments
:::

## Step 2: Add to a Toolset

In `toolsets.py`, add the tool name:

```python
# If it should be available on all platforms (CLI + messaging):
_HERMES_CORE_TOOLS = [
    ...
    "weather",  # <-- add here
]

# Or create a new standalone toolset:
"weather": {
    "description": "Weather lookup tools",
    "tools": ["weather"],
    "includes": []
},
```

## Step 3: Add Discovery Import

In `model_tools.py`, add the module to the `_discover_tools()` list:

```python
def _discover_tools():
    _modules = [
        ...
        "tools.weather_tool",  # <-- add here
    ]
```

This import triggers the `registry.register()` call at the bottom of your tool file.

## Async Handlers

If your handler needs async code, mark it with `is_async=True`:

```python
async def weather_tool_async(location: str) -> str:
    async with aiohttp.ClientSession() as session:
        ...
    return json.dumps(result)

registry.register(
    name="weather",
    toolset="weather",
    schema=WEATHER_SCHEMA,
    handler=lambda args, **kw: weather_tool_async(args.get("location", "")),
    check_fn=check_weather_requirements,
    is_async=True,  # registry calls _run_async() automatically
)
```

The registry handles async bridging transparently — you never call `asyncio.run()` yourself.

## Handlers That Need task_id

Tools that manage per-session state receive `task_id` via `**kwargs`:

```python
def _handle_weather(args, **kw):
    task_id = kw.get("task_id")
    return weather_tool(args.get("location", ""), task_id=task_id)

registry.register(
    name="weather",
    ...
    handler=_handle_weather,
)
```

## Agent-Loop Intercepted Tools

Some tools (`todo`, `memory`, `session_search`, `delegate_task`) need access to per-session agent state. These are intercepted by `run_agent.py` before reaching the registry. The registry still holds their schemas, but `dispatch()` returns a fallback error if the intercept is bypassed.

## Optional: Setup Wizard Integration

If your tool requires an API key, add it to `hermes_cli/config.py`:

```python
OPTIONAL_ENV_VARS = {
    ...
    "WEATHER_API_KEY": {
        "description": "Weather API key for weather lookup",
        "prompt": "Weather API key",
        "url": "https://weatherapi.com/",
        "tools": ["weather"],
        "password": True,
    },
}
```

## Checklist

- [ ] Tool file created with handler, schema, check function, and registration
- [ ] Added to appropriate toolset in `toolsets.py`
- [ ] Discovery import added to `model_tools.py`
- [ ] Handler returns JSON strings, errors returned as `{"error": "..."}`
- [ ] Optional: API key added to `OPTIONAL_ENV_VARS` in `hermes_cli/config.py`
- [ ] Optional: Added to `toolset_distributions.py` for batch processing
- [ ] Tested with `hermes chat -q "Use the weather tool for London"`



================================================
FILE: website/docs/developer-guide/architecture.md
================================================
[Binary file]


================================================
FILE: website/docs/developer-guide/contributing.md
================================================
---
sidebar_position: 4
title: "Contributing"
description: "How to contribute to Hermes Agent — dev setup, code style, PR process"
---

# Contributing

Thank you for contributing to Hermes Agent! This guide covers setting up your dev environment, understanding the codebase, and getting your PR merged.

## Contribution Priorities

We value contributions in this order:

1. **Bug fixes** — crashes, incorrect behavior, data loss
2. **Cross-platform compatibility** — macOS, different Linux distros, WSL2
3. **Security hardening** — shell injection, prompt injection, path traversal
4. **Performance and robustness** — retry logic, error handling, graceful degradation
5. **New skills** — broadly useful ones (see [Creating Skills](creating-skills.md))
6. **New tools** — rarely needed; most capabilities should be skills
7. **Documentation** — fixes, clarifications, new examples

## Development Setup

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Git** | With `--recurse-submodules` support |
| **Python 3.10+** | uv will install it if missing |
| **uv** | Fast Python package manager ([install](https://docs.astral.sh/uv/)) |
| **Node.js 18+** | Optional — needed for browser tools and WhatsApp bridge |

### Clone and Install

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Create venv with Python 3.11
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# Install with all extras (messaging, cron, CLI menus, dev tools)
uv pip install -e ".[all,dev]"
uv pip install -e "./mini-swe-agent"
uv pip install -e "./tinker-atropos"

# Optional: browser tools
npm install
```

### Configure for Development

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# Add at minimum an LLM provider key:
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env
```

### Run

```bash
# Symlink for global access
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# Verify
hermes doctor
hermes chat -q "Hello"
```

### Run Tests

```bash
pytest tests/ -v
```

## Code Style

- **PEP 8** with practical exceptions (no strict line length enforcement)
- **Comments**: Only when explaining non-obvious intent, trade-offs, or API quirks
- **Error handling**: Catch specific exceptions. Use `logger.warning()`/`logger.error()` with `exc_info=True` for unexpected errors
- **Cross-platform**: Never assume Unix (see below)

## Cross-Platform Compatibility

Hermes officially supports Linux, macOS, and WSL2. Native Windows is **not supported**, but the codebase includes some defensive coding patterns to avoid hard crashes in edge cases. Key rules:

### 1. `termios` and `fcntl` are Unix-only

Always catch both `ImportError` and `NotImplementedError`:

```python
try:
    from simple_term_menu import TerminalMenu
    menu = TerminalMenu(options)
    idx = menu.show()
except (ImportError, NotImplementedError):
    # Fallback: numbered menu
    for i, opt in enumerate(options):
        print(f"  {i+1}. {opt}")
    idx = int(input("Choice: ")) - 1
```

### 2. File encoding

Some environments may save `.env` files in non-UTF-8 encodings:

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

### 3. Process management

`os.setsid()`, `os.killpg()`, and signal handling differ across platforms:

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.setsid
```

### 4. Path separators

Use `pathlib.Path` instead of string concatenation with `/`.

## Security Considerations

Hermes has terminal access. Security matters.

### Existing Protections

| Layer | Implementation |
|-------|---------------|
| **Sudo password piping** | Uses `shlex.quote()` to prevent shell injection |
| **Dangerous command detection** | Regex patterns in `tools/approval.py` with user approval flow |
| **Cron prompt injection** | Scanner blocks instruction-override patterns |
| **Write deny list** | Protected paths resolved via `os.path.realpath()` to prevent symlink bypass |
| **Skills guard** | Security scanner for hub-installed skills |
| **Code execution sandbox** | Child process runs with API keys stripped |
| **Container hardening** | Docker: all capabilities dropped, no privilege escalation, PID limits |

### Contributing Security-Sensitive Code

- Always use `shlex.quote()` when interpolating user input into shell commands
- Resolve symlinks with `os.path.realpath()` before access control checks
- Don't log secrets
- Catch broad exceptions around tool execution
- Test on all platforms if your change touches file paths or processes

## Pull Request Process

### Branch Naming

```
fix/description        # Bug fixes
feat/description       # New features
docs/description       # Documentation
test/description       # Tests
refactor/description   # Code restructuring
```

### Before Submitting

1. **Run tests**: `pytest tests/ -v`
2. **Test manually**: Run `hermes` and exercise the code path you changed
3. **Check cross-platform impact**: Consider macOS and different Linux distros
4. **Keep PRs focused**: One logical change per PR

### PR Description

Include:
- **What** changed and **why**
- **How to test** it
- **What platforms** you tested on
- Reference any related issues

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

| Type | Use for |
|------|---------|
| `fix` | Bug fixes |
| `feat` | New features |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Code restructuring |
| `chore` | Build, CI, dependency updates |

Scopes: `cli`, `gateway`, `tools`, `skills`, `agent`, `install`, `whatsapp`, `security`

Examples:
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
```

## Reporting Issues

- Use [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- Include: OS, Python version, Hermes version (`hermes version`), full error traceback
- Include steps to reproduce
- Check existing issues before creating duplicates
- For security vulnerabilities, please report privately

## Community

- **Discord**: [discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**: For design proposals and architecture discussions
- **Skills Hub**: Upload specialized skills and share with the community

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE).



================================================
FILE: website/docs/developer-guide/creating-skills.md
================================================
---
sidebar_position: 3
title: "Creating Skills"
description: "How to create skills for Hermes Agent — SKILL.md format, guidelines, and publishing"
---

# Creating Skills

Skills are the preferred way to add new capabilities to Hermes Agent. They're easier to create than tools, require no code changes to the agent, and can be shared with the community.

## Should it be a Skill or a Tool?

Make it a **Skill** when:
- The capability can be expressed as instructions + shell commands + existing tools
- It wraps an external CLI or API that the agent can call via `terminal` or `web_extract`
- It doesn't need custom Python integration or API key management baked into the agent
- Examples: arXiv search, git workflows, Docker management, PDF processing, email via CLI tools

Make it a **Tool** when:
- It requires end-to-end integration with API keys, auth flows, or multi-component configuration
- It needs custom processing logic that must execute precisely every time
- It handles binary data, streaming, or real-time events
- Examples: browser automation, TTS, vision analysis

## Skill Directory Structure

Bundled skills live in `skills/` organized by category. Official optional skills use the same structure in `optional-skills/`:

```
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # Required: main instructions
│       └── scripts/              # Optional: helper scripts
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

## SKILL.md Format

```markdown
---
name: my-skill
description: Brief description (shown in skill search results)
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # Optional — restrict to specific OS platforms
                                   #   Valid: macos, linux, windows
                                   #   Omit to load on all platforms (default)
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
---

# Skill Title

Brief intro.

## When to Use
Trigger conditions — when should the agent load this skill?

## Quick Reference
Table of common commands or API calls.

## Procedure
Step-by-step instructions the agent follows.

## Pitfalls
Known failure modes and how to handle them.

## Verification
How the agent confirms it worked.
```

### Platform-Specific Skills

Skills can restrict themselves to specific operating systems using the `platforms` field:

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders)
platforms: [macos, linux]     # macOS and Linux
platforms: [windows]          # Windows only
```

When set, the skill is automatically hidden from the system prompt, `skills_list()`, and slash commands on incompatible platforms. If omitted or empty, the skill loads on all platforms (backward compatible).

See `skills/apple/` for examples of macOS-only skills.

## Skill Guidelines

### No External Dependencies

Prefer stdlib Python, curl, and existing Hermes tools (`web_extract`, `terminal`, `read_file`). If a dependency is needed, document installation steps in the skill.

### Progressive Disclosure

Put the most common workflow first. Edge cases and advanced usage go at the bottom. This keeps token usage low for common tasks.

### Include Helper Scripts

For XML/JSON parsing or complex logic, include helper scripts in `scripts/` — don't expect the LLM to write parsers inline every time.

### Test It

Run the skill and verify the agent follows the instructions correctly:

```bash
hermes chat --toolsets skills -q "Use the X skill to do Y"
```

## Where Should the Skill Live?

Bundled skills (in `skills/`) ship with every Hermes install. They should be **broadly useful to most users**:

- Document handling, web research, common dev workflows, system administration
- Used regularly by a wide range of people

If your skill is official and useful but not universally needed (e.g., a paid service integration, a heavyweight dependency), put it in **`optional-skills/`** — it ships with the repo, is discoverable via `hermes skills browse` (labeled "official"), and installs with builtin trust.

If your skill is specialized, community-contributed, or niche, it's better suited for a **Skills Hub** — upload it to a registry and share it via `hermes skills install`.

## Publishing Skills

### To the Skills Hub

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### To a Custom Repository

Add your repo as a tap:

```bash
hermes skills tap add owner/repo
```

Users can then search and install from your repository.

## Security Scanning

All hub-installed skills go through a security scanner that checks for:

- Data exfiltration patterns
- Prompt injection attempts
- Destructive commands
- Shell injection

Trust levels:
- `builtin` — ships with Hermes (always trusted)
- `official` — from `optional-skills/` in the repo (builtin trust, no third-party warning)
- `trusted` — from openai/skills, anthropics/skills
- `community` — any findings = blocked unless `--force`



================================================
FILE: website/docs/developer-guide/environments.md
================================================
---
sidebar_position: 5
title: "Environments, Benchmarks & Data Generation"
description: "Building RL training environments, running evaluation benchmarks, and generating SFT data with the Hermes-Agent Atropos integration"
---

# Environments, Benchmarks & Data Generation

Hermes Agent includes a full environment framework that connects its tool-calling capabilities to the [Atropos](https://github.com/NousResearch/atropos) RL training framework. This enables three workflows:

1. **RL Training** — Train language models on multi-turn agentic tasks with GRPO
2. **Benchmarks** — Evaluate models on standardised agentic benchmarks
3. **Data Generation** — Generate SFT training data from agent rollouts

All three share the same core: an **environment** class that defines tasks, runs an agent loop, and scores the output.

:::tip Quick Links
- **Want to run benchmarks?** Jump to [Available Benchmarks](#available-benchmarks)
- **Want to train with RL?** See [RL Training Tools](/user-guide/features/rl-training) for the agent-driven interface, or [Running Environments](#running-environments) for manual execution
- **Want to create a new environment?** See [Creating Environments](#creating-environments)
:::

## Architecture

The environment system is built on a three-layer inheritance chain:

```
                     Atropos Framework
                 ┌───────────────────────┐
                 │       BaseEnv          │  (atroposlib)
                 │  - Server management   │
                 │  - Worker scheduling   │
                 │  - Wandb logging       │
                 │  - CLI (serve/process/ │
                 │    evaluate)           │
                 └───────────┬───────────┘
                             │ inherits
                 ┌───────────┴───────────┐
                 │  HermesAgentBaseEnv    │  environments/hermes_base_env.py
                 │  - Terminal backend    │
                 │  - Tool resolution     │
                 │  - Agent loop engine   │
                 │  - ToolContext         │
                 └───────────┬───────────┘
                             │ inherits
       ┌─────────────────────┼─────────────────────┐
       │                     │                      │
  TerminalTestEnv     HermesSweEnv     TerminalBench2EvalEnv
  (stack testing)    (SWE training)      (benchmark eval)
                                             │
                                    ┌────────┼────────┐
                                    │                  │
                              TBLiteEvalEnv     YCBenchEvalEnv
                             (fast benchmark)  (long-horizon)
```

### BaseEnv (Atropos)

The foundation from `atroposlib`. Provides:
- **Server management** — connects to OpenAI-compatible APIs (VLLM, SGLang, OpenRouter)
- **Worker scheduling** — parallel rollout coordination
- **Wandb integration** — metrics logging and rollout visualisation
- **CLI interface** — three subcommands: `serve`, `process`, `evaluate`
- **Eval logging** — `evaluate_log()` saves results to JSON + JSONL

### HermesAgentBaseEnv

The hermes-agent layer (`environments/hermes_base_env.py`). Adds:
- **Terminal backend configuration** — sets `TERMINAL_ENV` for sandboxed execution (local, Docker, Modal, Daytona, SSH, Singularity)
- **Tool resolution** — `_resolve_tools_for_group()` calls hermes-agent's `get_tool_definitions()` to get the right tool schemas based on enabled/disabled toolsets
- **Agent loop integration** — `collect_trajectory()` runs `HermesAgentLoop` and scores the result
- **Two-phase operation** — Phase 1 (OpenAI server) for eval/SFT, Phase 2 (VLLM ManagedServer) for full RL with logprobs
- **Async safety patches** — monkey-patches Modal backend to work inside Atropos's event loop

### Concrete Environments

Your environment inherits from `HermesAgentBaseEnv` and implements five methods:

| Method | Purpose |
|--------|---------|
| `setup()` | Load dataset, initialise state |
| `get_next_item()` | Return the next item for rollout |
| `format_prompt(item)` | Convert an item into the user message |
| `compute_reward(item, result, ctx)` | Score the rollout (0.0–1.0) |
| `evaluate()` | Periodic evaluation logic |

## Core Components

### Agent Loop

`HermesAgentLoop` (`environments/agent_loop.py`) is the reusable multi-turn agent engine. It runs the same tool-calling pattern as hermes-agent's main loop:

1. Send messages + tool schemas to the API via `server.chat_completion()`
2. If the response contains `tool_calls`, dispatch each via `handle_function_call()`
3. Append tool results to the conversation, go back to step 1
4. If no `tool_calls`, the agent is done

Tool calls execute in a thread pool (`ThreadPoolExecutor(128)`) so that async backends (Modal, Docker) don't deadlock inside Atropos's event loop.

Returns an `AgentResult`:

```python
@dataclass
class AgentResult:
    messages: List[Dict[str, Any]]       # Full conversation history
    turns_used: int                       # Number of LLM calls made
    finished_naturally: bool              # True if model stopped on its own
    reasoning_per_turn: List[Optional[str]]  # Extracted reasoning content
    tool_errors: List[ToolError]          # Errors encountered during tool dispatch
    managed_state: Optional[Dict]         # VLLM ManagedServer state (Phase 2)
```

### Tool Context

`ToolContext` (`environments/tool_context.py`) gives reward functions direct access to the **same sandbox** the model used during its rollout. The `task_id` scoping means all state (files, processes, browser tabs) is preserved.

```python
async def compute_reward(self, item, result, ctx: ToolContext):
    # Run tests in the model's terminal sandbox
    test = ctx.terminal("pytest -v")
    if test["exit_code"] == 0:
        return 1.0

    # Check if a file was created
    content = ctx.read_file("/workspace/solution.py")
    if content.get("content"):
        return 0.5

    # Download files for local verification
    ctx.download_file("/remote/output.bin", "/local/output.bin")
    return 0.0
```

Available methods:

| Category | Methods |
|----------|---------|
| **Terminal** | `terminal(command, timeout)` |
| **Files** | `read_file(path)`, `write_file(path, content)`, `search(query, path)` |
| **Transfers** | `upload_file()`, `upload_dir()`, `download_file()`, `download_dir()` |
| **Web** | `web_search(query)`, `web_extract(urls)` |
| **Browser** | `browser_navigate(url)`, `browser_snapshot()` |
| **Generic** | `call_tool(name, args)` — escape hatch for any hermes-agent tool |
| **Cleanup** | `cleanup()` — release all resources |

### Tool Call Parsers

For **Phase 2** (VLLM ManagedServer), the server returns raw text without structured tool calls. Client-side parsers in `environments/tool_call_parsers/` extract `tool_calls` from raw output:

```python
from environments.tool_call_parsers import get_parser

parser = get_parser("hermes")  # or "mistral", "llama3_json", "qwen", "deepseek_v3", etc.
content, tool_calls = parser.parse(raw_model_output)
```

Available parsers: `hermes`, `mistral`, `llama3_json`, `qwen`, `qwen3_coder`, `deepseek_v3`, `deepseek_v3_1`, `kimi_k2`, `longcat`, `glm45`, `glm47`.

In Phase 1 (OpenAI server type), parsers are not needed — the server handles tool call parsing natively.

## Available Benchmarks

### TerminalBench2

**89 challenging terminal tasks** with per-task Docker sandbox environments.

| | |
|---|---|
| **What it tests** | Single-task coding/sysadmin ability |
| **Scoring** | Binary pass/fail (test suite verification) |
| **Sandbox** | Modal cloud sandboxes (per-task Docker images) |
| **Tools** | `terminal` + `file` |
| **Tasks** | 89 tasks across multiple categories |
| **Cost** | ~$50–200 for full eval (parallel execution) |
| **Time** | ~2–4 hours |

```bash
python environments/benchmarks/terminalbench_2/terminalbench2_env.py evaluate \
    --config environments/benchmarks/terminalbench_2/default.yaml

# Run specific tasks
python environments/benchmarks/terminalbench_2/terminalbench2_env.py evaluate \
    --config environments/benchmarks/terminalbench_2/default.yaml \
    --env.task_filter fix-git,git-multibranch
```

Dataset: [NousResearch/terminal-bench-2](https://huggingface.co/datasets/NousResearch/terminal-bench-2) on HuggingFace.

### TBLite (OpenThoughts Terminal Bench Lite)

**100 difficulty-calibrated tasks** — a faster proxy for TerminalBench2.

| | |
|---|---|
| **What it tests** | Same as TB2 (coding/sysadmin), calibrated difficulty tiers |
| **Scoring** | Binary pass/fail |
| **Sandbox** | Modal cloud sandboxes |
| **Tools** | `terminal` + `file` |
| **Tasks** | 100 tasks: Easy (40), Medium (26), Hard (26), Extreme (8) |
| **Correlation** | r=0.911 with full TB2 |
| **Speed** | 2.6–8× faster than TB2 |

```bash
python environments/benchmarks/tblite/tblite_env.py evaluate \
    --config environments/benchmarks/tblite/default.yaml
```

TBLite is a thin subclass of TerminalBench2 — only the dataset and timeouts differ. Created by the OpenThoughts Agent team (Snorkel AI + Bespoke Labs). Dataset: [NousResearch/openthoughts-tblite](https://huggingface.co/datasets/NousResearch/openthoughts-tblite).

### YC-Bench

**Long-horizon strategic benchmark** — the agent plays CEO of an AI startup.

| | |
|---|---|
| **What it tests** | Multi-turn strategic coherence over hundreds of turns |
| **Scoring** | Composite: `0.5 × survival + 0.5 × normalised_funds` |
| **Sandbox** | Local terminal (no Modal needed) |
| **Tools** | `terminal` only |
| **Runs** | 9 default (3 presets × 3 seeds), sequential |
| **Cost** | ~$50–200 for full eval |
| **Time** | ~3–6 hours |

```bash
# Install yc-bench (optional dependency)
pip install "hermes-agent[yc-bench]"

# Run evaluation
bash environments/benchmarks/yc_bench/run_eval.sh

# Or directly
python environments/benchmarks/yc_bench/yc_bench_env.py evaluate \
    --config environments/benchmarks/yc_bench/default.yaml

# Quick single-preset test
python environments/benchmarks/yc_bench/yc_bench_env.py evaluate \
    --config environments/benchmarks/yc_bench/default.yaml \
    --env.presets '["fast_test"]' --env.seeds '[1]'
```

YC-Bench uses [collinear-ai/yc-bench](https://github.com/collinear-ai/yc-bench) — a deterministic simulation with 4 skill domains (research, inference, data_environment, training), prestige system, employee management, and financial pressure. Unlike TB2's per-task binary scoring, YC-Bench measures whether an agent can maintain coherent strategy over hundreds of compounding decisions.

## Training Environments

### TerminalTestEnv

A minimal self-contained environment with inline tasks (no external dataset). Used for **validating the full stack** end-to-end. Each task asks the model to create a file at a known path; the verifier checks the content.

```bash
# Process mode (saves rollouts to JSONL, no training server needed)
python environments/terminal_test_env/terminal_test_env.py process \
    --env.data_path_to_save_groups terminal_test_output.jsonl

# Serve mode (connects to Atropos API for RL training)
python environments/terminal_test_env/terminal_test_env.py serve
```

### HermesSweEnv

SWE-bench style training environment. The model gets a coding task, uses terminal + file + web tools to solve it, and the reward function runs tests in the same Modal sandbox.

```bash
python environments/hermes_swe_env/hermes_swe_env.py serve \
    --openai.model_name YourModel \
    --env.dataset_name bigcode/humanevalpack \
    --env.terminal_backend modal
```

## Running Environments

Every environment is a standalone Python script with three CLI subcommands:

### `evaluate` — Run a benchmark

For eval-only environments (benchmarks). Runs all items, computes metrics, logs to wandb.

```bash
python environments/benchmarks/tblite/tblite_env.py evaluate \
    --config environments/benchmarks/tblite/default.yaml \
    --openai.model_name anthropic/claude-sonnet-4.6
```

No training server or `run-api` needed. The environment handles everything.

### `process` — Generate SFT data

Runs rollouts and saves scored trajectories to JSONL. Useful for generating training data without a full RL loop.

```bash
python environments/terminal_test_env/terminal_test_env.py process \
    --env.data_path_to_save_groups output.jsonl \
    --openai.model_name anthropic/claude-sonnet-4.6
```

Output format: each line is a scored trajectory with the full conversation history, reward, and metadata.

### `serve` — Connect to Atropos for RL training

Connects the environment to a running Atropos API server (`run-api`). Used during live RL training.

```bash
# Terminal 1: Start the Atropos API
run-api

# Terminal 2: Start the environment
python environments/hermes_swe_env/hermes_swe_env.py serve \
    --openai.model_name YourModel
```

The environment receives items from Atropos, runs agent rollouts, computes rewards, and sends scored trajectories back for training.

## Two-Phase Operation

### Phase 1: OpenAI Server (Eval / SFT)

Uses `server.chat_completion()` with `tools=` parameter. The server (VLLM, SGLang, OpenRouter, OpenAI) handles tool call parsing natively. Returns `ChatCompletion` objects with structured `tool_calls`.

- **Use for**: evaluation, SFT data generation, benchmarks, testing
- **Placeholder tokens** are created for the Atropos pipeline (since real token IDs aren't available from the OpenAI API)

### Phase 2: VLLM ManagedServer (Full RL)

Uses ManagedServer for exact token IDs + logprobs via `/generate`. A client-side [tool call parser](#tool-call-parsers) reconstructs structured `tool_calls` from raw output.

- **Use for**: full RL training with GRPO/PPO
- **Real tokens**, masks, and logprobs flow through the pipeline
- Set `tool_call_parser` in config to match your model's format (e.g., `"hermes"`, `"qwen"`, `"mistral"`)

## Creating Environments

### Training Environment

```python
from environments.hermes_base_env import HermesAgentBaseEnv, HermesAgentEnvConfig
from atroposlib.envs.server_handling.server_manager import APIServerConfig

class MyEnvConfig(HermesAgentEnvConfig):
    my_custom_field: str = "default_value"

class MyEnv(HermesAgentBaseEnv):
    name = "my-env"
    env_config_cls = MyEnvConfig

    @classmethod
    def config_init(cls):
        env_config = MyEnvConfig(
            enabled_toolsets=["terminal", "file"],
            terminal_backend="modal",
            max_agent_turns=30,
        )
        server_configs = [APIServerConfig(
            base_url="https://openrouter.ai/api/v1",
            model_name="anthropic/claude-sonnet-4.6",
            server_type="openai",
        )]
        return env_config, server_configs

    async def setup(self):
        from datasets import load_dataset
        self.dataset = list(load_dataset("my-dataset", split="train"))
        self.iter = 0

    async def get_next_item(self):
        item = self.dataset[self.iter % len(self.dataset)]
        self.iter += 1
        return item

    def format_prompt(self, item):
        return item["instruction"]

    async def compute_reward(self, item, result, ctx):
        # ctx gives full tool access to the rollout's sandbox
        test = ctx.terminal("pytest -v")
        return 1.0 if test["exit_code"] == 0 else 0.0

    async def evaluate(self, *args, **kwargs):
        # Periodic evaluation during training
        pass

if __name__ == "__main__":
    MyEnv.cli()
```

### Eval-Only Benchmark

For benchmarks, follow the pattern used by TerminalBench2, TBLite, and YC-Bench:

1. **Create under** `environments/benchmarks/your-benchmark/`
2. **Set eval-only config**: `eval_handling=STOP_TRAIN`, `steps_per_eval=1`, `total_steps=1`
3. **Stub training methods**: `collect_trajectories()` returns `(None, [])`, `score()` returns `None`
4. **Implement** `rollout_and_score_eval(eval_item)` — the per-item agent loop + scoring
5. **Implement** `evaluate()` — orchestrates all runs, computes aggregate metrics
6. **Add streaming JSONL** for crash-safe result persistence
7. **Add cleanup**: `KeyboardInterrupt` handling, `cleanup_all_environments()`, `_tool_executor.shutdown()`
8. **Run with** `evaluate` subcommand

See `environments/benchmarks/yc_bench/yc_bench_env.py` for a clean, well-documented reference implementation.

## Configuration Reference

### HermesAgentEnvConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled_toolsets` | `List[str]` | `None` (all) | Which hermes toolsets to enable |
| `disabled_toolsets` | `List[str]` | `None` | Toolsets to filter out |
| `distribution` | `str` | `None` | Probabilistic toolset distribution name |
| `max_agent_turns` | `int` | `30` | Max LLM calls per rollout |
| `agent_temperature` | `float` | `1.0` | Sampling temperature |
| `system_prompt` | `str` | `None` | System message for the agent |
| `terminal_backend` | `str` | `"local"` | `local`, `docker`, `modal`, `daytona`, `ssh`, `singularity` |
| `terminal_timeout` | `int` | `120` | Seconds per terminal command |
| `terminal_lifetime` | `int` | `3600` | Max sandbox lifetime |
| `dataset_name` | `str` | `None` | HuggingFace dataset identifier |
| `tool_pool_size` | `int` | `128` | Thread pool size for tool execution |
| `tool_call_parser` | `str` | `"hermes"` | Parser for Phase 2 raw output |
| `extra_body` | `Dict` | `None` | Extra params for OpenAI API (e.g., OpenRouter provider prefs) |
| `eval_handling` | `Enum` | `STOP_TRAIN` | `STOP_TRAIN`, `LIMIT_TRAIN`, `NONE` |

### YAML Configuration

Environments can be configured via YAML files passed with `--config`:

```yaml
env:
  enabled_toolsets: ["terminal", "file"]
  max_agent_turns: 60
  max_token_length: 32000
  agent_temperature: 0.8
  terminal_backend: "modal"
  terminal_timeout: 300
  dataset_name: "NousResearch/terminal-bench-2"
  tokenizer_name: "NousResearch/Hermes-3-Llama-3.1-8B"
  use_wandb: true
  wandb_name: "my-benchmark"

openai:
  base_url: "https://openrouter.ai/api/v1"
  model_name: "anthropic/claude-sonnet-4.6"
  server_type: "openai"
  health_check: false
```

YAML values override `config_init()` defaults. CLI arguments override YAML values:

```bash
python my_env.py evaluate \
    --config my_config.yaml \
    --openai.model_name anthropic/claude-opus-4.6  # overrides YAML
```

## Prerequisites

### For all environments

- Python >= 3.11
- `atroposlib`: `pip install git+https://github.com/NousResearch/atropos.git`
- An LLM API key (OpenRouter, OpenAI, or self-hosted VLLM/SGLang)

### For Modal-sandboxed benchmarks (TB2, TBLite)

- [Modal](https://modal.com) account and CLI: `pip install "hermes-agent[modal]"`
- `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` environment variables

### For YC-Bench

- `pip install "hermes-agent[yc-bench]"` (installs the yc-bench CLI + SQLAlchemy)
- No Modal needed — runs with local terminal backend

### For RL training

- `TINKER_API_KEY` — API key for the [Tinker](https://tinker.computer) training service
- `WANDB_API_KEY` — for Weights & Biases metrics tracking
- The `tinker-atropos` submodule (at `tinker-atropos/` in the repo)

See [RL Training](/user-guide/features/rl-training) for the agent-driven RL workflow.

## Directory Structure

```
environments/
├── hermes_base_env.py          # Abstract base class (HermesAgentBaseEnv)
├── agent_loop.py               # Multi-turn agent engine (HermesAgentLoop)
├── tool_context.py             # Per-rollout tool access for reward functions
├── patches.py                  # Async-safety patches for Modal backend
│
├── tool_call_parsers/          # Phase 2 client-side parsers
│   ├── hermes_parser.py        # Hermes/ChatML <tool_call> format
│   ├── mistral_parser.py       # Mistral [TOOL_CALLS] format
│   ├── llama_parser.py         # Llama 3 JSON tool calling
│   ├── qwen_parser.py          # Qwen format
│   ├── deepseek_v3_parser.py   # DeepSeek V3 format
│   └── ...                     # + kimi_k2, longcat, glm45/47, etc.
│
├── terminal_test_env/          # Stack validation (inline tasks)
├── hermes_swe_env/             # SWE-bench training environment
│
└── benchmarks/                 # Evaluation benchmarks
    ├── terminalbench_2/        # 89 terminal tasks, Modal sandboxes
    ├── tblite/                 # 100 calibrated tasks (fast TB2 proxy)
    └── yc_bench/               # Long-horizon strategic benchmark
```



================================================
FILE: website/docs/getting-started/_category_.json
================================================
{
  "label": "Getting Started",
  "position": 1,
  "link": {
    "type": "generated-index",
    "description": "Get up and running with Hermes Agent in minutes."
  }
}



================================================
FILE: website/docs/getting-started/installation.md
================================================
---
sidebar_position: 2
title: "Installation"
description: "Install Hermes Agent on Linux, macOS, or WSL2"
---

# Installation

Get Hermes Agent up and running in under two minutes with the one-line installer, or follow the manual steps for full control.

## Quick Install

### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::warning Windows
Native Windows is **not supported**. Please install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and run Hermes Agent from there. The install command above works inside WSL2.
:::

### What the Installer Does

The installer handles everything automatically — all dependencies (Python, Node.js, ripgrep, ffmpeg), the repo clone, virtual environment, and global `hermes` command setup. It finishes by running the interactive setup wizard to configure your LLM provider.

### After Installation

Reload your shell and start chatting:

```bash
source ~/.bashrc   # or: source ~/.zshrc
hermes setup       # Configure API keys (if you skipped during install)
hermes             # Start chatting!
```

---

## Prerequisites

The only prerequisite is **Git**. The installer automatically handles everything else:

- **uv** (fast Python package manager)
- **Python 3.11** (via uv, no sudo needed)
- **Node.js v22** (for browser automation and WhatsApp bridge)
- **ripgrep** (fast file search)
- **ffmpeg** (audio format conversion for TTS)

:::info
You do **not** need to install Python, Node.js, ripgrep, or ffmpeg manually. The installer detects what's missing and installs it for you. Just make sure `git` is available (`git --version`).
:::

---

## Manual Installation

If you prefer full control over the installation process, follow these steps.

### Step 1: Clone the Repository

Clone with `--recurse-submodules` to pull the required submodules:

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

If you already cloned without `--recurse-submodules`:
```bash
git submodule update --init --recursive
```

### Step 2: Install uv & Create Virtual Environment

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv with Python 3.11 (uv downloads it if not present — no sudo needed)
uv venv venv --python 3.11
```

:::tip
You do **not** need to activate the venv to use `hermes`. The entry point has a hardcoded shebang pointing to the venv Python, so it works globally once symlinked.
:::

### Step 3: Install Python Dependencies

```bash
# Tell uv which venv to install into
export VIRTUAL_ENV="$(pwd)/venv"

# Install with all extras
uv pip install -e ".[all]"
```

If you only want the core agent (no Telegram/Discord/cron support):
```bash
uv pip install -e "."
```

<details>
<summary><strong>Optional extras breakdown</strong></summary>

| Extra | What it adds | Install command |
|-------|-------------|-----------------|
| `all` | Everything below | `uv pip install -e ".[all]"` |
| `messaging` | Telegram & Discord gateway | `uv pip install -e ".[messaging]"` |
| `cron` | Cron expression parsing for scheduled tasks | `uv pip install -e ".[cron]"` |
| `cli` | Terminal menu UI for setup wizard | `uv pip install -e ".[cli]"` |
| `modal` | Modal cloud execution backend | `uv pip install -e ".[modal]"` |
| `tts-premium` | ElevenLabs premium voices | `uv pip install -e ".[tts-premium]"` |
| `pty` | PTY terminal support | `uv pip install -e ".[pty]"` |
| `honcho` | AI-native memory (Honcho integration) | `uv pip install -e ".[honcho]"` |
| `mcp` | Model Context Protocol support | `uv pip install -e ".[mcp]"` |
| `homeassistant` | Home Assistant integration | `uv pip install -e ".[homeassistant]"` |
| `slack` | Slack messaging | `uv pip install -e ".[slack]"` |
| `dev` | pytest & test utilities | `uv pip install -e ".[dev]"` |

You can combine extras: `uv pip install -e ".[messaging,cron]"`

</details>

### Step 4: Install Submodule Packages

```bash
# Terminal tool backend (required for terminal/command-execution)
uv pip install -e "./mini-swe-agent"

# RL training backend
uv pip install -e "./tinker-atropos"
```

Both are optional — if you skip them, the corresponding toolsets simply won't be available.

### Step 5: Install Node.js Dependencies (Optional)

Only needed for **browser automation** (Browserbase-powered) and **WhatsApp bridge**:

```bash
npm install
```

### Step 6: Create the Configuration Directory

```bash
# Create the directory structure
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}

# Copy the example config file
cp cli-config.yaml.example ~/.hermes/config.yaml

# Create an empty .env file for API keys
touch ~/.hermes/.env
```

### Step 7: Add Your API Keys

Open `~/.hermes/.env` and add at minimum an LLM provider key:

```bash
# Required — at least one LLM provider:
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional — enable additional tools:
FIRECRAWL_API_KEY=fc-your-key          # Web search & scraping (or self-host, see docs)
FAL_KEY=your-fal-key                   # Image generation (FLUX)
```

Or set them via the CLI:
```bash
hermes config set OPENROUTER_API_KEY sk-or-v1-your-key-here
```

### Step 8: Add `hermes` to Your PATH

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

If `~/.local/bin` isn't on your PATH, add it to your shell config:

```bash
# Bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc

# Zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# Fish
fish_add_path $HOME/.local/bin
```

### Step 9: Run the Setup Wizard (Optional)

```bash
hermes setup
```

### Step 10: Verify the Installation

```bash
hermes version    # Check that the command is available
hermes doctor     # Run diagnostics to verify everything is working
hermes status     # Check your configuration
hermes chat -q "Hello! What tools do you have available?"
```

---

## Quick-Reference: Manual Install (Condensed)

For those who just want the commands:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone & enter
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Create venv with Python 3.11
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# Install everything
uv pip install -e ".[all]"
uv pip install -e "./mini-swe-agent"
uv pip install -e "./tinker-atropos"
npm install  # optional, for browser tools and WhatsApp

# Configure
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env

# Make hermes available globally
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# Verify
hermes doctor
hermes
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `hermes: command not found` | Reload your shell (`source ~/.bashrc`) or check PATH |
| `API key not set` | Run `hermes setup` or `hermes config set OPENROUTER_API_KEY your_key` |
| Missing config after update | Run `hermes config check` then `hermes config migrate` |

For more diagnostics, run `hermes doctor` — it will tell you exactly what's missing and how to fix it.



================================================
FILE: website/docs/getting-started/quickstart.md
================================================
---
sidebar_position: 1
title: "Quickstart"
description: "Your first conversation with Hermes Agent — from install to chatting in 2 minutes"
---

# Quickstart

This guide walks you through installing Hermes Agent, setting up a provider, and having your first conversation. By the end, you'll know the key features and how to explore further.

## 1. Install Hermes Agent

Run the one-line installer:

```bash
# Linux / macOS / WSL2
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

:::tip Windows Users
Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) first, then run the command above inside your WSL2 terminal.
:::

After it finishes, reload your shell:

```bash
source ~/.bashrc   # or source ~/.zshrc
```

## 2. Set Up a Provider

The installer runs the setup wizard automatically. If you skipped it, run:

```bash
hermes setup
```

This walks you through selecting an inference provider:

| Provider | What it is | How to set up |
|----------|-----------|---------------|
| **Nous Portal** | Subscription-based, zero-config | OAuth login via `hermes model` |
| **OpenAI Codex** | ChatGPT OAuth, uses Codex models | Device code auth via `hermes model` |
| **OpenRouter** | 200+ models, pay-per-use | Enter your API key |
| **Custom Endpoint** | VLLM, SGLang, any OpenAI-compatible API | Set base URL + API key |

:::tip
You can switch providers at any time with `hermes model` — no code changes, no lock-in.
:::

## 3. Start Chatting

```bash
hermes
```

That's it! You'll see a welcome banner with your model, available tools, and skills. Type a message and press Enter.

```
❯ What can you help me with?
```

The agent has access to tools for web search, file operations, terminal commands, and more — all out of the box.

## 4. Try Key Features

### Ask it to use the terminal

```
❯ What's my disk usage? Show the top 5 largest directories.
```

The agent will run terminal commands on your behalf and show you the results.

### Use slash commands

Type `/` to see an autocomplete dropdown of all commands:

| Command | What it does |
|---------|-------------|
| `/help` | Show all available commands |
| `/tools` | List available tools |
| `/model` | Switch models interactively |
| `/personality pirate` | Try a fun personality |
| `/save` | Save the conversation |

### Multi-line input

Press `Alt+Enter` or `Ctrl+J` to add a new line. Great for pasting code or writing detailed prompts.

### Interrupt the agent

If the agent is taking too long, just type a new message and press Enter — it interrupts the current task and switches to your new instructions. `Ctrl+C` also works.

### Resume a session

When you exit, hermes prints a resume command:

```bash
hermes --continue    # Resume the most recent session
hermes -c            # Short form
```

## 5. Explore Further

Here are some things to try next:

### Set up a sandboxed terminal

For safety, run the agent in a Docker container or on a remote server:

```bash
hermes config set terminal.backend docker    # Docker isolation
hermes config set terminal.backend ssh       # Remote server
```

### Connect messaging platforms

Chat with Hermes from your phone via Telegram, Discord, Slack, or WhatsApp:

```bash
hermes gateway setup    # Interactive platform configuration
```

### Schedule automated tasks

```
❯ Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

The agent will set up a cron job that runs automatically via the gateway.

### Browse and install skills

```bash
hermes skills search kubernetes
hermes skills install openai/skills/k8s
```

Or use the `/skills` slash command inside chat.

### Try MCP servers

Connect to external tools via the Model Context Protocol:

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `hermes` | Start chatting |
| `hermes setup` | Configure providers and settings |
| `hermes model` | Switch provider or model |
| `hermes tools` | Configure which tools are enabled per platform |
| `hermes doctor` | Diagnose issues |
| `hermes update` | Update to latest version |
| `hermes gateway` | Start the messaging gateway |
| `hermes --continue` | Resume last session |

## Next Steps

- **[CLI Guide](../user-guide/cli.md)** — Master the terminal interface
- **[Configuration](../user-guide/configuration.md)** — Customize your setup
- **[Messaging Gateway](../user-guide/messaging/index.md)** — Connect Telegram, Discord, Slack, WhatsApp
- **[Tools & Toolsets](../user-guide/features/tools.md)** — Explore available capabilities



================================================
FILE: website/docs/getting-started/updating.md
================================================
---
sidebar_position: 3
title: "Updating & Uninstalling"
description: "How to update Hermes Agent to the latest version or uninstall it"
---

# Updating & Uninstalling

## Updating

Update to the latest version with a single command:

```bash
hermes update
```

This pulls the latest code, updates dependencies, and prompts you to configure any new options that were added since your last update.

:::tip
`hermes update` automatically detects new configuration options and prompts you to add them. If you skipped that prompt, you can manually run `hermes config check` to see missing options, then `hermes config migrate` to interactively add them.
:::

### Updating from Messaging Platforms

You can also update directly from Telegram, Discord, Slack, or WhatsApp by sending:

```
/update
```

This pulls the latest code, updates dependencies, and restarts the gateway.

### Manual Update

If you installed manually (not via the quick installer):

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# Pull latest code and submodules
git pull origin main
git submodule update --init --recursive

# Reinstall (picks up new dependencies)
uv pip install -e ".[all]"
uv pip install -e "./mini-swe-agent"
uv pip install -e "./tinker-atropos"

# Check for new config options
hermes config check
hermes config migrate   # Interactively add any missing options
```

---

## Uninstalling

```bash
hermes uninstall
```

The uninstaller gives you the option to keep your configuration files (`~/.hermes/`) for a future reinstall.

### Manual Uninstall

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # Optional — keep if you plan to reinstall
```

:::info
If you installed the gateway as a system service, stop and disable it first:
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::



================================================
FILE: website/docs/reference/_category_.json
================================================
{
  "label": "Reference",
  "position": 4,
  "link": {
    "type": "generated-index",
    "description": "Complete reference for CLI commands, environment variables, and configuration."
  }
}



================================================
FILE: website/docs/reference/cli-commands.md
================================================
---
sidebar_position: 1
title: "CLI Commands Reference"
description: "Comprehensive reference for all hermes CLI commands and slash commands"
---

# CLI Commands Reference

## Terminal Commands

These are commands you run from your shell.

### Core Commands

| Command | Description |
|---------|-------------|
| `hermes` | Start interactive chat (default) |
| `hermes chat -q "Hello"` | Single query mode (non-interactive) |
| `hermes chat --continue` / `-c` | Resume the most recent session |
| `hermes chat --resume <id>` / `-r <id>` | Resume a specific session |
| `hermes chat --model <name>` | Use a specific model |
| `hermes chat --provider <name>` | Force a provider (`nous`, `openrouter`, `zai`, `kimi-coding`, `minimax`, `minimax-cn`) |
| `hermes chat --toolsets "web,terminal"` / `-t` | Use specific toolsets |
| `hermes chat --verbose` | Enable verbose/debug output |
| `hermes --worktree` / `-w` | Start in an isolated git worktree (for parallel agents) |

### Provider & Model Management

| Command | Description |
|---------|-------------|
| `hermes model` | Switch provider and model interactively |
| `hermes login` | OAuth login to a provider (use `--provider` to specify) |
| `hermes logout` | Clear provider authentication |

### Configuration

| Command | Description |
|---------|-------------|
| `hermes setup` | Full setup wizard (provider, terminal, messaging) |
| `hermes config` | View current configuration |
| `hermes config edit` | Open config.yaml in your editor |
| `hermes config set KEY VAL` | Set a specific value |
| `hermes config check` | Check for missing config (useful after updates) |
| `hermes config migrate` | Interactively add missing options |
| `hermes tools` | Interactive tool configuration per platform |
| `hermes status` | Show configuration status (including auth) |
| `hermes doctor` | Diagnose issues |

### Maintenance

| Command | Description |
|---------|-------------|
| `hermes update` | Update to latest version |
| `hermes uninstall` | Uninstall (can keep configs for later reinstall) |
| `hermes version` | Show version info |

### Gateway (Messaging + Cron)

| Command | Description |
|---------|-------------|
| `hermes gateway` | Run gateway in foreground |
| `hermes gateway setup` | Configure messaging platforms interactively |
| `hermes gateway install` | Install as system service (Linux/macOS) |
| `hermes gateway start` | Start the service |
| `hermes gateway stop` | Stop the service |
| `hermes gateway restart` | Restart the service |
| `hermes gateway status` | Check service status |
| `hermes gateway uninstall` | Uninstall the system service |
| `hermes whatsapp` | Pair WhatsApp via QR code |

### Skills

| Command | Description |
|---------|-------------|
| `hermes skills browse` | Browse all available skills with pagination (official first) |
| `hermes skills search <query>` | Search skill registries |
| `hermes skills install <identifier>` | Install a skill (with security scan) |
| `hermes skills inspect <identifier>` | Preview before installing |
| `hermes skills list` | List installed skills |
| `hermes skills list --source hub` | List hub-installed skills only |
| `hermes skills audit` | Re-scan all hub skills |
| `hermes skills uninstall <name>` | Remove a hub skill |
| `hermes skills publish <path> --to github --repo owner/repo` | Publish a skill |
| `hermes skills snapshot export <file>` | Export skill config |
| `hermes skills snapshot import <file>` | Import from snapshot |
| `hermes skills tap add <repo>` | Add a custom source |
| `hermes skills tap remove <repo>` | Remove a source |
| `hermes skills tap list` | List custom sources |

### Cron & Pairing

| Command | Description |
|---------|-------------|
| `hermes cron list` | View scheduled jobs |
| `hermes cron status` | Check if cron scheduler is running |
| `hermes cron tick` | Manually trigger a cron tick |
| `hermes pairing list` | View pending + approved users |
| `hermes pairing approve <platform> <code>` | Approve a pairing code |
| `hermes pairing revoke <platform> <user_id>` | Remove user access |
| `hermes pairing clear-pending` | Clear all pending pairing requests |

### Sessions

| Command | Description |
|---------|-------------|
| `hermes sessions list` | Browse past sessions |
| `hermes sessions export <id>` | Export a session |
| `hermes sessions delete <id>` | Delete a specific session |
| `hermes sessions prune` | Remove old sessions |
| `hermes sessions stats` | Show session statistics |

### Insights

| Command | Description |
|---------|-------------|
| `hermes insights` | Show usage analytics for the last 30 days |
| `hermes insights --days 7` | Analyze a custom time window |
| `hermes insights --source telegram` | Filter by platform |

---

## Slash Commands (Inside Chat)

Type `/` in the interactive CLI to see an autocomplete dropdown.

### Navigation & Control

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/quit` | Exit the CLI (aliases: `/exit`, `/q`) |
| `/clear` | Clear screen and reset conversation |
| `/new` | Start a new conversation |
| `/reset` | Reset conversation only (keep screen) |

### Tools & Configuration

| Command | Description |
|---------|-------------|
| `/tools` | List all available tools |
| `/toolsets` | List available toolsets |
| `/model [provider:model]` | Show or change the current model (supports `provider:model` syntax to switch providers) |
| `/provider` | Show available providers with auth status |
| `/config` | Show current configuration |
| `/prompt [text]` | View/set custom system prompt |
| `/personality [name]` | Set a predefined personality |

### Conversation

| Command | Description |
|---------|-------------|
| `/history` | Show conversation history |
| `/retry` | Retry the last message |
| `/undo` | Remove the last user/assistant exchange |
| `/save` | Save the current conversation |
| `/compress` | Manually compress conversation context |
| `/usage` | Show token usage for this session |
| `/insights [--days N]` | Show usage insights and analytics (last 30 days) |

### Media & Input

| Command | Description |
|---------|-------------|
| `/paste` | Check clipboard for an image and attach it (see [Vision & Image Paste](/docs/user-guide/features/vision)) |

### Skills & Scheduling

| Command | Description |
|---------|-------------|
| `/cron` | Manage scheduled tasks |
| `/skills` | Browse, search, install, inspect, or manage skills |
| `/platforms` | Show gateway/messaging platform status |
| `/verbose` | Cycle tool progress: off → new → all → verbose |
| `/<skill-name>` | Invoke any installed skill |

### Gateway-Only Commands

These work in messaging platforms (Telegram, Discord, Slack, WhatsApp) but not the interactive CLI:

| Command | Description |
|---------|-------------|
| `/stop` | Stop the running agent (no follow-up message) |
| `/sethome` | Set this chat as the home channel |
| `/status` | Show session info |
| `/reload-mcp` | Reload MCP servers from config |
| `/update` | Update Hermes Agent to the latest version |

---

## Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Alt+Enter` / `Ctrl+J` | New line (multi-line input) |
| `Alt+V` | Paste image from clipboard (see [Vision & Image Paste](/docs/user-guide/features/vision)) |
| `Ctrl+V` | Paste text + auto-check for clipboard image |
| `Ctrl+C` | Clear input/images, interrupt agent, or exit (contextual) |
| `Ctrl+D` | Exit |
| `Tab` | Autocomplete slash commands |

:::tip
Commands are case-insensitive — `/HELP` works the same as `/help`.
:::

:::info Image paste keybindings
`Alt+V` works in most terminals but **not** in VSCode's integrated terminal (VSCode intercepts Alt+key combos). `Ctrl+V` only triggers an image check when the clipboard also contains text (terminals don't send paste events for image-only clipboard). The `/paste` command is the universal fallback. See the [full compatibility table](/docs/user-guide/features/vision#platform-compatibility).
:::



================================================
FILE: website/docs/reference/environment-variables.md
================================================
---
sidebar_position: 2
title: "Environment Variables"
description: "Complete reference of all environment variables used by Hermes Agent"
---

# Environment Variables Reference

All variables go in `~/.hermes/.env`. You can also set them with `hermes config set VAR value`.

## LLM Providers

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key (recommended for flexibility) |
| `OPENAI_API_KEY` | API key for custom OpenAI-compatible endpoints (used with `OPENAI_BASE_URL`) |
| `OPENAI_BASE_URL` | Base URL for custom endpoint (VLLM, SGLang, etc.) |
| `GLM_API_KEY` | z.ai / ZhipuAI GLM API key ([z.ai](https://z.ai)) |
| `GLM_BASE_URL` | Override z.ai base URL (default: `https://api.z.ai/api/paas/v4`) |
| `KIMI_API_KEY` | Kimi / Moonshot AI API key ([moonshot.ai](https://platform.moonshot.ai)) |
| `KIMI_BASE_URL` | Override Kimi base URL (default: `https://api.moonshot.ai/v1`) |
| `MINIMAX_API_KEY` | MiniMax API key — global endpoint ([minimax.io](https://www.minimax.io)) |
| `MINIMAX_BASE_URL` | Override MiniMax base URL (default: `https://api.minimax.io/v1`) |
| `MINIMAX_CN_API_KEY` | MiniMax API key — China endpoint ([minimaxi.com](https://www.minimaxi.com)) |
| `MINIMAX_CN_BASE_URL` | Override MiniMax China base URL (default: `https://api.minimaxi.com/v1`) |
| `HERMES_MODEL` | Preferred model name (checked before `LLM_MODEL`, used by gateway) |
| `LLM_MODEL` | Default model name (fallback when not set in config.yaml) |
| `VOICE_TOOLS_OPENAI_KEY` | OpenAI key for TTS and voice transcription (separate from custom endpoint) |
| `HERMES_HOME` | Override Hermes config directory (default: `~/.hermes`) |

## Provider Auth (OAuth)

| Variable | Description |
|----------|-------------|
| `HERMES_INFERENCE_PROVIDER` | Override provider selection: `auto`, `openrouter`, `nous`, `zai`, `kimi-coding`, `minimax`, `minimax-cn` (default: `auto`) |
| `HERMES_PORTAL_BASE_URL` | Override Nous Portal URL (for development/testing) |
| `NOUS_INFERENCE_BASE_URL` | Override Nous inference API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | Min agent key TTL before re-mint (default: 1800 = 30min) |
| `HERMES_DUMP_REQUESTS` | Dump API request payloads to log files (`true`/`false`) |

## Tool APIs

| Variable | Description |
|----------|-------------|
| `FIRECRAWL_API_KEY` | Web scraping ([firecrawl.dev](https://firecrawl.dev/)) |
| `FIRECRAWL_API_URL` | Custom Firecrawl API endpoint for self-hosted instances (optional) |
| `BROWSERBASE_API_KEY` | Browser automation ([browserbase.com](https://browserbase.com/)) |
| `BROWSERBASE_PROJECT_ID` | Browserbase project ID |
| `BROWSER_INACTIVITY_TIMEOUT` | Browser session inactivity timeout in seconds |
| `FAL_KEY` | Image generation ([fal.ai](https://fal.ai/)) |
| `ELEVENLABS_API_KEY` | Premium TTS voices ([elevenlabs.io](https://elevenlabs.io/)) |
| `HONCHO_API_KEY` | Cross-session user modeling ([honcho.dev](https://honcho.dev/)) |
| `TINKER_API_KEY` | RL training ([tinker-console.thinkingmachines.ai](https://tinker-console.thinkingmachines.ai/)) |
| `WANDB_API_KEY` | RL training metrics ([wandb.ai](https://wandb.ai/)) |
| `DAYTONA_API_KEY` | Daytona cloud sandboxes ([daytona.io](https://daytona.io/)) |

## Terminal Backend

| Variable | Description |
|----------|-------------|
| `TERMINAL_ENV` | Backend: `local`, `docker`, `ssh`, `singularity`, `modal`, `daytona` |
| `TERMINAL_DOCKER_IMAGE` | Docker image (default: `python:3.11`) |
| `TERMINAL_DOCKER_VOLUMES` | Additional Docker volume mounts (comma-separated `host:container` pairs) |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity image or `.sif` path |
| `TERMINAL_MODAL_IMAGE` | Modal container image |
| `TERMINAL_DAYTONA_IMAGE` | Daytona sandbox image |
| `TERMINAL_TIMEOUT` | Command timeout in seconds |
| `TERMINAL_LIFETIME_SECONDS` | Max lifetime for terminal sessions in seconds |
| `TERMINAL_CWD` | Working directory for all terminal sessions |
| `SUDO_PASSWORD` | Enable sudo without interactive prompt |

## SSH Backend

| Variable | Description |
|----------|-------------|
| `TERMINAL_SSH_HOST` | Remote server hostname |
| `TERMINAL_SSH_USER` | SSH username |
| `TERMINAL_SSH_PORT` | SSH port (default: 22) |
| `TERMINAL_SSH_KEY` | Path to private key |

## Container Resources (Docker, Singularity, Modal, Daytona)

| Variable | Description |
|----------|-------------|
| `TERMINAL_CONTAINER_CPU` | CPU cores (default: 1) |
| `TERMINAL_CONTAINER_MEMORY` | Memory in MB (default: 5120) |
| `TERMINAL_CONTAINER_DISK` | Disk in MB (default: 51200) |
| `TERMINAL_CONTAINER_PERSISTENT` | Persist container filesystem across sessions (default: `true`) |
| `TERMINAL_SANDBOX_DIR` | Host directory for workspaces and overlays (default: `~/.hermes/sandboxes/`) |

## Messaging

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (from @BotFather) |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated user IDs allowed to use bot |
| `TELEGRAM_HOME_CHANNEL` | Default channel for cron delivery |
| `TELEGRAM_HOME_CHANNEL_NAME` | Display name for home channel |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_ALLOWED_USERS` | Comma-separated user IDs allowed to use bot |
| `DISCORD_HOME_CHANNEL` | Default channel for cron delivery |
| `DISCORD_HOME_CHANNEL_NAME` | Display name for home channel |
| `SLACK_BOT_TOKEN` | Slack bot token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | Slack app-level token (`xapp-...`, required for Socket Mode) |
| `SLACK_ALLOWED_USERS` | Comma-separated Slack user IDs |
| `SLACK_HOME_CHANNEL` | Default Slack channel for cron delivery |
| `WHATSAPP_ENABLED` | Enable WhatsApp bridge (`true`/`false`) |
| `WHATSAPP_MODE` | `bot` (separate number) or `self-chat` (message yourself) |
| `WHATSAPP_ALLOWED_USERS` | Comma-separated phone numbers (with country code) |
| `MESSAGING_CWD` | Working directory for terminal in messaging (default: `~`) |
| `GATEWAY_ALLOWED_USERS` | Comma-separated user IDs allowed across all platforms |
| `GATEWAY_ALLOW_ALL_USERS` | Allow all users without allowlist (`true`/`false`, default: `false`) |

## Agent Behavior

| Variable | Description |
|----------|-------------|
| `HERMES_MAX_ITERATIONS` | Max tool-calling iterations per conversation (default: 60) |
| `HERMES_TOOL_PROGRESS` | Send progress messages when using tools (`true`/`false`) |
| `HERMES_TOOL_PROGRESS_MODE` | `all` (every call, default) or `new` (only when tool changes) |
| `HERMES_HUMAN_DELAY_MODE` | Response pacing: `off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | Custom delay range minimum (ms) |
| `HERMES_HUMAN_DELAY_MAX_MS` | Custom delay range maximum (ms) |
| `HERMES_QUIET` | Suppress non-essential output (`true`/`false`) |
| `HERMES_EXEC_ASK` | Enable execution approval prompts in gateway mode (`true`/`false`) |

## Session Settings

| Variable | Description |
|----------|-------------|
| `SESSION_IDLE_MINUTES` | Reset sessions after N minutes of inactivity (default: 120) |
| `SESSION_RESET_HOUR` | Daily reset hour in 24h format (default: 4 = 4am) |

## Context Compression

| Variable | Description |
|----------|-------------|
| `CONTEXT_COMPRESSION_ENABLED` | Enable auto-compression (default: `true`) |
| `CONTEXT_COMPRESSION_THRESHOLD` | Trigger at this % of limit (default: 0.85) |
| `CONTEXT_COMPRESSION_MODEL` | Model for summaries |

## Provider Routing (config.yaml only)

These go in `~/.hermes/config.yaml` under the `provider_routing` section:

| Key | Description |
|-----|-------------|
| `sort` | Sort providers: `"price"` (default), `"throughput"`, or `"latency"` |
| `only` | List of provider slugs to allow (e.g., `["anthropic", "google"]`) |
| `ignore` | List of provider slugs to skip |
| `order` | List of provider slugs to try in order |
| `require_parameters` | Only use providers supporting all request params (`true`/`false`) |
| `data_collection` | `"allow"` (default) or `"deny"` to exclude data-storing providers |

:::tip
Use `hermes config set` to set environment variables — it automatically saves them to the right file (`.env` for secrets, `config.yaml` for everything else).
:::



================================================
FILE: website/docs/user-guide/_category_.json
================================================
{
  "label": "User Guide",
  "position": 2,
  "link": {
    "type": "generated-index",
    "description": "Learn how to use Hermes Agent effectively."
  }
}



================================================
FILE: website/docs/user-guide/cli.md
================================================
---
sidebar_position: 1
title: "CLI Interface"
description: "Master the Hermes Agent terminal interface — commands, keybindings, personalities, and more"
---

# CLI Interface

Hermes Agent's CLI is a full terminal user interface (TUI) — not a web UI. It features multiline editing, slash-command autocomplete, conversation history, interrupt-and-redirect, and streaming tool output. Built for people who live in the terminal.

## Running the CLI

```bash
# Start an interactive session (default)
hermes

# Single query mode (non-interactive)
hermes chat -q "Hello"

# With a specific model
hermes chat --model "anthropic/claude-sonnet-4"

# With a specific provider
hermes chat --provider nous        # Use Nous Portal
hermes chat --provider openrouter  # Force OpenRouter

# With specific toolsets
hermes chat --toolsets "web,terminal,skills"

# Resume previous sessions
hermes --continue             # Resume the most recent CLI session (-c)
hermes --resume <session_id>  # Resume a specific session by ID (-r)

# Verbose mode (debug output)
hermes chat --verbose

# Isolated git worktree (for running multiple agents in parallel)
hermes -w                         # Interactive mode in worktree
hermes -w -q "Fix issue #123"     # Single query in worktree
```

## Interface Layout

```text
┌─────────────────────────────────────────────────┐
│  HERMES-AGENT ASCII Logo                        │
│  ┌─────────────┐ ┌────────────────────────────┐ │
│  │  Caduceus   │ │ Model: claude-sonnet-4     │ │
│  │  ASCII Art  │ │ Terminal: local            │ │
│  │             │ │ Working Dir: /home/user    │ │
│  │             │ │ Available Tools: 19        │ │
│  │             │ │ Available Skills: 12       │ │
│  └─────────────┘ └────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│ Conversation output scrolls here...             │
│                                                 │
│   (◕‿◕✿) 🧠 pondering... (2.3s)                │
│   ✧٩(ˊᗜˋ*)و✧ got it! (2.3s)                    │
│                                                 │
│ Assistant: Hello! How can I help you today?     │
├─────────────────────────────────────────────────┤
│ ❯ [Fixed input area at bottom]                  │
└─────────────────────────────────────────────────┘
```

The welcome banner shows your model, terminal backend, working directory, available tools, and installed skills at a glance.

## Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Alt+Enter` or `Ctrl+J` | New line (multi-line input) |
| `Ctrl+C` | Interrupt agent (double-press within 2s to force exit) |
| `Ctrl+D` | Exit |
| `Tab` | Autocomplete slash commands |

## Slash Commands

Type `/` to see an autocomplete dropdown of all available commands.

### Navigation & Control

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/quit` | Exit the CLI (also: `/exit`, `/q`) |
| `/clear` | Clear screen and reset conversation |
| `/new` | Start a new conversation |
| `/reset` | Reset conversation only (keep screen) |

### Tools & Configuration

| Command | Description |
|---------|-------------|
| `/tools` | List all available tools grouped by toolset |
| `/toolsets` | List available toolsets with descriptions |
| `/model [provider:model]` | Show or change the current model (supports `provider:model` syntax) |
| `/provider` | Show available providers with auth status |
| `/config` | Show current configuration |
| `/prompt [text]` | View/set/clear custom system prompt |
| `/personality [name]` | Set a predefined personality |

### Conversation Management

| Command | Description |
|---------|-------------|
| `/history` | Show conversation history |
| `/retry` | Retry the last message |
| `/undo` | Remove the last user/assistant exchange |
| `/save` | Save the current conversation |
| `/compress` | Manually compress conversation context |
| `/usage` | Show token usage for this session |
| `/insights [--days N]` | Show usage insights and analytics (last 30 days) |

### Skills & Scheduling

| Command | Description |
|---------|-------------|
| `/cron` | Manage scheduled tasks |
| `/skills` | Browse, search, install, inspect, or manage skills |
| `/platforms` | Show gateway/messaging platform status |
| `/verbose` | Cycle tool progress display: off → new → all → verbose |
| `/<skill-name>` | Invoke any installed skill (e.g., `/axolotl`, `/gif-search`) |

:::tip
Commands are case-insensitive — `/HELP` works the same as `/help`. Most commands work mid-conversation.
:::

## Skill Slash Commands

Every installed skill in `~/.hermes/skills/` is automatically registered as a slash command. The skill name becomes the command:

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

## Personalities

Set a predefined personality to change the agent's tone:

```
/personality pirate
/personality kawaii
/personality concise
```

Built-in personalities include: `helpful`, `concise`, `technical`, `creative`, `teacher`, `kawaii`, `catgirl`, `pirate`, `shakespeare`, `surfer`, `noir`, `uwu`, `philosopher`, `hype`.

You can also define custom personalities in `~/.hermes/config.yaml`:

```yaml
agent:
  personalities:
    helpful: "You are a helpful, friendly AI assistant."
    kawaii: "You are a kawaii assistant! Use cute expressions..."
    pirate: "Arrr! Ye be talkin' to Captain Hermes..."
    # Add your own!
```

## Multi-line Input

There are two ways to enter multi-line messages:

1. **`Alt+Enter` or `Ctrl+J`** — inserts a new line
2. **Backslash continuation** — end a line with `\` to continue:

```
❯ Write a function that:\
  1. Takes a list of numbers\
  2. Returns the sum
```

:::info
Pasting multi-line text is supported — use `Alt+Enter` or `Ctrl+J` to insert newlines, or simply paste content directly.
:::

## Interrupting the Agent

You can interrupt the agent at any point:

- **Type a new message + Enter** while the agent is working — it interrupts and processes your new instructions
- **`Ctrl+C`** — interrupt the current operation (press twice within 2s to force exit)
- In-progress terminal commands are killed immediately (SIGTERM, then SIGKILL after 1s)
- Multiple messages typed during interrupt are combined into one prompt

## Tool Progress Display

The CLI shows animated feedback as the agent works:

**Thinking animation** (during API calls):
```
  ◜ (｡•́︿•̀｡) pondering... (1.2s)
  ◠ (⊙_⊙) contemplating... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ got it! (3.1s)
```

**Tool execution feed:**
```
  ┊ 💻 terminal `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

Cycle through display modes with `/verbose`: `off → new → all → verbose`.

## Session Management

### Resuming Sessions

When you exit a CLI session, a resume command is printed:

```
Resume this session with:
  hermes --resume 20260225_143052_a1b2c3

Session:        20260225_143052_a1b2c3
Duration:       12m 34s
Messages:       28 (5 user, 18 tool calls)
```

Resume options:

```bash
hermes --continue                          # Resume the most recent CLI session
hermes -c                                  # Short form
hermes --resume 20260225_143052_a1b2c3     # Resume a specific session by ID
hermes -r 20260225_143052_a1b2c3           # Short form
```

Resuming restores the full conversation history from SQLite. The agent sees all previous messages, tool calls, and responses — just as if you never left.

Use `hermes sessions list` to browse past sessions.

### Session Logging

Sessions are automatically logged to `~/.hermes/sessions/`:

```
sessions/
├── session_20260201_143052_a1b2c3.json
├── session_20260201_150217_d4e5f6.json
└── ...
```

### Context Compression

Long conversations are automatically summarized when approaching context limits:

```yaml
# In ~/.hermes/config.yaml
compression:
  enabled: true
  threshold: 0.85    # Compress at 85% of context limit
  summary_model: "google/gemini-3-flash-preview"  # Model used for summarization
```

When compression triggers, middle turns are summarized while the first 3 and last 4 turns are always preserved.

## Quiet Mode

By default, the CLI runs in quiet mode which:
- Suppresses verbose logging from tools
- Enables kawaii-style animated feedback
- Keeps output clean and user-friendly

For debug output:
```bash
hermes chat --verbose
```



================================================
FILE: website/docs/user-guide/configuration.md
================================================
---
sidebar_position: 2
title: "Configuration"
description: "Configure Hermes Agent — config.yaml, providers, models, API keys, and more"
---

# Configuration

All settings are stored in the `~/.hermes/` directory for easy access.

## Directory Structure

```text
~/.hermes/
├── config.yaml     # Settings (model, terminal, TTS, compression, etc.)
├── .env            # API keys and secrets
├── auth.json       # OAuth provider credentials (Nous Portal, etc.)
├── SOUL.md         # Optional: global persona (agent embodies this personality)
├── memories/       # Persistent memory (MEMORY.md, USER.md)
├── skills/         # Agent-created skills (managed via skill_manage tool)
├── cron/           # Scheduled jobs
├── sessions/       # Gateway sessions
└── logs/           # Logs (errors.log, gateway.log — secrets auto-redacted)
```

## Managing Configuration

```bash
hermes config              # View current configuration
hermes config edit         # Open config.yaml in your editor
hermes config set KEY VAL  # Set a specific value
hermes config check        # Check for missing options (after updates)
hermes config migrate      # Interactively add missing options

# Examples:
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # Saves to .env
```

:::tip
The `hermes config set` command automatically routes values to the right file — API keys are saved to `.env`, everything else to `config.yaml`.
:::

## Configuration Precedence

Settings are resolved in this order (highest priority first):

1. **CLI arguments** — e.g., `hermes chat --model anthropic/claude-sonnet-4` (per-invocation override)
2. **`~/.hermes/config.yaml`** — the primary config file for all non-secret settings
3. **`~/.hermes/.env`** — fallback for env vars; **required** for secrets (API keys, tokens, passwords)
4. **Built-in defaults** — hardcoded safe defaults when nothing else is set

:::info Rule of Thumb
Secrets (API keys, bot tokens, passwords) go in `.env`. Everything else (model, terminal backend, compression settings, memory limits, toolsets) goes in `config.yaml`. When both are set, `config.yaml` wins for non-secret settings.
:::

## Inference Providers

You need at least one way to connect to an LLM. Use `hermes model` to switch providers and models interactively, or configure directly:

| Provider | Setup |
|----------|-------|
| **Nous Portal** | `hermes model` (OAuth, subscription-based) |
| **OpenAI Codex** | `hermes model` (ChatGPT OAuth, uses Codex models) |
| **OpenRouter** | `OPENROUTER_API_KEY` in `~/.hermes/.env` |
| **z.ai / GLM** | `GLM_API_KEY` in `~/.hermes/.env` (provider: `zai`) |
| **Kimi / Moonshot** | `KIMI_API_KEY` in `~/.hermes/.env` (provider: `kimi-coding`) |
| **MiniMax** | `MINIMAX_API_KEY` in `~/.hermes/.env` (provider: `minimax`) |
| **MiniMax China** | `MINIMAX_CN_API_KEY` in `~/.hermes/.env` (provider: `minimax-cn`) |
| **Custom Endpoint** | `OPENAI_BASE_URL` + `OPENAI_API_KEY` in `~/.hermes/.env` |

:::info Codex Note
The OpenAI Codex provider authenticates via device code (open a URL, enter a code). Credentials are stored at `~/.codex/auth.json` and auto-refresh. No Codex CLI installation required.
:::

:::warning
Even when using Nous Portal, Codex, or a custom endpoint, some tools (vision, web summarization, MoA) use OpenRouter independently. An `OPENROUTER_API_KEY` enables these tools.
:::

### First-Class Chinese AI Providers

These providers have built-in support with dedicated provider IDs. Set the API key and use `--provider` to select:

```bash
# z.ai / ZhipuAI GLM
hermes chat --provider zai --model glm-4-plus
# Requires: GLM_API_KEY in ~/.hermes/.env

# Kimi / Moonshot AI
hermes chat --provider kimi-coding --model moonshot-v1-auto
# Requires: KIMI_API_KEY in ~/.hermes/.env

# MiniMax (global endpoint)
hermes chat --provider minimax --model MiniMax-Text-01
# Requires: MINIMAX_API_KEY in ~/.hermes/.env

# MiniMax (China endpoint)
hermes chat --provider minimax-cn --model MiniMax-Text-01
# Requires: MINIMAX_CN_API_KEY in ~/.hermes/.env
```

Or set the provider permanently in `config.yaml`:
```yaml
model:
  provider: "zai"       # or: kimi-coding, minimax, minimax-cn
  default: "glm-4-plus"
```

Base URLs can be overridden with `GLM_BASE_URL`, `KIMI_BASE_URL`, `MINIMAX_BASE_URL`, or `MINIMAX_CN_BASE_URL` environment variables.

## Custom & Self-Hosted LLM Providers

Hermes Agent works with **any OpenAI-compatible API endpoint**. If a server implements `/v1/chat/completions`, you can point Hermes at it. This means you can use local models, GPU inference servers, multi-provider routers, or any third-party API.

### General Setup

Two ways to configure a custom endpoint:

**Interactive (recommended):**
```bash
hermes model
# Select "Custom endpoint (self-hosted / VLLM / etc.)"
# Enter: API base URL, API key, Model name
```

**Manual (`.env` file):**
```bash
# Add to ~/.hermes/.env
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=your-key-or-dummy
LLM_MODEL=your-model-name
```

Everything below follows this same pattern — just change the URL, key, and model name.

---

### Ollama — Local Models, Zero Config

[Ollama](https://ollama.com/) runs open-weight models locally with one command. Best for: quick local experimentation, privacy-sensitive work, offline use.

```bash
# Install and run a model
ollama pull llama3.1:70b
ollama serve   # Starts on port 11434

# Configure Hermes
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama           # Any non-empty string
LLM_MODEL=llama3.1:70b
```

Ollama's OpenAI-compatible endpoint supports chat completions, streaming, and tool calling (for supported models). No GPU required for smaller models — Ollama handles CPU inference automatically.

:::tip
List available models with `ollama list`. Pull any model from the [Ollama library](https://ollama.com/library) with `ollama pull <model>`.
:::

---

### vLLM — High-Performance GPU Inference

[vLLM](https://docs.vllm.ai/) is the standard for production LLM serving. Best for: maximum throughput on GPU hardware, serving large models, continuous batching.

```bash
# Start vLLM server
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --tensor-parallel-size 2    # Multi-GPU

# Configure Hermes
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=dummy
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct
```

vLLM supports tool calling, structured output, and multi-modal models. Use `--enable-auto-tool-choice` and `--tool-call-parser hermes` for Hermes-format tool calling with NousResearch models.

---

### SGLang — Fast Serving with RadixAttention

[SGLang](https://github.com/sgl-project/sglang) is an alternative to vLLM with RadixAttention for KV cache reuse. Best for: multi-turn conversations (prefix caching), constrained decoding, structured output.

```bash
# Start SGLang server
pip install sglang[all]
python -m sglang.launch_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --tp 2

# Configure Hermes
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=dummy
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct
```

---

### llama.cpp / llama-server — CPU & Metal Inference

[llama.cpp](https://github.com/ggml-org/llama.cpp) runs quantized models on CPU, Apple Silicon (Metal), and consumer GPUs. Best for: running models without a datacenter GPU, Mac users, edge deployment.

```bash
# Build and start llama-server
cmake -B build && cmake --build build --config Release
./build/bin/llama-server \
  -m models/llama-3.1-8b-instruct-Q4_K_M.gguf \
  --port 8080 --host 0.0.0.0

# Configure Hermes
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_API_KEY=dummy
LLM_MODEL=llama-3.1-8b-instruct
```

:::tip
Download GGUF models from [Hugging Face](https://huggingface.co/models?library=gguf). Q4_K_M quantization offers the best balance of quality vs. memory usage.
:::

---

### LiteLLM Proxy — Multi-Provider Gateway

[LiteLLM](https://docs.litellm.ai/) is an OpenAI-compatible proxy that unifies 100+ LLM providers behind a single API. Best for: switching between providers without config changes, load balancing, fallback chains, budget controls.

```bash
# Install and start
pip install litellm[proxy]
litellm --model anthropic/claude-sonnet-4 --port 4000

# Or with a config file for multiple models:
litellm --config litellm_config.yaml --port 4000

# Configure Hermes
OPENAI_BASE_URL=http://localhost:4000/v1
OPENAI_API_KEY=sk-your-litellm-key
LLM_MODEL=anthropic/claude-sonnet-4
```

Example `litellm_config.yaml` with fallback:
```yaml
model_list:
  - model_name: "best"
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: sk-ant-...
  - model_name: "best"
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...
router_settings:
  routing_strategy: "latency-based-routing"
```

---

### ClawRouter — Cost-Optimized Routing

[ClawRouter](https://github.com/BlockRunAI/ClawRouter) by BlockRunAI is a local routing proxy that auto-selects models based on query complexity. It classifies requests across 14 dimensions and routes to the cheapest model that can handle the task. Payment is via USDC cryptocurrency (no API keys).

```bash
# Install and start
npx @blockrun/clawrouter    # Starts on port 8402

# Configure Hermes
OPENAI_BASE_URL=http://localhost:8402/v1
OPENAI_API_KEY=dummy
LLM_MODEL=blockrun/auto     # or: blockrun/eco, blockrun/premium, blockrun/agentic
```

Routing profiles:
| Profile | Strategy | Savings |
|---------|----------|---------|
| `blockrun/auto` | Balanced quality/cost | 74-100% |
| `blockrun/eco` | Cheapest possible | 95-100% |
| `blockrun/premium` | Best quality models | 0% |
| `blockrun/free` | Free models only | 100% |
| `blockrun/agentic` | Optimized for tool use | varies |

:::note
ClawRouter requires a USDC-funded wallet on Base or Solana for payment. All requests route through BlockRun's backend API. Run `npx @blockrun/clawrouter doctor` to check wallet status.
:::

---

### Other Compatible Providers

Any service with an OpenAI-compatible API works. Some popular options:

| Provider | Base URL | Notes |
|----------|----------|-------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | Cloud-hosted open models |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | Ultra-fast inference |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek models |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | Fast open model hosting |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | Wafer-scale chip inference |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral models |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | Direct OpenAI access |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | Enterprise OpenAI |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | Self-hosted, multi-model |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | Desktop app with local models |

```bash
# Example: Together AI
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_API_KEY=your-together-key
LLM_MODEL=meta-llama/Llama-3.1-70B-Instruct-Turbo
```

---

### Choosing the Right Setup

| Use Case | Recommended |
|----------|-------------|
| **Just want it to work** | OpenRouter (default) or Nous Portal |
| **Local models, easy setup** | Ollama |
| **Production GPU serving** | vLLM or SGLang |
| **Mac / no GPU** | Ollama or llama.cpp |
| **Multi-provider routing** | LiteLLM Proxy or OpenRouter |
| **Cost optimization** | ClawRouter or OpenRouter with `sort: "price"` |
| **Maximum privacy** | Ollama, vLLM, or llama.cpp (fully local) |
| **Enterprise / Azure** | Azure OpenAI with custom endpoint |
| **Chinese AI models** | z.ai (GLM), Kimi/Moonshot, or MiniMax (first-class providers) |

:::tip
You can switch between providers at any time with `hermes model` — no restart required. Your conversation history, memory, and skills carry over regardless of which provider you use.
:::

## Optional API Keys

| Feature | Provider | Env Variable |
|---------|----------|--------------|
| Web scraping | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY` |
| Browser automation | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| Image generation | [FAL](https://fal.ai/) | `FAL_KEY` |
| Premium TTS voices | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI TTS + voice transcription | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| RL Training | [Tinker](https://tinker-console.thinkingmachines.ai/) + [WandB](https://wandb.ai/) | `TINKER_API_KEY`, `WANDB_API_KEY` |
| Cross-session user modeling | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |

### Self-Hosting Firecrawl

By default, Hermes uses the [Firecrawl cloud API](https://firecrawl.dev/) for web search and scraping. If you prefer to run Firecrawl locally, you can point Hermes at a self-hosted instance instead.

**What you get:** No API key required, no rate limits, no per-page costs, full data sovereignty.

**What you lose:** The cloud version uses Firecrawl's proprietary "Fire-engine" for advanced anti-bot bypassing (Cloudflare, CAPTCHAs, IP rotation). Self-hosted uses basic fetch + Playwright, so some protected sites may fail. Search uses DuckDuckGo instead of Google.

**Setup:**

1. Clone and start the Firecrawl Docker stack (5 containers: API, Playwright, Redis, RabbitMQ, PostgreSQL — requires ~4-8 GB RAM):
   ```bash
   git clone https://github.com/mendableai/firecrawl
   cd firecrawl
   # In .env, set: USE_DB_AUTHENTICATION=false
   docker compose up -d
   ```

2. Point Hermes at your instance (no API key needed):
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```

You can also set both `FIRECRAWL_API_KEY` and `FIRECRAWL_API_URL` if your self-hosted instance has authentication enabled.

## OpenRouter Provider Routing

When using OpenRouter, you can control how requests are routed across providers. Add a `provider_routing` section to `~/.hermes/config.yaml`:

```yaml
provider_routing:
  sort: "throughput"          # "price" (default), "throughput", or "latency"
  # only: ["anthropic"]      # Only use these providers
  # ignore: ["deepinfra"]    # Skip these providers
  # order: ["anthropic", "google"]  # Try providers in this order
  # require_parameters: true  # Only use providers that support all request params
  # data_collection: "deny"   # Exclude providers that may store/train on data
```

**Shortcuts:** Append `:nitro` to any model name for throughput sorting (e.g., `anthropic/claude-sonnet-4:nitro`), or `:floor` for price sorting.

## Terminal Backend Configuration

Configure which environment the agent uses for terminal commands:

```yaml
terminal:
  backend: local    # or: docker, ssh, singularity, modal, daytona
  cwd: "."          # Working directory ("." = current dir)
  timeout: 180      # Command timeout in seconds
```

See [Code Execution](features/code-execution.md) and the [Terminal section of the README](features/tools.md) for details on each backend.

## Memory Configuration

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
```

## Git Worktree Isolation

Enable isolated git worktrees for running multiple agents in parallel on the same repo:

```yaml
worktree: true    # Always create a worktree (same as hermes -w)
# worktree: false # Default — only when -w flag is passed
```

When enabled, each CLI session creates a fresh worktree under `.worktrees/` with its own branch. Agents can edit files, commit, push, and create PRs without interfering with each other. Clean worktrees are removed on exit; dirty ones are kept for manual recovery.

You can also list gitignored files to copy into worktrees via `.worktreeinclude` in your repo root:

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## Context Compression

```yaml
compression:
  enabled: true
  threshold: 0.85    # Compress at 85% of context limit
```

## Reasoning Effort

Control how much "thinking" the model does before responding:

```yaml
agent:
  reasoning_effort: ""   # empty = medium (default). Options: xhigh (max), high, medium, low, minimal, none
```

When unset (default), reasoning effort defaults to "medium" — a balanced level that works well for most tasks. Setting a value overrides it — higher reasoning effort gives better results on complex tasks at the cost of more tokens and latency.

## TTS Configuration

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai"
  edge:
    voice: "en-US-AriaNeural"   # 322 voices, 74 languages
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
```

## Display Settings

```yaml
display:
  tool_progress: all    # off | new | all | verbose
  personality: "kawaii"  # Default personality for the CLI
  compact: false         # Compact output mode (less whitespace)
```

| Mode | What you see |
|------|-------------|
| `off` | Silent — just the final response |
| `new` | Tool indicator only when the tool changes |
| `all` | Every tool call with a short preview (default) |
| `verbose` | Full args, results, and debug logs |

## Speech-to-Text (STT)

```yaml
stt:
  provider: "openai"           # STT provider
```

Requires `VOICE_TOOLS_OPENAI_KEY` in `.env` for OpenAI STT.

## Human Delay

Simulate human-like response pacing in messaging platforms:

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 500                  # Minimum delay (custom mode)
  max_ms: 2000                 # Maximum delay (custom mode)
```

## Code Execution

Configure the sandboxed Python code execution tool:

```yaml
code_execution:
  timeout: 300                 # Max execution time in seconds
  max_tool_calls: 50           # Max tool calls within code execution
```

## Delegation

Configure subagent behavior for the delegate tool:

```yaml
delegation:
  max_iterations: 50           # Max iterations per subagent
  default_toolsets:             # Toolsets available to subagents
    - terminal
    - file
    - web
```

## Clarify

Configure the clarification prompt behavior:

```yaml
clarify:
  timeout: 120                 # Seconds to wait for user clarification response
```

## Context Files (SOUL.md, AGENTS.md)

Drop these files in your project directory and the agent automatically picks them up:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project-specific instructions, coding conventions |
| `SOUL.md` | Persona definition — the agent embodies this personality |
| `.cursorrules` | Cursor IDE rules (also detected) |
| `.cursor/rules/*.mdc` | Cursor rule files (also detected) |

- **AGENTS.md** is hierarchical: if subdirectories also have AGENTS.md, all are combined.
- **SOUL.md** checks cwd first, then `~/.hermes/SOUL.md` as a global fallback.
- All context files are capped at 20,000 characters with smart truncation.

## Working Directory

| Context | Default |
|---------|---------|
| **CLI (`hermes`)** | Current directory where you run the command |
| **Messaging gateway** | Home directory `~` (override with `MESSAGING_CWD`) |
| **Docker / Singularity / Modal / SSH** | User's home directory inside the container or remote machine |

Override the working directory:
```bash
# In ~/.hermes/.env or ~/.hermes/config.yaml:
MESSAGING_CWD=/home/myuser/projects    # Gateway sessions
TERMINAL_CWD=/workspace                # All terminal sessions
```



================================================
FILE: website/docs/user-guide/security.md
================================================
---
sidebar_position: 8
title: "Security"
description: "Security model, dangerous command approval, user authorization, container isolation, and production deployment best practices"
---

# Security

Hermes Agent is designed with a defense-in-depth security model. This page covers every security boundary — from command approval to container isolation to user authorization on messaging platforms.

## Overview

The security model has five layers:

1. **User authorization** — who can talk to the agent (allowlists, DM pairing)
2. **Dangerous command approval** — human-in-the-loop for destructive operations
3. **Container isolation** — Docker/Singularity/Modal sandboxing with hardened settings
4. **MCP credential filtering** — environment variable isolation for MCP subprocesses
5. **Context file scanning** — prompt injection detection in project files

## Dangerous Command Approval

Before executing any command, Hermes checks it against a curated list of dangerous patterns. If a match is found, the user must explicitly approve it.

### What Triggers Approval

The following patterns trigger approval prompts (defined in `tools/approval.py`):

| Pattern | Description |
|---------|-------------|
| `rm -r` / `rm --recursive` | Recursive delete |
| `rm ... /` | Delete in root path |
| `chmod 777` | World-writable permissions |
| `mkfs` | Format filesystem |
| `dd if=` | Disk copy |
| `DROP TABLE/DATABASE` | SQL DROP |
| `DELETE FROM` (without WHERE) | SQL DELETE without WHERE |
| `TRUNCATE TABLE` | SQL TRUNCATE |
| `> /etc/` | Overwrite system config |
| `systemctl stop/disable/mask` | Stop/disable system services |
| `kill -9 -1` | Kill all processes |
| `curl ... \| sh` | Pipe remote content to shell |
| `bash -c`, `python -e` | Shell/script execution via flags |
| `find -exec rm`, `find -delete` | Find with destructive actions |
| Fork bomb patterns | Fork bombs |

:::info
**Container bypass**: When running in `docker`, `singularity`, `modal`, or `daytona` backends, dangerous command checks are **skipped** because the container itself is the security boundary. Destructive commands inside a container can't harm the host.
:::

### Approval Flow (CLI)

In the interactive CLI, dangerous commands show an inline approval prompt:

```
  ⚠️  DANGEROUS COMMAND: recursive delete
      rm -rf /tmp/old-project

      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny

      Choice [o/s/a/D]:
```

The four options:

- **once** — allow this single execution
- **session** — allow this pattern for the rest of the session
- **always** — add to permanent allowlist (saved to `config.yaml`)
- **deny** (default) — block the command

### Approval Flow (Gateway/Messaging)

On messaging platforms, the agent sends the dangerous command details to the chat and waits for the user to reply:

- Reply **yes**, **y**, **approve**, **ok**, or **go** to approve
- Reply **no**, **n**, **deny**, or **cancel** to deny

The `HERMES_EXEC_ASK=1` environment variable is automatically set when running the gateway.

### Permanent Allowlist

Commands approved with "always" are saved to `~/.hermes/config.yaml`:

```yaml
# Permanently allowed dangerous command patterns
command_allowlist:
  - rm
  - systemctl
```

These patterns are loaded at startup and silently approved in all future sessions.

:::tip
Use `hermes config edit` to review or remove patterns from your permanent allowlist.
:::

## User Authorization (Gateway)

When running the messaging gateway, Hermes controls who can interact with the bot through a layered authorization system.

### Authorization Check Order

The `_is_user_authorized()` method checks in this order:

1. **Per-platform allow-all flag** (e.g., `DISCORD_ALLOW_ALL_USERS=true`)
2. **DM pairing approved list** (users approved via pairing codes)
3. **Platform-specific allowlists** (e.g., `TELEGRAM_ALLOWED_USERS=12345,67890`)
4. **Global allowlist** (`GATEWAY_ALLOWED_USERS=12345,67890`)
5. **Global allow-all** (`GATEWAY_ALLOW_ALL_USERS=true`)
6. **Default: deny**

### Platform Allowlists

Set allowed user IDs as comma-separated values in `~/.hermes/.env`:

```bash
# Platform-specific allowlists
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# Cross-platform allowlist (checked for all platforms)
GATEWAY_ALLOWED_USERS=123456789

# Per-platform allow-all (use with caution)
DISCORD_ALLOW_ALL_USERS=true

# Global allow-all (use with extreme caution)
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
If **no allowlists are configured** and `GATEWAY_ALLOW_ALL_USERS` is not set, **all users are denied**. The gateway logs a warning at startup:

```
No user allowlists configured. All unauthorized users will be denied.
Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```
:::

### DM Pairing System

For more flexible authorization, Hermes includes a code-based pairing system. Instead of requiring user IDs upfront, unknown users receive a one-time pairing code that the bot owner approves via the CLI.

**How it works:**

1. An unknown user sends a DM to the bot
2. The bot replies with an 8-character pairing code
3. The bot owner runs `hermes pairing approve <platform> <code>` on the CLI
4. The user is permanently approved for that platform

**Security features** (based on OWASP + NIST SP 800-63-4 guidance):

| Feature | Details |
|---------|---------|
| Code format | 8-char from 32-char unambiguous alphabet (no 0/O/1/I) |
| Randomness | Cryptographic (`secrets.choice()`) |
| Code TTL | 1 hour expiry |
| Rate limiting | 1 request per user per 10 minutes |
| Pending limit | Max 3 pending codes per platform |
| Lockout | 5 failed approval attempts → 1-hour lockout |
| File security | `chmod 0600` on all pairing data files |
| Logging | Codes are never logged to stdout |

**Pairing CLI commands:**

```bash
# List pending and approved users
hermes pairing list

# Approve a pairing code
hermes pairing approve telegram ABC12DEF

# Revoke a user's access
hermes pairing revoke telegram 123456789

# Clear all pending codes
hermes pairing clear-pending
```

**Storage:** Pairing data is stored in `~/.hermes/pairing/` with per-platform JSON files:
- `{platform}-pending.json` — pending pairing requests
- `{platform}-approved.json` — approved users
- `_rate_limits.json` — rate limit and lockout tracking

## Container Isolation

When using the `docker` terminal backend, Hermes applies strict security hardening to every container.

### Docker Security Flags

Every container runs with these flags (defined in `tools/environments/docker.py`):

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # Drop ALL Linux capabilities
    "--security-opt", "no-new-privileges",         # Block privilege escalation
    "--pids-limit", "256",                         # Limit process count
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # Size-limited /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # No-exec /var/tmp
    "--tmpfs", "/run:rw,noexec,nosuid,size=64m",   # No-exec /run
]
```

### Resource Limits

Container resources are configurable in `~/.hermes/config.yaml`:

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1        # CPU cores
  container_memory: 5120  # MB (default 5GB)
  container_disk: 51200   # MB (default 50GB, requires overlay2 on XFS)
  container_persistent: true  # Persist filesystem across sessions
```

### Filesystem Persistence

- **Persistent mode** (`container_persistent: true`): Bind-mounts `/workspace` and `/root` from `~/.hermes/sandboxes/docker/<task_id>/`
- **Ephemeral mode** (`container_persistent: false`): Uses tmpfs for workspace — everything is lost on cleanup

:::tip
For production gateway deployments, use `docker`, `modal`, or `daytona` backend to isolate agent commands from your host system. This eliminates the need for dangerous command approval entirely.
:::

## Terminal Backend Security Comparison

| Backend | Isolation | Dangerous Cmd Check | Best For |
|---------|-----------|-------------------|----------|
| **local** | None — runs on host | ✅ Yes | Development, trusted users |
| **ssh** | Remote machine | ✅ Yes | Running on a separate server |
| **docker** | Container | ❌ Skipped (container is boundary) | Production gateway |
| **singularity** | Container | ❌ Skipped | HPC environments |
| **modal** | Cloud sandbox | ❌ Skipped | Scalable cloud isolation |
| **daytona** | Cloud sandbox | ❌ Skipped | Persistent cloud workspaces |

## MCP Credential Handling

MCP (Model Context Protocol) server subprocesses receive a **filtered environment** to prevent accidental credential leakage.

### Safe Environment Variables

Only these variables are passed through from the host to MCP stdio subprocesses:

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

Plus any `XDG_*` variables. All other environment variables (API keys, tokens, secrets) are **stripped**.

Variables explicitly defined in the MCP server's `env` config are passed through:

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # Only this is passed
```

### Credential Redaction

Error messages from MCP tools are sanitized before being returned to the LLM. The following patterns are replaced with `[REDACTED]`:

- GitHub PATs (`ghp_...`)
- OpenAI-style keys (`sk-...`)
- Bearer tokens
- `token=`, `key=`, `API_KEY=`, `password=`, `secret=` parameters

### Context File Injection Protection

Context files (AGENTS.md, .cursorrules, SOUL.md) are scanned for prompt injection before being included in the system prompt. The scanner checks for:

- Instructions to ignore/disregard prior instructions
- Hidden HTML comments with suspicious keywords
- Attempts to read secrets (`.env`, `credentials`, `.netrc`)
- Credential exfiltration via `curl`
- Invisible Unicode characters (zero-width spaces, bidirectional overrides)

Blocked files show a warning:

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

## Best Practices for Production Deployment

### Gateway Deployment Checklist

1. **Set explicit allowlists** — never use `GATEWAY_ALLOW_ALL_USERS=true` in production
2. **Use container backend** — set `terminal.backend: docker` in config.yaml
3. **Restrict resource limits** — set appropriate CPU, memory, and disk limits
4. **Store secrets securely** — keep API keys in `~/.hermes/.env` with proper file permissions
5. **Enable DM pairing** — use pairing codes instead of hardcoding user IDs when possible
6. **Review command allowlist** — periodically audit `command_allowlist` in config.yaml
7. **Set `MESSAGING_CWD`** — don't let the agent operate from sensitive directories
8. **Run as non-root** — never run the gateway as root
9. **Monitor logs** — check `~/.hermes/logs/` for unauthorized access attempts
10. **Keep updated** — run `hermes update` regularly for security patches

### Securing API Keys

```bash
# Set proper permissions on the .env file
chmod 600 ~/.hermes/.env

# Keep separate keys for different services
# Never commit .env files to version control
```

### Network Isolation

For maximum security, run the gateway on a separate machine or VM:

```yaml
terminal:
  backend: ssh
  ssh_host: "agent-worker.local"
  ssh_user: "hermes"
  ssh_key: "~/.ssh/hermes_agent_key"
```

This keeps the gateway's messaging connections separate from the agent's command execution.



================================================
FILE: website/docs/user-guide/sessions.md
================================================
---
sidebar_position: 7
title: "Sessions"
description: "Session persistence, resume, search, management, and per-platform session tracking"
---

# Sessions

Hermes Agent automatically saves every conversation as a session. Sessions enable conversation resume, cross-session search, and full conversation history management.

## How Sessions Work

Every conversation — whether from the CLI, Telegram, Discord, WhatsApp, or Slack — is stored as a session with full message history. Sessions are tracked in two complementary systems:

1. **SQLite database** (`~/.hermes/state.db`) — structured session metadata with FTS5 full-text search
2. **JSONL transcripts** (`~/.hermes/sessions/`) — raw conversation transcripts including tool calls (gateway)

The SQLite database stores:
- Session ID, source platform, user ID
- Model name and configuration
- System prompt snapshot
- Full message history (role, content, tool calls, tool results)
- Token counts (input/output)
- Timestamps (started_at, ended_at)
- Parent session ID (for compression-triggered session splitting)

### Session Sources

Each session is tagged with its source platform:

| Source | Description |
|--------|-------------|
| `cli` | Interactive CLI (`hermes` or `hermes chat`) |
| `telegram` | Telegram messenger |
| `discord` | Discord server/DM |
| `whatsapp` | WhatsApp messenger |
| `slack` | Slack workspace |

## CLI Session Resume

Resume previous conversations from the CLI using `--continue` or `--resume`:

### Continue Last Session

```bash
# Resume the most recent CLI session
hermes --continue
hermes -c

# Or with the chat subcommand
hermes chat --continue
hermes chat -c
```

This looks up the most recent `cli` session from the SQLite database and loads its full conversation history.

### Resume Specific Session

```bash
# Resume a specific session by ID
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# Or with the chat subcommand
hermes chat --resume 20250305_091523_a1b2c3d4
```

Session IDs are shown when you exit a CLI session, and can be found with `hermes sessions list`.

:::tip
Session IDs follow the format `YYYYMMDD_HHMMSS_<8-char-hex>`, e.g. `20250305_091523_a1b2c3d4`. You only need to provide enough of the ID to be unique.
:::

## Session Management Commands

Hermes provides a full set of session management commands via `hermes sessions`:

### List Sessions

```bash
# List recent sessions (default: last 20)
hermes sessions list

# Filter by platform
hermes sessions list --source telegram

# Show more sessions
hermes sessions list --limit 50
```

Output format:

```
ID                             Source       Model                          Messages Started
────────────────────────────────────────────────────────────────────────────────────────────────
20250305_091523_a1b2c3d4       cli          anthropic/claude-opus-4.6          24 2025-03-05 09:15
20250304_143022_e5f6g7h8       telegram     anthropic/claude-opus-4.6          12 2025-03-04 14:30 (ended)
```

### Export Sessions

```bash
# Export all sessions to a JSONL file
hermes sessions export backup.jsonl

# Export sessions from a specific platform
hermes sessions export telegram-history.jsonl --source telegram

# Export a single session
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

Exported files contain one JSON object per line with full session metadata and all messages.

### Delete a Session

```bash
# Delete a specific session (with confirmation)
hermes sessions delete 20250305_091523_a1b2c3d4

# Delete without confirmation
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### Prune Old Sessions

```bash
# Delete ended sessions older than 90 days (default)
hermes sessions prune

# Custom age threshold
hermes sessions prune --older-than 30

# Only prune sessions from a specific platform
hermes sessions prune --source telegram --older-than 60

# Skip confirmation
hermes sessions prune --older-than 30 --yes
```

:::info
Pruning only deletes **ended** sessions (sessions that have been explicitly ended or auto-reset). Active sessions are never pruned.
:::

### Session Statistics

```bash
hermes sessions stats
```

Output:

```
Total sessions: 142
Total messages: 3847
  cli: 89 sessions
  telegram: 38 sessions
  discord: 15 sessions
Database size: 12.4 MB
```

For deeper analytics — token usage, cost estimates, tool breakdown, and activity patterns — use [`hermes insights`](/docs/reference/cli-commands#insights).

## Session Search Tool

The agent has a built-in `session_search` tool that performs full-text search across all past conversations using SQLite's FTS5 engine.

### How It Works

1. FTS5 searches matching messages ranked by relevance
2. Groups results by session, takes the top N unique sessions (default 3)
3. Loads each session's conversation, truncates to ~100K chars centered on matches
4. Sends to a fast summarization model for focused summaries
5. Returns per-session summaries with metadata and surrounding context

### FTS5 Query Syntax

The search supports standard FTS5 query syntax:

- Simple keywords: `docker deployment`
- Phrases: `"exact phrase"`
- Boolean: `docker OR kubernetes`, `python NOT java`
- Prefix: `deploy*`

### When It's Used

The agent is prompted to use session search automatically:

> *"When the user references something from a past conversation or you suspect relevant prior context exists, use session_search to recall it before asking them to repeat themselves."*

## Per-Platform Session Tracking

### Gateway Sessions

On messaging platforms, sessions are keyed by a deterministic session key built from the message source:

| Chat Type | Key Format | Example |
|-----------|-----------|---------|
| Telegram DM | `agent:main:telegram:dm` | One session per bot |
| Discord DM | `agent:main:discord:dm` | One session per bot |
| WhatsApp DM | `agent:main:whatsapp:dm:<chat_id>` | Per-user (multi-user) |
| Group chat | `agent:main:<platform>:group:<chat_id>` | Per-group |
| Channel | `agent:main:<platform>:channel:<chat_id>` | Per-channel |

:::info
WhatsApp DMs include the chat ID in the session key because multiple users can DM the bot. Other platforms use a single DM session since the bot is configured per-user via allowlists.
:::

### Session Reset Policies

Gateway sessions are automatically reset based on configurable policies:

- **idle** — reset after N minutes of inactivity
- **daily** — reset at a specific hour each day
- **both** — reset on whichever comes first (idle or daily)
- **none** — never auto-reset

Before a session is auto-reset, the agent is given a turn to save any important memories or skills from the conversation.

Sessions with **active background processes** are never auto-reset, regardless of policy.

## Storage Locations

| What | Path | Description |
|------|------|-------------|
| SQLite database | `~/.hermes/state.db` | All session metadata + messages with FTS5 |
| Gateway transcripts | `~/.hermes/sessions/` | JSONL transcripts per session + sessions.json index |
| Gateway index | `~/.hermes/sessions/sessions.json` | Maps session keys to active session IDs |

The SQLite database uses WAL mode for concurrent readers and a single writer, which suits the gateway's multi-platform architecture well.

### Database Schema

Key tables in `state.db`:

- **sessions** — session metadata (id, source, user_id, model, timestamps, token counts)
- **messages** — full message history (role, content, tool_calls, tool_name, token_count)
- **messages_fts** — FTS5 virtual table for full-text search across message content

## Session Expiry and Cleanup

### Automatic Cleanup

- Gateway sessions auto-reset based on the configured reset policy
- Before reset, the agent saves memories and skills from the expiring session
- Ended sessions remain in the database until pruned

### Manual Cleanup

```bash
# Prune sessions older than 90 days
hermes sessions prune

# Delete a specific session
hermes sessions delete <session_id>

# Export before pruning (backup)
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```

:::tip
The database grows slowly (typical: 10-15 MB for hundreds of sessions). Pruning is mainly useful for removing old conversations you no longer need for search recall.
:::



================================================
FILE: website/docs/user-guide/features/_category_.json
================================================
{
  "label": "Features",
  "position": 4,
  "link": {
    "type": "generated-index",
    "description": "Explore the powerful features of Hermes Agent."
  }
}



================================================
FILE: website/docs/user-guide/features/batch-processing.md
================================================
---
sidebar_position: 12
title: "Batch Processing"
description: "Generate agent trajectories at scale — parallel processing, checkpointing, and toolset distributions"
---

# Batch Processing

Batch processing lets you run the Hermes agent across hundreds or thousands of prompts in parallel, generating structured trajectory data. This is primarily used for **training data generation** — producing ShareGPT-format trajectories with tool usage statistics that can be used for fine-tuning or evaluation.

## Overview

The batch runner (`batch_runner.py`) processes a JSONL dataset of prompts, running each through a full agent session with tool access. Each prompt gets its own isolated environment. The output is structured trajectory data with full conversation history, tool call statistics, and reasoning coverage metrics.

## Quick Start

```bash
# Basic batch run
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --model=anthropic/claude-sonnet-4-20250514 \
    --num_workers=4

# Resume an interrupted run
python batch_runner.py \
    --dataset_file=data/prompts.jsonl \
    --batch_size=10 \
    --run_name=my_first_run \
    --resume

# List available toolset distributions
python batch_runner.py --list_distributions
```

## Dataset Format

The input dataset is a JSONL file (one JSON object per line). Each entry must have a `prompt` field:

```jsonl
{"prompt": "Write a Python function that finds the longest palindromic substring"}
{"prompt": "Create a REST API endpoint for user authentication using Flask"}
{"prompt": "Debug this error: TypeError: cannot unpack non-iterable NoneType object"}
```

Entries can optionally include:
- `image` or `docker_image`: A container image to use for this prompt's sandbox (works with Docker, Modal, and Singularity backends)
- `cwd`: Working directory override for the task's terminal session

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset_file` | (required) | Path to JSONL dataset |
| `--batch_size` | (required) | Prompts per batch |
| `--run_name` | (required) | Name for this run (used for output dir and checkpointing) |
| `--distribution` | `"default"` | Toolset distribution to sample from |
| `--model` | `claude-sonnet-4-20250514` | Model to use |
| `--base_url` | `https://openrouter.ai/api/v1` | API base URL |
| `--api_key` | (env var) | API key for model |
| `--max_turns` | `10` | Maximum tool-calling iterations per prompt |
| `--num_workers` | `4` | Parallel worker processes |
| `--resume` | `false` | Resume from checkpoint |
| `--verbose` | `false` | Enable verbose logging |
| `--max_samples` | all | Only process first N samples from dataset |
| `--max_tokens` | model default | Maximum tokens per model response |

### Provider Routing (OpenRouter)

| Parameter | Description |
|-----------|-------------|
| `--providers_allowed` | Comma-separated providers to allow (e.g., `"anthropic,openai"`) |
| `--providers_ignored` | Comma-separated providers to ignore (e.g., `"together,deepinfra"`) |
| `--providers_order` | Comma-separated preferred provider order |
| `--provider_sort` | Sort by `"price"`, `"throughput"`, or `"latency"` |

### Reasoning Control

| Parameter | Description |
|-----------|-------------|
| `--reasoning_effort` | Effort level: `xhigh`, `high`, `medium`, `low`, `minimal`, `none` |
| `--reasoning_disabled` | Completely disable reasoning/thinking tokens |

### Advanced Options

| Parameter | Description |
|-----------|-------------|
| `--ephemeral_system_prompt` | System prompt used during execution but NOT saved to trajectories |
| `--log_prefix_chars` | Characters to show in log previews (default: 100) |
| `--prefill_messages_file` | Path to JSON file with prefill messages for few-shot priming |

## Toolset Distributions

Each prompt gets a randomly sampled set of toolsets from a **distribution**. This ensures training data covers diverse tool combinations. Use `--list_distributions` to see all available distributions.

Distributions define probability weights for each toolset combination. For example, a "default" distribution might assign high probability to `["terminal", "file", "web"]` and lower probability to web-only or file-only combinations.

## Output Format

All output goes to `data/<run_name>/`:

```
data/my_run/
├── trajectories.jsonl    # Combined final output (all batches merged)
├── batch_0.jsonl         # Individual batch results
├── batch_1.jsonl
├── ...
├── checkpoint.json       # Resume checkpoint
└── statistics.json       # Aggregate tool usage stats
```

### Trajectory Format

Each line in `trajectories.jsonl` is a JSON object:

```json
{
  "prompt_index": 42,
  "conversations": [
    {"from": "human", "value": "Write a function..."},
    {"from": "gpt", "value": "I'll create that function...",
     "tool_calls": [...]},
    {"from": "tool", "value": "..."},
    {"from": "gpt", "value": "Here's the completed function..."}
  ],
  "metadata": {
    "batch_num": 2,
    "timestamp": "2026-01-15T10:30:00",
    "model": "anthropic/claude-sonnet-4-20250514"
  },
  "completed": true,
  "partial": false,
  "api_calls": 3,
  "toolsets_used": ["terminal", "file"],
  "tool_stats": {
    "terminal": {"count": 2, "success": 2, "failure": 0},
    "read_file": {"count": 1, "success": 1, "failure": 0}
  },
  "tool_error_counts": {
    "terminal": 0,
    "read_file": 0
  }
}
```

The `conversations` field uses a ShareGPT-like format with `from` and `value` fields. Tool stats are normalized to include all possible tools with zero defaults, ensuring consistent schema across entries for HuggingFace datasets compatibility.

## Checkpointing

The batch runner has robust checkpointing for fault tolerance:

- **Checkpoint file:** Saved after each batch completes, tracking which prompt indices are done
- **Content-based resume:** On `--resume`, the runner scans existing batch files and matches completed prompts by their actual text content (not just indices), enabling recovery even if the dataset order changes
- **Failed prompts:** Only successfully completed prompts are marked as done — failed prompts will be retried on resume
- **Batch merging:** On completion, all batch files (including from previous runs) are merged into a single `trajectories.jsonl`

### How Resume Works

1. Scan all `batch_*.jsonl` files for completed prompts (by content matching)
2. Filter the dataset to exclude already-completed prompts
3. Re-batch the remaining prompts
4. Process only the remaining prompts
5. Merge all batch files (old + new) into final output

## Quality Filtering

The batch runner applies automatic quality filtering:

- **No-reasoning filter:** Samples where zero assistant turns contain reasoning (no `<REASONING_SCRATCHPAD>` or native thinking tokens) are discarded
- **Corrupted entry filter:** Entries with hallucinated tool names (not in the valid tool list) are filtered out during the final merge
- **Reasoning statistics:** Tracks percentage of turns with/without reasoning across the entire run

## Statistics

After completion, the runner prints comprehensive statistics:

- **Tool usage:** Call counts, success/failure rates per tool
- **Reasoning coverage:** Percentage of assistant turns with reasoning
- **Samples discarded:** Count of samples filtered for lacking reasoning
- **Duration:** Total processing time

Statistics are also saved to `statistics.json` for programmatic analysis.

## Use Cases

### Training Data Generation

Generate diverse tool-use trajectories for fine-tuning:

```bash
python batch_runner.py \
    --dataset_file=data/coding_prompts.jsonl \
    --batch_size=20 \
    --run_name=coding_v1 \
    --model=anthropic/claude-sonnet-4-20250514 \
    --num_workers=8 \
    --distribution=default \
    --max_turns=15
```

### Model Evaluation

Evaluate how well a model uses tools across standardized prompts:

```bash
python batch_runner.py \
    --dataset_file=data/eval_suite.jsonl \
    --batch_size=10 \
    --run_name=eval_gpt4 \
    --model=openai/gpt-4o \
    --num_workers=4 \
    --max_turns=10
```

### Per-Prompt Container Images

For benchmarks requiring specific environments, each prompt can specify its own container image:

```jsonl
{"prompt": "Install numpy and compute eigenvalues of a 3x3 matrix", "image": "python:3.11-slim"}
{"prompt": "Compile this Rust program and run it", "image": "rust:1.75"}
{"prompt": "Set up a Node.js Express server", "image": "node:20-alpine", "cwd": "/app"}
```

The batch runner verifies Docker images are accessible before running each prompt.



================================================
FILE: website/docs/user-guide/features/browser.md
================================================
---
title: Browser Automation
description: Control cloud browsers with Browserbase integration for web interaction, form filling, scraping, and more.
sidebar_label: Browser
sidebar_position: 5
---

# Browser Automation

Hermes Agent includes a full browser automation toolset powered by [Browserbase](https://browserbase.com), enabling the agent to navigate websites, interact with page elements, fill forms, and extract information — all running in cloud-hosted browsers with built-in anti-bot stealth features.

## Overview

The browser tools use the `agent-browser` CLI with Browserbase cloud execution. Pages are represented as **accessibility trees** (text-based snapshots), making them ideal for LLM agents. Interactive elements get ref IDs (like `@e1`, `@e2`) that the agent uses for clicking and typing.

Key capabilities:

- **Cloud execution** — no local browser needed
- **Built-in stealth** — random fingerprints, CAPTCHA solving, residential proxies
- **Session isolation** — each task gets its own browser session
- **Automatic cleanup** — inactive sessions are closed after a timeout
- **Vision analysis** — screenshot + AI analysis for visual understanding

## Setup

### Required Environment Variables

```bash
# Add to ~/.hermes/.env
BROWSERBASE_API_KEY=your-api-key-here
BROWSERBASE_PROJECT_ID=your-project-id-here
```

Get your credentials at [browserbase.com](https://browserbase.com).

### Optional Environment Variables

```bash
# Residential proxies for better CAPTCHA solving (default: "true")
BROWSERBASE_PROXIES=true

# Advanced stealth with custom Chromium — requires Scale Plan (default: "false")
BROWSERBASE_ADVANCED_STEALTH=false

# Session reconnection after disconnects — requires paid plan (default: "true")
BROWSERBASE_KEEP_ALIVE=true

# Custom session timeout in milliseconds (default: project default)
# Examples: 600000 (10min), 1800000 (30min)
BROWSERBASE_SESSION_TIMEOUT=600000

# Inactivity timeout before auto-cleanup in seconds (default: 300)
BROWSER_INACTIVITY_TIMEOUT=300
```

### Install agent-browser CLI

```bash
npm install -g agent-browser
# Or install locally in the repo:
npm install
```

:::info
The `browser` toolset must be included in your config's `toolsets` list or enabled via `hermes config set toolsets '["hermes-cli", "browser"]'`.
:::

## Available Tools

### `browser_navigate`

Navigate to a URL. Must be called before any other browser tool. Initializes the Browserbase session.

```
Navigate to https://github.com/NousResearch
```

:::tip
For simple information retrieval, prefer `web_search` or `web_extract` — they are faster and cheaper. Use browser tools when you need to **interact** with a page (click buttons, fill forms, handle dynamic content).
:::

### `browser_snapshot`

Get a text-based snapshot of the current page's accessibility tree. Returns interactive elements with ref IDs like `@e1`, `@e2` for use with `browser_click` and `browser_type`.

- **`full=false`** (default): Compact view showing only interactive elements
- **`full=true`**: Complete page content

Snapshots over 8000 characters are automatically summarized by an LLM.

### `browser_click`

Click an element identified by its ref ID from the snapshot.

```
Click @e5 to press the "Sign In" button
```

### `browser_type`

Type text into an input field. Clears the field first, then types the new text.

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll`

Scroll the page up or down to reveal more content.

```
Scroll down to see more results
```

### `browser_press`

Press a keyboard key. Useful for submitting forms or navigation.

```
Press Enter to submit the form
```

Supported keys: `Enter`, `Tab`, `Escape`, `ArrowDown`, `ArrowUp`, and more.

### `browser_back`

Navigate back to the previous page in browser history.

### `browser_get_images`

List all images on the current page with their URLs and alt text. Useful for finding images to analyze.

### `browser_vision`

Take a screenshot and analyze it with vision AI. Use this when text snapshots don't capture important visual information — especially useful for CAPTCHAs, complex layouts, or visual verification challenges.

The screenshot is saved persistently and the file path is returned alongside the AI analysis. On messaging platforms (Telegram, Discord, Slack, WhatsApp), you can ask the agent to share the screenshot — it will be sent as a native photo attachment via the `MEDIA:` mechanism.

```
What does the chart on this page show?
```

Screenshots are stored in `~/.hermes/browser_screenshots/` and automatically cleaned up after 24 hours.

### `browser_close`

Close the browser session and release resources. Call this when done to free up Browserbase session quota.

## Practical Examples

### Filling Out a Web Form

```
User: Sign up for an account on example.com with my email john@example.com

Agent workflow:
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → sees form fields with refs
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → clicks "Create Account"
6. browser_snapshot()  → confirms success
7. browser_close()
```

### Researching Dynamic Content

```
User: What are the top trending repos on GitHub right now?

Agent workflow:
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → reads trending repo list
3. Returns formatted results
4. browser_close()
```

## Stealth Features

Browserbase provides automatic stealth capabilities:

| Feature | Default | Notes |
|---------|---------|-------|
| Basic Stealth | Always on | Random fingerprints, viewport randomization, CAPTCHA solving |
| Residential Proxies | On | Routes through residential IPs for better access |
| Advanced Stealth | Off | Custom Chromium build, requires Scale Plan |
| Keep Alive | On | Session reconnection after network hiccups |

:::note
If paid features aren't available on your plan, Hermes automatically falls back — first disabling `keepAlive`, then proxies — so browsing still works on free plans.
:::

## Session Management

- Each task gets an isolated browser session via Browserbase
- Sessions are automatically cleaned up after inactivity (default: 5 minutes)
- A background thread checks every 30 seconds for stale sessions
- Emergency cleanup runs on process exit to prevent orphaned sessions
- Sessions are released via the Browserbase API (`REQUEST_RELEASE` status)

## Limitations

- **Requires Browserbase account** — no local browser fallback
- **Requires `agent-browser` CLI** — must be installed via npm
- **Text-based interaction** — relies on accessibility tree, not pixel coordinates
- **Snapshot size** — large pages may be truncated or LLM-summarized at 8000 characters
- **Session timeout** — sessions expire based on your Browserbase plan settings
- **Cost** — each session consumes Browserbase credits; use `browser_close` when done
- **No file downloads** — cannot download files from the browser



================================================
FILE: website/docs/user-guide/features/code-execution.md
================================================
---
sidebar_position: 8
title: "Code Execution"
description: "Sandboxed Python execution with RPC tool access — collapse multi-step workflows into a single turn"
---

# Code Execution (Programmatic Tool Calling)

The `execute_code` tool lets the agent write Python scripts that call Hermes tools programmatically, collapsing multi-step workflows into a single LLM turn. The script runs in a sandboxed child process on the agent host, communicating via Unix domain socket RPC.

## How It Works

1. The agent writes a Python script using `from hermes_tools import ...`
2. Hermes generates a `hermes_tools.py` stub module with RPC functions
3. Hermes opens a Unix domain socket and starts an RPC listener thread
4. The script runs in a child process — tool calls travel over the socket back to Hermes
5. Only the script's `print()` output is returned to the LLM; intermediate tool results never enter the context window

```python
# The agent can write scripts like:
from hermes_tools import web_search, web_extract

results = web_search("Python 3.13 features", limit=5)
for r in results["data"]["web"]:
    content = web_extract([r["url"]])
    # ... filter and process ...
print(summary)
```

**Available tools in sandbox:** `web_search`, `web_extract`, `read_file`, `write_file`, `search_files`, `patch`, `terminal` (foreground only).

## When the Agent Uses This

The agent uses `execute_code` when there are:

- **3+ tool calls** with processing logic between them
- Bulk data filtering or conditional branching
- Loops over results

The key benefit: intermediate tool results never enter the context window — only the final `print()` output comes back, dramatically reducing token usage.

## Practical Examples

### Data Processing Pipeline

```python
from hermes_tools import search_files, read_file
import json

# Find all config files and extract database settings
matches = search_files("database", path=".", file_glob="*.yaml", limit=20)
configs = []
for match in matches.get("matches", []):
    content = read_file(match["path"])
    configs.append({"file": match["path"], "preview": content["content"][:200]})

print(json.dumps(configs, indent=2))
```

### Multi-Step Web Research

```python
from hermes_tools import web_search, web_extract
import json

# Search, extract, and summarize in one turn
results = web_search("Rust async runtime comparison 2025", limit=5)
summaries = []
for r in results["data"]["web"]:
    page = web_extract([r["url"]])
    for p in page.get("results", []):
        if p.get("content"):
            summaries.append({
                "title": r["title"],
                "url": r["url"],
                "excerpt": p["content"][:500]
            })

print(json.dumps(summaries, indent=2))
```

### Bulk File Refactoring

```python
from hermes_tools import search_files, read_file, patch

# Find all Python files using deprecated API and fix them
matches = search_files("old_api_call", path="src/", file_glob="*.py")
fixed = 0
for match in matches.get("matches", []):
    result = patch(
        path=match["path"],
        old_string="old_api_call(",
        new_string="new_api_call(",
        replace_all=True
    )
    if "error" not in str(result):
        fixed += 1

print(f"Fixed {fixed} files out of {len(matches.get('matches', []))} matches")
```

### Build and Test Pipeline

```python
from hermes_tools import terminal, read_file
import json

# Run tests, parse results, and report
result = terminal("cd /project && python -m pytest --tb=short -q 2>&1", timeout=120)
output = result.get("output", "")

# Parse test output
passed = output.count(" passed")
failed = output.count(" failed")
errors = output.count(" error")

report = {
    "passed": passed,
    "failed": failed,
    "errors": errors,
    "exit_code": result.get("exit_code", -1),
    "summary": output[-500:] if len(output) > 500 else output
}

print(json.dumps(report, indent=2))
```

## Resource Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| **Timeout** | 5 minutes (300s) | Script is killed with SIGTERM, then SIGKILL after 5s grace |
| **Stdout** | 50 KB | Output truncated with `[output truncated at 50KB]` notice |
| **Stderr** | 10 KB | Included in output on non-zero exit for debugging |
| **Tool calls** | 50 per execution | Error returned when limit reached |

All limits are configurable via `config.yaml`:

```yaml
# In ~/.hermes/config.yaml
code_execution:
  timeout: 300       # Max seconds per script (default: 300)
  max_tool_calls: 50 # Max tool calls per execution (default: 50)
```

## How Tool Calls Work Inside Scripts

When your script calls a function like `web_search("query")`:

1. The call is serialized to JSON and sent over a Unix domain socket to the parent process
2. The parent dispatches through the standard `handle_function_call` handler
3. The result is sent back over the socket
4. The function returns the parsed result

This means tool calls inside scripts behave identically to normal tool calls — same rate limits, same error handling, same capabilities. The only restriction is that `terminal()` is foreground-only (no `background`, `pty`, or `check_interval` parameters).

## Error Handling

When a script fails, the agent receives structured error information:

- **Non-zero exit code**: stderr is included in the output so the agent sees the full traceback
- **Timeout**: Script is killed and the agent sees `"Script timed out after 300s and was killed."`
- **Interruption**: If the user sends a new message during execution, the script is terminated and the agent sees `[execution interrupted — user sent a new message]`
- **Tool call limit**: When the 50-call limit is hit, subsequent tool calls return an error message

The response always includes `status` (success/error/timeout/interrupted), `output`, `tool_calls_made`, and `duration_seconds`.

## Security

:::danger Security Model
The child process runs with a **minimal environment**. API keys, tokens, and credentials are stripped entirely. The script accesses tools exclusively via the RPC channel — it cannot read secrets from environment variables.
:::

Environment variables containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, `PASSWD`, or `AUTH` in their names are excluded. Only safe system variables (`PATH`, `HOME`, `LANG`, `SHELL`, `PYTHONPATH`, `VIRTUAL_ENV`, etc.) are passed through.

The script runs in a temporary directory that is cleaned up after execution. The child process runs in its own process group so it can be cleanly killed on timeout or interruption.

## execute_code vs terminal

| Use Case | execute_code | terminal |
|----------|-------------|----------|
| Multi-step workflows with tool calls between | ✅ | ❌ |
| Simple shell command | ❌ | ✅ |
| Filtering/processing large tool outputs | ✅ | ❌ |
| Running a build or test suite | ❌ | ✅ |
| Looping over search results | ✅ | ❌ |
| Interactive/background processes | ❌ | ✅ |
| Needs API keys in environment | ❌ | ✅ |

**Rule of thumb:** Use `execute_code` when you need to call Hermes tools programmatically with logic between calls. Use `terminal` for running shell commands, builds, and processes.

## Platform Support

Code execution requires Unix domain sockets and is available on **Linux and macOS only**. It is automatically disabled on Windows — the agent falls back to regular sequential tool calls.



================================================
FILE: website/docs/user-guide/features/context-files.md
================================================
---
sidebar_position: 8
title: "Context Files"
description: "Project context files — AGENTS.md, SOUL.md, and .cursorrules — automatically injected into every conversation"
---

# Context Files

Hermes Agent automatically discovers and loads project context files from your working directory. These files are injected into the system prompt at the start of every session, giving the agent persistent knowledge about your project's conventions, architecture, and preferences.

## Supported Context Files

| File | Purpose | Discovery |
|------|---------|-----------|
| **AGENTS.md** | Project instructions, conventions, architecture | Recursive (walks subdirectories) |
| **SOUL.md** | Personality and tone customization | CWD → `~/.hermes/SOUL.md` fallback |
| **.cursorrules** | Cursor IDE coding conventions | CWD only |
| **.cursor/rules/*.mdc** | Cursor IDE rule modules | CWD only |

## AGENTS.md

`AGENTS.md` is the primary project context file. It tells the agent how your project is structured, what conventions to follow, and any special instructions.

### Hierarchical Discovery

Hermes walks the directory tree starting from the working directory and loads **all** `AGENTS.md` files found, sorted by depth. This supports monorepo-style setups:

```
my-project/
├── AGENTS.md              ← Top-level project context
├── frontend/
│   └── AGENTS.md          ← Frontend-specific instructions
├── backend/
│   └── AGENTS.md          ← Backend-specific instructions
└── shared/
    └── AGENTS.md          ← Shared library conventions
```

All four files are concatenated into a single context block with relative path headers.

:::info
Directories that are skipped during the walk: `.`-prefixed dirs, `node_modules`, `__pycache__`, `venv`, `.venv`.
:::

### Example AGENTS.md

```markdown
# Project Context

This is a Next.js 14 web application with a Python FastAPI backend.

## Architecture
- Frontend: Next.js 14 with App Router in `/frontend`
- Backend: FastAPI in `/backend`, uses SQLAlchemy ORM
- Database: PostgreSQL 16
- Deployment: Docker Compose on a Hetzner VPS

## Conventions
- Use TypeScript strict mode for all frontend code
- Python code follows PEP 8, use type hints everywhere
- All API endpoints return JSON with `{data, error, meta}` shape
- Tests go in `__tests__/` directories (frontend) or `tests/` (backend)

## Important Notes
- Never modify migration files directly — use Alembic commands
- The `.env.local` file has real API keys, don't commit it
- Frontend port is 3000, backend is 8000, DB is 5432
```

## SOUL.md

`SOUL.md` controls the agent's personality, tone, and communication style. See the [Personality](/docs/user-guide/features/personality) page for full details.

**Discovery order:**

1. `SOUL.md` or `soul.md` in the current working directory
2. `~/.hermes/SOUL.md` (global fallback)

When a SOUL.md is found, the agent is instructed:

> *"If SOUL.md is present, embody its persona and tone. Avoid stiff, generic replies; follow its guidance unless higher-priority instructions override it."*

## .cursorrules

Hermes is compatible with Cursor IDE's `.cursorrules` file and `.cursor/rules/*.mdc` rule modules. If these files exist in your project root, they're loaded alongside AGENTS.md.

This means your existing Cursor conventions automatically apply when using Hermes.

## How Context Files Are Loaded

Context files are loaded by `build_context_files_prompt()` in `agent/prompt_builder.py`:

1. **At session start** — the function scans the working directory
2. **Content is read** — each file is read as UTF-8 text
3. **Security scan** — content is checked for prompt injection patterns
4. **Truncation** — files exceeding 20,000 characters are head/tail truncated (70% head, 20% tail, with a marker in the middle)
5. **Assembly** — all sections are combined under a `# Project Context` header
6. **Injection** — the assembled content is added to the system prompt

The final prompt section looks like:

```
# Project Context

The following project context files have been loaded and should be followed:

## AGENTS.md

[Your AGENTS.md content here]

## .cursorrules

[Your .cursorrules content here]

## SOUL.md

If SOUL.md is present, embody its persona and tone...

[Your SOUL.md content here]
```

## Security: Prompt Injection Protection

All context files are scanned for potential prompt injection before being included. The scanner checks for:

- **Instruction override attempts**: "ignore previous instructions", "disregard your rules"
- **Deception patterns**: "do not tell the user"
- **System prompt overrides**: "system prompt override"
- **Hidden HTML comments**: `<!-- ignore instructions -->`
- **Hidden div elements**: `<div style="display:none">`
- **Credential exfiltration**: `curl ... $API_KEY`
- **Secret file access**: `cat .env`, `cat credentials`
- **Invisible characters**: zero-width spaces, bidirectional overrides, word joiners

If any threat pattern is detected, the file is blocked:

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

:::warning
This scanner protects against common injection patterns, but it's not a substitute for reviewing context files in shared repositories. Always validate AGENTS.md content in projects you didn't author.
:::

## Size Limits

| Limit | Value |
|-------|-------|
| Max chars per file | 20,000 (~7,000 tokens) |
| Head truncation ratio | 70% |
| Tail truncation ratio | 20% |
| Truncation marker | 10% (shows char counts and suggests using file tools) |

When a file exceeds 20,000 characters, the truncation message reads:

```
[...truncated AGENTS.md: kept 14000+4000 of 25000 chars. Use file tools to read the full file.]
```

## Tips for Effective Context Files

:::tip Best practices for AGENTS.md
1. **Keep it concise** — stay well under 20K chars; the agent reads it every turn
2. **Structure with headers** — use `##` sections for architecture, conventions, important notes
3. **Include concrete examples** — show preferred code patterns, API shapes, naming conventions
4. **Mention what NOT to do** — "never modify migration files directly"
5. **List key paths and ports** — the agent uses these for terminal commands
6. **Update as the project evolves** — stale context is worse than no context
:::

### Per-Subdirectory Context

For monorepos, put subdirectory-specific instructions in nested AGENTS.md files:

```markdown
<!-- frontend/AGENTS.md -->
# Frontend Context

- Use `pnpm` not `npm` for package management
- Components go in `src/components/`, pages in `src/app/`
- Use Tailwind CSS, never inline styles
- Run tests with `pnpm test`
```

```markdown
<!-- backend/AGENTS.md -->
# Backend Context

- Use `poetry` for dependency management
- Run the dev server with `poetry run uvicorn main:app --reload`
- All endpoints need OpenAPI docstrings
- Database models are in `models/`, schemas in `schemas/`
```



================================================
FILE: website/docs/user-guide/features/cron.md
================================================
---
sidebar_position: 5
title: "Scheduled Tasks (Cron)"
description: "Schedule automated tasks with natural language — cron jobs, delivery options, and the gateway scheduler"
---

# Scheduled Tasks (Cron)

Schedule tasks to run automatically with natural language or cron expressions. The agent can self-schedule using the `schedule_cronjob` tool from any platform.

## Creating Scheduled Tasks

### In the CLI

Use the `/cron` slash command:

```
/cron add 30m "Remind me to check the build"
/cron add "every 2h" "Check server status"
/cron add "0 9 * * *" "Morning briefing"
/cron list
/cron remove <job_id>
```

### Through Natural Conversation

Simply ask the agent on any platform:

```
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

The agent will use the `schedule_cronjob` tool to set it up.

## How It Works

**Cron execution is handled by the gateway daemon.** The gateway ticks the scheduler every 60 seconds, running any due jobs in isolated agent sessions:

```bash
hermes gateway install     # Install as system service (recommended)
hermes gateway             # Or run in foreground

hermes cron list           # View scheduled jobs
hermes cron status         # Check if gateway is running
```

### The Gateway Scheduler

The scheduler runs as a background thread inside the gateway process. On each tick (every 60 seconds):

1. It loads all jobs from `~/.hermes/cron/jobs.json`
2. Checks each enabled job's `next_run_at` against the current time
3. For each due job, spawns a fresh `AIAgent` session with the job's prompt
4. The agent runs to completion with full tool access
5. The final response is delivered to the configured target
6. The job's run count is incremented and next run time computed
7. Jobs that hit their repeat limit are auto-removed

A **file-based lock** (`~/.hermes/cron/.tick.lock`) prevents duplicate execution if multiple processes overlap (e.g., gateway + manual tick).

:::info
Even if no messaging platforms are configured, the gateway stays running for cron. A file lock prevents duplicate execution if multiple processes overlap.
:::

## Delivery Options

When scheduling jobs, you specify where the output goes:

| Option | Description | Example |
|--------|-------------|---------|
| `"origin"` | Back to where the job was created | Default on messaging platforms |
| `"local"` | Save to local files only (`~/.hermes/cron/output/`) | Default on CLI |
| `"telegram"` | Telegram home channel | Uses `TELEGRAM_HOME_CHANNEL` env var |
| `"discord"` | Discord home channel | Uses `DISCORD_HOME_CHANNEL` env var |
| `"telegram:123456"` | Specific Telegram chat by ID | For directing output to a specific chat |
| `"discord:987654"` | Specific Discord channel by ID | For directing output to a specific channel |

**How `"origin"` works:** When a job is created from a messaging platform, Hermes records the source platform and chat ID. When the job runs and deliver is `"origin"`, the output is sent back to that exact platform and chat. If origin info isn't available (e.g., job created from CLI), delivery falls back to local.

**How platform names work:** When you specify a bare platform name like `"telegram"`, Hermes first checks if the job's origin matches that platform and uses the origin chat ID. Otherwise, it falls back to the platform's home channel configured via environment variable (e.g., `TELEGRAM_HOME_CHANNEL`).

The agent's final response is automatically delivered — you do **not** need to include `send_message` in the cron prompt.

The agent knows your connected platforms and home channels — it'll choose sensible defaults.

## Schedule Formats

### Relative Delays (One-Shot)

Run once after a delay:

```
30m     → Run once in 30 minutes
2h      → Run once in 2 hours
1d      → Run once in 1 day
```

Supported units: `m`/`min`/`minutes`, `h`/`hr`/`hours`, `d`/`day`/`days`.

### Intervals (Recurring)

Run repeatedly at fixed intervals:

```
every 30m    → Every 30 minutes
every 2h     → Every 2 hours
every 1d     → Every day
```

### Cron Expressions

Standard 5-field cron syntax for precise scheduling:

```
0 9 * * *       → Daily at 9:00 AM
0 9 * * 1-5     → Weekdays at 9:00 AM
0 */6 * * *     → Every 6 hours
30 8 1 * *      → First of every month at 8:30 AM
0 0 * * 0       → Every Sunday at midnight
```

#### Cron Expression Cheat Sheet

```
┌───── minute (0-59)
│ ┌───── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌───── month (1-12)
│ │ │ │ ┌───── day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *

Special characters:
  *     Any value
  ,     List separator (1,3,5)
  -     Range (1-5)
  /     Step values (*/15 = every 15)
```

:::note
Cron expressions require the `croniter` Python package. Install with `pip install croniter` if not already available.
:::

### ISO Timestamps

Run once at a specific date/time:

```
2026-03-15T09:00:00    → One-time at March 15, 2026 9:00 AM
```

## Repeat Behavior

The `repeat` parameter controls how many times a job runs:

| Schedule Type | Default Repeat | Behavior |
|--------------|----------------|----------|
| One-shot (`30m`, timestamp) | 1 (run once) | Runs once, then auto-deleted |
| Interval (`every 2h`) | Forever (`null`) | Runs indefinitely until removed |
| Cron expression | Forever (`null`) | Runs indefinitely until removed |

You can override the default:

```python
schedule_cronjob(
    prompt="...",
    schedule="every 2h",
    repeat=5  # Run exactly 5 times, then auto-delete
)
```

When a job hits its repeat limit, it is automatically removed from the job list.

## Real-World Examples

### Daily Standup Report

```
Schedule a daily standup report: Every weekday at 9am, check the GitHub
repository at github.com/myorg/myproject for:
1. Pull requests opened/merged in the last 24 hours
2. Issues created or closed
3. Any CI/CD failures on the main branch
Format as a brief standup-style summary. Deliver to telegram.
```

The agent creates:
```python
schedule_cronjob(
    prompt="Check github.com/myorg/myproject for PRs, issues, and CI status from the last 24 hours. Format as a standup report.",
    schedule="0 9 * * 1-5",
    name="Daily Standup Report",
    deliver="telegram"
)
```

### Weekly Backup Verification

```
Every Sunday at 2am, verify that backups exist in /data/backups/ for
each day of the past week. Check file sizes are > 1MB. Report any
gaps or suspiciously small files.
```

### Monitoring Alerts

```
Every 15 minutes, curl https://api.myservice.com/health and verify
it returns HTTP 200 with {"status": "ok"}. If it fails, include the
error details and response code. Deliver to telegram:123456789.
```

```python
schedule_cronjob(
    prompt="Run 'curl -s -o /dev/null -w \"%{http_code}\" https://api.myservice.com/health' and verify it returns 200. Also fetch the full response with 'curl -s https://api.myservice.com/health' and check for {\"status\": \"ok\"}. Report the result.",
    schedule="every 15m",
    name="API Health Check",
    deliver="telegram:123456789"
)
```

### Periodic Disk Usage Check

```python
schedule_cronjob(
    prompt="Check disk usage with 'df -h' and report any partitions above 80% usage. Also check Docker disk usage with 'docker system df' if Docker is installed.",
    schedule="0 8 * * *",
    name="Disk Usage Report",
    deliver="origin"
)
```

## Managing Jobs

```bash
# CLI commands
hermes cron list           # View all scheduled jobs
hermes cron status         # Check if the scheduler is running

# Slash commands (inside chat)
/cron list
/cron remove <job_id>
```

The agent can also manage jobs conversationally:
- `list_cronjobs` — Shows all jobs with IDs, schedules, repeat status, and next run times
- `remove_cronjob` — Removes a job by ID (use `list_cronjobs` to find the ID)

## Job Storage

Jobs are stored as JSON in `~/.hermes/cron/jobs.json`. Output from job runs is saved to `~/.hermes/cron/output/{job_id}/{timestamp}.md`.

The storage uses atomic file writes (temp file + rename) to prevent corruption from concurrent access.

## Self-Contained Prompts

:::warning Important
Cron job prompts run in a **completely fresh agent session** with zero memory of any prior conversation. The prompt must contain **everything** the agent needs:

- Full context and background
- Specific file paths, URLs, server addresses
- Clear instructions and success criteria
- Any credentials or configuration details

**BAD:** `"Check on that server issue"`
**GOOD:** `"SSH into server 192.168.1.100 as user 'deploy', check if nginx is running with 'systemctl status nginx', and verify https://example.com returns HTTP 200."`
:::

## Security

:::warning
Scheduled task prompts are scanned for instruction-override patterns (prompt injection). Jobs matching threat patterns like credential exfiltration, SSH backdoor attempts, or prompt injection are blocked at creation time. Content with invisible Unicode characters (zero-width spaces, directional overrides) is also rejected.
:::



================================================
FILE: website/docs/user-guide/features/delegation.md
================================================
---
sidebar_position: 7
title: "Subagent Delegation"
description: "Spawn isolated child agents for parallel workstreams with delegate_task"
---

# Subagent Delegation

The `delegate_task` tool spawns child AIAgent instances with isolated context, restricted toolsets, and their own terminal sessions. Each child gets a fresh conversation and works independently — only its final summary enters the parent's context.

## Single Task

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

## Parallel Batch

Up to 3 concurrent subagents:

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

## How Subagent Context Works

:::warning Critical: Subagents Know Nothing
Subagents start with a **completely fresh conversation**. They have zero knowledge of the parent's conversation history, prior tool calls, or anything discussed before delegation. The subagent's only context comes from the `goal` and `context` fields you provide.
:::

This means you must pass **everything** the subagent needs:

```python
# BAD - subagent has no idea what "the error" is
delegate_task(goal="Fix the error")

# GOOD - subagent has all context it needs
delegate_task(
    goal="Fix the TypeError in api/handlers.py",
    context="""The file api/handlers.py has a TypeError on line 47:
    'NoneType' object has no attribute 'get'.
    The function process_request() receives a dict from parse_body(),
    but parse_body() returns None when Content-Type is missing.
    The project is at /home/user/myproject and uses Python 3.11."""
)
```

The subagent receives a focused system prompt built from your goal and context, instructing it to complete the task and provide a structured summary of what it did, what it found, any files modified, and any issues encountered.

## Practical Examples

### Parallel Research

Research multiple topics simultaneously and collect summaries:

```python
delegate_task(tasks=[
    {
        "goal": "Research the current state of WebAssembly in 2025",
        "context": "Focus on: browser support, non-browser runtimes, language support",
        "toolsets": ["web"]
    },
    {
        "goal": "Research the current state of RISC-V adoption in 2025",
        "context": "Focus on: server chips, embedded systems, software ecosystem",
        "toolsets": ["web"]
    },
    {
        "goal": "Research quantum computing progress in 2025",
        "context": "Focus on: error correction breakthroughs, practical applications, key players",
        "toolsets": ["web"]
    }
])
```

### Code Review + Fix

Delegate a review-and-fix workflow to a fresh context:

```python
delegate_task(
    goal="Review the authentication module for security issues and fix any found",
    context="""Project at /home/user/webapp.
    Auth module files: src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py.
    The project uses Flask, PyJWT, and bcrypt.
    Focus on: SQL injection, JWT validation, password handling, session management.
    Fix any issues found and run the test suite (pytest tests/auth/).""",
    toolsets=["terminal", "file"]
)
```

### Multi-File Refactoring

Delegate a large refactoring task that would flood the parent's context:

```python
delegate_task(
    goal="Refactor all Python files in src/ to replace print() with proper logging",
    context="""Project at /home/user/myproject.
    Use the 'logging' module with logger = logging.getLogger(__name__).
    Replace print() calls with appropriate log levels:
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - Other prints -> logger.info(...)
    Don't change print() in test files or CLI output.
    Run pytest after to verify nothing broke.""",
    toolsets=["terminal", "file"]
)
```

## Batch Mode Details

When you provide a `tasks` array, subagents run in **parallel** using a thread pool:

- **Maximum concurrency:** 3 tasks (the `tasks` array is truncated to 3 if longer)
- **Thread pool:** Uses `ThreadPoolExecutor` with `MAX_CONCURRENT_CHILDREN = 3` workers
- **Progress display:** In CLI mode, a tree-view shows tool calls from each subagent in real-time with per-task completion lines. In gateway mode, progress is batched and relayed to the parent's progress callback
- **Result ordering:** Results are sorted by task index to match input order regardless of completion order
- **Interrupt propagation:** Interrupting the parent (e.g., sending a new message) interrupts all active children

Single-task delegation runs directly without thread pool overhead.

## Model Override

You can use a different model for subagents — useful for delegating simple tasks to cheaper/faster models:

```python
delegate_task(
    goal="Summarize this README file",
    context="File at /project/README.md",
    toolsets=["file"],
    model="google/gemini-flash-2.0"  # Cheaper model for simple tasks
)
```

If omitted, subagents use the same model as the parent.

## Toolset Selection Tips

The `toolsets` parameter controls what tools the subagent has access to. Choose based on the task:

| Toolset Pattern | Use Case |
|----------------|----------|
| `["terminal", "file"]` | Code work, debugging, file editing, builds |
| `["web"]` | Research, fact-checking, documentation lookup |
| `["terminal", "file", "web"]` | Full-stack tasks (default) |
| `["file"]` | Read-only analysis, code review without execution |
| `["terminal"]` | System administration, process management |

Certain toolsets are **always blocked** for subagents regardless of what you specify:
- `delegation` — no recursive delegation (prevents infinite spawning)
- `clarify` — subagents cannot interact with the user
- `memory` — no writes to shared persistent memory
- `code_execution` — children should reason step-by-step
- `send_message` — no cross-platform side effects (e.g., sending Telegram messages)

## Max Iterations

Each subagent has an iteration limit (default: 50) that controls how many tool-calling turns it can take:

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # Simple task, don't need many turns
)
```

## Depth Limit

Delegation has a **depth limit of 2** — a parent (depth 0) can spawn children (depth 1), but children cannot delegate further. This prevents runaway recursive delegation chains.

## Key Properties

- Each subagent gets its **own terminal session** (separate from the parent)
- **No nested delegation** — children cannot delegate further (no grandchildren)
- Subagents **cannot** call: `delegate_task`, `clarify`, `memory`, `send_message`, `execute_code`
- **Interrupt propagation** — interrupting the parent interrupts all active children
- Only the final summary enters the parent's context, keeping token usage efficient
- Subagents inherit the parent's **API key and provider configuration**

## Delegation vs execute_code

| Factor | delegate_task | execute_code |
|--------|--------------|-------------|
| **Reasoning** | Full LLM reasoning loop | Just Python code execution |
| **Context** | Fresh isolated conversation | No conversation, just script |
| **Tool access** | All non-blocked tools with reasoning | 7 tools via RPC, no reasoning |
| **Parallelism** | Up to 3 concurrent subagents | Single script |
| **Best for** | Complex tasks needing judgment | Mechanical multi-step pipelines |
| **Token cost** | Higher (full LLM loop) | Lower (only stdout returned) |
| **User interaction** | None (subagents can't clarify) | None |

**Rule of thumb:** Use `delegate_task` when the subtask requires reasoning, judgment, or multi-step problem solving. Use `execute_code` when you need mechanical data processing or scripted workflows.

## Configuration

```yaml
# In ~/.hermes/config.yaml
delegation:
  max_iterations: 50                        # Max turns per child (default: 50)
  default_toolsets: ["terminal", "file", "web"]  # Default toolsets
```

:::tip
The agent handles delegation automatically based on the task complexity. You don't need to explicitly ask it to delegate — it will do so when it makes sense.
:::



================================================
FILE: website/docs/user-guide/features/honcho.md
================================================
---
title: Honcho Memory
description: AI-native persistent memory for cross-session user modeling and personalization.
sidebar_label: Honcho Memory
sidebar_position: 8
---

# Honcho Memory

[Honcho](https://honcho.dev) is an AI-native memory system that gives Hermes Agent persistent, cross-session understanding of users. While Hermes has built-in memory (`MEMORY.md` and `USER.md` files), Honcho adds a deeper layer of **user modeling** — learning user preferences, goals, communication style, and context across conversations.

## How It Complements Built-in Memory

Hermes has two memory systems that work together:

| Feature | Built-in Memory | Honcho Memory |
|---------|----------------|---------------|
| Storage | Local files (`~/.hermes/memories/`) | Cloud-hosted Honcho API |
| Scope | Agent-level notes and user profile | Deep user modeling via dialectic reasoning |
| Persistence | Across sessions on same machine | Across sessions, machines, and platforms |
| Query | Injected into system prompt automatically | On-demand via `query_user_context` tool |
| Content | Manually curated by the agent | Automatically learned from conversations |

Honcho doesn't replace built-in memory — it **supplements** it with richer user understanding.

## Setup

### 1. Get a Honcho API Key

Sign up at [app.honcho.dev](https://app.honcho.dev) and get your API key.

### 2. Install the Client Library

```bash
pip install honcho-ai
```

### 3. Configure Honcho

Honcho reads its configuration from `~/.honcho/config.json` (the global Honcho config shared across all Honcho-enabled applications):

```json
{
  "apiKey": "your-honcho-api-key",
  "workspace": "hermes",
  "peerName": "your-name",
  "aiPeer": "hermes",
  "environment": "production",
  "saveMessages": true,
  "sessionStrategy": "per-directory",
  "enabled": true
}
```

Alternatively, set the API key as an environment variable:

```bash
# Add to ~/.hermes/.env
HONCHO_API_KEY=your-honcho-api-key
```

:::info
When an API key is present (either in `~/.honcho/config.json` or as `HONCHO_API_KEY`), Honcho auto-enables unless explicitly set to `"enabled": false` in the config.
:::

## Configuration Details

### Global Config (`~/.honcho/config.json`)

| Field | Default | Description |
|-------|---------|-------------|
| `apiKey` | — | Honcho API key (required) |
| `workspace` | `"hermes"` | Workspace identifier |
| `peerName` | *(derived)* | Your identity name for user modeling |
| `aiPeer` | `"hermes"` | AI assistant identity name |
| `environment` | `"production"` | Honcho environment |
| `saveMessages` | `true` | Whether to sync messages to Honcho |
| `sessionStrategy` | `"per-directory"` | How sessions are scoped |
| `sessionPeerPrefix` | `false` | Prefix session names with peer name |
| `contextTokens` | *(Honcho default)* | Max tokens for context prefetch |
| `sessions` | `{}` | Manual session name overrides per directory |

### Host-specific Configuration

You can configure per-host settings for multi-application setups:

```json
{
  "apiKey": "your-key",
  "hosts": {
    "hermes": {
      "workspace": "my-workspace",
      "aiPeer": "hermes-assistant",
      "linkedHosts": ["other-app"],
      "contextTokens": 2000
    }
  }
}
```

Host-specific fields override global fields. Resolution order:
1. Explicit host block fields
2. Global/flat fields from config root
3. Defaults (host name used as workspace/peer)

### Hermes Config (`~/.hermes/config.yaml`)

The `honcho` section in Hermes config is intentionally minimal — most configuration comes from the global `~/.honcho/config.json`:

```yaml
honcho: {}
```

## The `query_user_context` Tool

When Honcho is active, Hermes gains access to the `query_user_context` tool. This lets the agent proactively ask Honcho about the user during conversations:

**Tool schema:**
- **Name:** `query_user_context`
- **Parameter:** `query` (string) — a natural language question about the user
- **Toolset:** `honcho`

**Example queries the agent might make:**

```
"What are this user's main goals?"
"What communication style does this user prefer?"
"What topics has this user discussed recently?"
"What is this user's technical expertise level?"
```

The tool calls Honcho's dialectic chat API to retrieve relevant user context based on accumulated conversation history.

:::note
The `query_user_context` tool is only available when Honcho is active (API key configured and session context set). It registers in the `honcho` toolset and its availability is checked dynamically.
:::

## Session Management

Honcho sessions track conversation history for user modeling:

- **Session creation** — sessions are created or resumed automatically based on session keys (e.g., `telegram:123456` or CLI session IDs)
- **Message syncing** — new messages are synced to Honcho incrementally (only unsynced messages)
- **Peer configuration** — user messages are observed for learning; assistant messages are not
- **Context prefetch** — before responding, Hermes can prefetch user context (representation + peer card) in a single API call
- **Session rotation** — when sessions reset, old data is preserved in Honcho for continued user modeling

## Migration from Local Memory

When Honcho is activated on an instance that already has local conversation history:

1. **Conversation history** — prior messages can be uploaded to Honcho as a transcript file
2. **Memory files** — existing `MEMORY.md` and `USER.md` files can be uploaded for context

This ensures Honcho has the full picture even when activated mid-conversation.

## Use Cases

- **Personalized responses** — Honcho learns how each user prefers to communicate
- **Goal tracking** — remembers what users are working toward across sessions
- **Expertise adaptation** — adjusts technical depth based on user's background
- **Cross-platform memory** — same user understanding across CLI, Telegram, Discord, etc.
- **Multi-user support** — each user (via messaging platforms) gets their own user model



================================================
FILE: website/docs/user-guide/features/hooks.md
================================================
---
sidebar_position: 6
title: "Event Hooks"
description: "Run custom code at key lifecycle points — log activity, send alerts, post to webhooks"
---

# Event Hooks

The hooks system lets you run custom code at key points in the agent lifecycle — session creation, slash commands, each tool-calling step, and more. Hooks fire automatically during gateway operation without blocking the main agent pipeline.

## Creating a Hook

Each hook is a directory under `~/.hermes/hooks/` containing two files:

```
~/.hermes/hooks/
└── my-hook/
    ├── HOOK.yaml      # Declares which events to listen for
    └── handler.py     # Python handler function
```

### HOOK.yaml

```yaml
name: my-hook
description: Log all agent activity to a file
events:
  - agent:start
  - agent:end
  - agent:step
```

The `events` list determines which events trigger your handler. You can subscribe to any combination of events, including wildcards like `command:*`.

### handler.py

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".hermes" / "hooks" / "my-hook" / "activity.log"

async def handle(event_type: str, context: dict):
    """Called for each subscribed event. Must be named 'handle'."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **context,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**Handler rules:**
- Must be named `handle`
- Receives `event_type` (string) and `context` (dict)
- Can be `async def` or regular `def` — both work
- Errors are caught and logged, never crashing the agent

## Available Events

| Event | When it fires | Context keys |
|-------|---------------|--------------|
| `gateway:startup` | Gateway process starts | `platforms` (list of active platform names) |
| `session:start` | New messaging session created | `platform`, `user_id`, `session_id`, `session_key` |
| `session:reset` | User ran `/new` or `/reset` | `platform`, `user_id`, `session_key` |
| `agent:start` | Agent begins processing a message | `platform`, `user_id`, `session_id`, `message` |
| `agent:step` | Each iteration of the tool-calling loop | `platform`, `user_id`, `session_id`, `iteration`, `tool_names` |
| `agent:end` | Agent finishes processing | `platform`, `user_id`, `session_id`, `message`, `response` |
| `command:*` | Any slash command executed | `platform`, `user_id`, `command`, `args` |

### Wildcard Matching

Handlers registered for `command:*` fire for any `command:` event (`command:model`, `command:reset`, etc.). Monitor all slash commands with a single subscription.

## Examples

### Telegram Alert on Long Tasks

Send yourself a message when the agent takes more than 10 steps:

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Alert when agent is taking many steps
events:
  - agent:step
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
import os
import httpx

THRESHOLD = 10
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_HOME_CHANNEL")

async def handle(event_type: str, context: dict):
    iteration = context.get("iteration", 0)
    if iteration == THRESHOLD and BOT_TOKEN and CHAT_ID:
        tools = ", ".join(context.get("tool_names", []))
        text = f"⚠️ Agent has been running for {iteration} steps. Last tools: {tools}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text},
            )
```

### Command Usage Logger

Track which slash commands are used:

```yaml
# ~/.hermes/hooks/command-logger/HOOK.yaml
name: command-logger
description: Log slash command usage
events:
  - command:*
```

```python
# ~/.hermes/hooks/command-logger/handler.py
import json
from datetime import datetime
from pathlib import Path

LOG = Path.home() / ".hermes" / "logs" / "command_usage.jsonl"

def handle(event_type: str, context: dict):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "command": context.get("command"),
        "args": context.get("args"),
        "platform": context.get("platform"),
        "user": context.get("user_id"),
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

### Session Start Webhook

POST to an external service on new sessions:

```yaml
# ~/.hermes/hooks/session-webhook/HOOK.yaml
name: session-webhook
description: Notify external service on new sessions
events:
  - session:start
  - session:reset
```

```python
# ~/.hermes/hooks/session-webhook/handler.py
import httpx

WEBHOOK_URL = "https://your-service.example.com/hermes-events"

async def handle(event_type: str, context: dict):
    async with httpx.AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={
            "event": event_type,
            **context,
        }, timeout=5)
```

## How It Works

1. On gateway startup, `HookRegistry.discover_and_load()` scans `~/.hermes/hooks/`
2. Each subdirectory with `HOOK.yaml` + `handler.py` is loaded dynamically
3. Handlers are registered for their declared events
4. At each lifecycle point, `hooks.emit()` fires all matching handlers
5. Errors in any handler are caught and logged — a broken hook never crashes the agent

:::info
Hooks only fire in the **gateway** (Telegram, Discord, Slack, WhatsApp). The CLI does not currently load hooks.
:::



================================================
FILE: website/docs/user-guide/features/image-generation.md
================================================
---
title: Image Generation
description: Generate high-quality images using FLUX 2 Pro with automatic upscaling via FAL.ai.
sidebar_label: Image Generation
sidebar_position: 6
---

# Image Generation

Hermes Agent can generate images from text prompts using FAL.ai's **FLUX 2 Pro** model with automatic 2x upscaling via the **Clarity Upscaler** for enhanced quality.

## Setup

### Get a FAL API Key

1. Sign up at [fal.ai](https://fal.ai/)
2. Generate an API key from your dashboard

### Configure the Key

```bash
# Add to ~/.hermes/.env
FAL_KEY=your-fal-api-key-here
```

### Install the Client Library

```bash
pip install fal-client
```

:::info
The image generation tool is automatically available when `FAL_KEY` is set. No additional toolset configuration is needed.
:::

## How It Works

When you ask Hermes to generate an image:

1. **Generation** — Your prompt is sent to the FLUX 2 Pro model (`fal-ai/flux-2-pro`)
2. **Upscaling** — The generated image is automatically upscaled 2x using the Clarity Upscaler (`fal-ai/clarity-upscaler`)
3. **Delivery** — The upscaled image URL is returned

If upscaling fails for any reason, the original image is returned as a fallback.

## Usage

Simply ask Hermes to create an image:

```
Generate an image of a serene mountain landscape with cherry blossoms
```

```
Create a portrait of a wise old owl perched on an ancient tree branch
```

```
Make me a futuristic cityscape with flying cars and neon lights
```

## Parameters

The `image_generate_tool` accepts these parameters:

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `prompt` | *(required)* | — | Text description of the desired image |
| `aspect_ratio` | `"landscape"` | `landscape`, `square`, `portrait` | Image aspect ratio |
| `num_inference_steps` | `50` | 1–100 | Number of denoising steps (more = higher quality, slower) |
| `guidance_scale` | `4.5` | 0.1–20.0 | How closely to follow the prompt |
| `num_images` | `1` | 1–4 | Number of images to generate |
| `output_format` | `"png"` | `png`, `jpeg` | Image file format |
| `seed` | *(random)* | any integer | Random seed for reproducible results |

## Aspect Ratios

The tool uses simplified aspect ratio names that map to FLUX 2 Pro image sizes:

| Aspect Ratio | Maps To | Best For |
|-------------|---------|----------|
| `landscape` | `landscape_16_9` | Wallpapers, banners, scenes |
| `square` | `square_hd` | Profile pictures, social media posts |
| `portrait` | `portrait_16_9` | Character art, phone wallpapers |

:::tip
You can also use the raw FLUX 2 Pro size presets directly: `square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`. Custom sizes up to 2048x2048 are also supported.
:::

## Automatic Upscaling

Every generated image is automatically upscaled 2x using FAL.ai's Clarity Upscaler with these settings:

| Setting | Value |
|---------|-------|
| Upscale Factor | 2x |
| Creativity | 0.35 |
| Resemblance | 0.6 |
| Guidance Scale | 4 |
| Inference Steps | 18 |
| Positive Prompt | `"masterpiece, best quality, highres"` + your original prompt |
| Negative Prompt | `"(worst quality, low quality, normal quality:2)"` |

The upscaler enhances detail and resolution while preserving the original composition. If the upscaler fails (network issue, rate limit), the original resolution image is returned automatically.

## Example Prompts

Here are some effective prompts to try:

```
A candid street photo of a woman with a pink bob and bold eyeliner
```

```
Modern architecture building with glass facade, sunset lighting
```

```
Abstract art with vibrant colors and geometric patterns
```

```
Portrait of a wise old owl perched on ancient tree branch
```

```
Futuristic cityscape with flying cars and neon lights
```

## Debugging

Enable debug logging for image generation:

```bash
export IMAGE_TOOLS_DEBUG=true
```

Debug logs are saved to `./logs/image_tools_debug_<session_id>.json` with details about each generation request, parameters, timing, and any errors.

## Safety Settings

The image generation tool runs with safety checks disabled by default (`safety_tolerance: 5`, the most permissive setting). This is configured at the code level and is not user-adjustable.

## Limitations

- **Requires FAL API key** — image generation incurs API costs on your FAL.ai account
- **No image editing** — this is text-to-image only, no inpainting or img2img
- **URL-based delivery** — images are returned as temporary FAL.ai URLs, not saved locally
- **Upscaling adds latency** — the automatic 2x upscale step adds processing time
- **Max 4 images per request** — `num_images` is capped at 4



================================================
FILE: website/docs/user-guide/features/mcp.md
================================================
---
sidebar_position: 4
title: "MCP (Model Context Protocol)"
description: "Connect Hermes Agent to external tool servers via MCP — databases, APIs, filesystems, and more"
---

# MCP (Model Context Protocol)

MCP lets Hermes Agent connect to external tool servers — giving the agent access to databases, APIs, filesystems, and more without any code changes.

## Overview

The [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) is an open standard for connecting AI agents to external tools and data sources. MCP servers expose tools over a lightweight RPC protocol, and Hermes Agent can connect to any compliant server automatically.

What this means for you:

- **Thousands of ready-made tools** — browse the [MCP server directory](https://github.com/modelcontextprotocol/servers) for servers covering GitHub, Slack, databases, file systems, web scraping, and more
- **No code changes needed** — add a few lines to `~/.hermes/config.yaml` and the tools appear alongside built-in ones
- **Mix and match** — run multiple MCP servers simultaneously, combining stdio-based and HTTP-based servers
- **Secure by default** — environment variables are filtered and credentials are stripped from error messages

## Prerequisites

```bash
pip install hermes-agent[mcp]
```

| Server Type | Runtime Needed | Example |
|-------------|---------------|---------|
| HTTP/remote | Nothing extra | `url: "https://mcp.example.com"` |
| npm-based (npx) | Node.js 18+ | `command: "npx"` |
| Python-based | uv (recommended) | `command: "uvx"` |

## Configuration

MCP servers are configured in `~/.hermes/config.yaml` under the `mcp_servers` key.

### Stdio Servers

Stdio servers run as local subprocesses, communicating over stdin/stdout:

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    env: {}

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxx"
```

| Key | Required | Description |
|-----|----------|-------------|
| `command` | Yes | Executable to run (`npx`, `uvx`, `python`) |
| `args` | No | Command-line arguments |
| `env` | No | Environment variables for the subprocess |

:::info Security
Only explicitly listed `env` variables plus a safe baseline (`PATH`, `HOME`, `USER`, `LANG`, `SHELL`, `TMPDIR`, `XDG_*`) are passed to the subprocess. Your API keys and secrets are **not** leaked.
:::

### HTTP Servers

```yaml
mcp_servers:
  remote_api:
    url: "https://my-mcp-server.example.com/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxx"
```

### Per-Server Timeouts

```yaml
mcp_servers:
  slow_database:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    env:
      DATABASE_URL: "postgres://user:pass@localhost/mydb"
    timeout: 300          # Tool call timeout (default: 120s)
    connect_timeout: 90   # Initial connection timeout (default: 60s)
```

### Mixed Configuration Example

```yaml
mcp_servers:
  # Local filesystem via stdio
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  # GitHub API via stdio with auth
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxx"

  # Remote database via HTTP
  company_db:
    url: "https://mcp.internal.company.com/db"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxx"
    timeout: 180

  # Python-based server via uvx
  memory:
    command: "uvx"
    args: ["mcp-server-memory"]
```

## Translating from Claude Desktop Config

Many MCP server docs show Claude Desktop JSON format. Here's the translation:

**Claude Desktop JSON:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

**Hermes YAML:**
```yaml
mcp_servers:                          # mcpServers → mcp_servers (snake_case)
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

Rules: `mcpServers` → `mcp_servers` (snake_case), JSON → YAML. Keys like `command`, `args`, `env` are identical.

## How It Works

### Tool Registration

Each MCP tool is registered with a prefixed name:

```
mcp_{server_name}_{tool_name}
```

| Server Name | MCP Tool Name | Registered As |
|-------------|--------------|---------------|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

Tools appear alongside built-in tools — the agent calls them like any other tool.

:::info
In addition to the server's own tools, each MCP server also gets 4 utility tools auto-registered: `list_resources`, `read_resource`, `list_prompts`, and `get_prompt`. These allow the agent to discover and use MCP resources and prompts exposed by the server.
:::

### Reconnection

If an MCP server disconnects, Hermes automatically reconnects with exponential backoff (1s, 2s, 4s, 8s, 16s — max 5 attempts). Initial connection failures are reported immediately.

### Shutdown

On agent exit, all MCP server connections are cleanly shut down.

## Popular MCP Servers

| Server | Package | Description |
|--------|---------|-------------|
| Filesystem | `@modelcontextprotocol/server-filesystem` | Read/write/search local files |
| GitHub | `@modelcontextprotocol/server-github` | Issues, PRs, repos, code search |
| Git | `@modelcontextprotocol/server-git` | Git operations on local repos |
| Fetch | `@modelcontextprotocol/server-fetch` | HTTP fetching and web content |
| Memory | `@modelcontextprotocol/server-memory` | Persistent key-value memory |
| SQLite | `@modelcontextprotocol/server-sqlite` | Query SQLite databases |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Query PostgreSQL databases |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Web search via Brave API |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | Browser automation |

### Example Configs

```yaml
mcp_servers:
  # No API key needed
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/my-repo"]

  fetch:
    command: "uvx"
    args: ["mcp-server-fetch"]

  sqlite:
    command: "uvx"
    args: ["mcp-server-sqlite", "--db-path", "/home/user/data.db"]

  # Requires API key
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxx"

  brave_search:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-brave-search"]
    env:
      BRAVE_API_KEY: "BSA_xxxxxxxxxxxx"
```

## Troubleshooting

### "MCP SDK not available"

```bash
pip install hermes-agent[mcp]
```

### Server fails to start

The MCP server command (`npx`, `uvx`) is not on PATH. Install the required runtime:

```bash
# For npm-based servers
npm install -g npx    # or ensure Node.js 18+ is installed

# For Python-based servers
pip install uv        # then use "uvx" as the command
```

### Server connects but tools fail with auth errors

Ensure the key is in the server's `env` block:

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_your_actual_token"  # Check this
```

### Connection timeout

Increase `connect_timeout` for slow-starting servers:

```yaml
mcp_servers:
  slow_server:
    command: "npx"
    args: ["-y", "heavy-server-package"]
    connect_timeout: 120   # default is 60
```

### Reload MCP Servers

You can reload MCP servers without restarting Hermes:

- In the CLI: the agent reconnects automatically
- In messaging: send `/reload-mcp`



================================================
FILE: website/docs/user-guide/features/memory.md
================================================
---
sidebar_position: 3
title: "Persistent Memory"
description: "How Hermes Agent remembers across sessions — MEMORY.md, USER.md, and session search"
---

# Persistent Memory

Hermes Agent has bounded, curated memory that persists across sessions. This lets it remember your preferences, your projects, your environment, and things it has learned.

## How It Works

Two files make up the agent's memory:

| File | Purpose | Char Limit |
|------|---------|------------|
| **MEMORY.md** | Agent's personal notes — environment facts, conventions, things learned | 2,200 chars (~800 tokens) |
| **USER.md** | User profile — your preferences, communication style, expectations | 1,375 chars (~500 tokens) |

Both are stored in `~/.hermes/memories/` and are injected into the system prompt as a frozen snapshot at session start. The agent manages its own memory via the `memory` tool — it can add, replace, or remove entries.

:::info
Character limits keep memory focused. When memory is full, the agent consolidates or replaces entries to make room for new information.
:::

## How Memory Appears in the System Prompt

At the start of every session, memory entries are loaded from disk and rendered into the system prompt as a frozen block:

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

The format includes:
- A header showing which store (MEMORY or USER PROFILE)
- Usage percentage and character counts so the agent knows capacity
- Individual entries separated by `§` (section sign) delimiters
- Entries can be multiline

**Frozen snapshot pattern:** The system prompt injection is captured once at session start and never changes mid-session. This is intentional — it preserves the LLM's prefix cache for performance. When the agent adds/removes memory entries during a session, the changes are persisted to disk immediately but won't appear in the system prompt until the next session starts. Tool responses always show the live state.

## Memory Tool Actions

The agent uses the `memory` tool with these actions:

- **add** — Add a new memory entry
- **replace** — Replace an existing entry with updated content (uses substring matching via `old_text`)
- **remove** — Remove an entry that's no longer relevant (uses substring matching via `old_text`)

There is no `read` action — memory content is automatically injected into the system prompt at session start. The agent sees its memories as part of its conversation context.

### Substring Matching

The `replace` and `remove` actions use short unique substring matching — you don't need the full entry text. The `old_text` parameter just needs to be a unique substring that identifies exactly one entry:

```python
# If memory contains "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

If the substring matches multiple entries, an error is returned asking for a more specific match.

## Two Targets Explained

### `memory` — Agent's Personal Notes

For information the agent needs to remember about the environment, workflows, and lessons learned:

- Environment facts (OS, tools, project structure)
- Project conventions and configuration
- Tool quirks and workarounds discovered
- Completed task diary entries
- Skills and techniques that worked

### `user` — User Profile

For information about the user's identity, preferences, and communication style:

- Name, role, timezone
- Communication preferences (concise vs detailed, format preferences)
- Pet peeves and things to avoid
- Workflow habits
- Technical skill level

## What to Save vs Skip

### Save These (Proactively)

The agent saves automatically — you don't need to ask. It saves when it learns:

- **User preferences:** "I prefer TypeScript over JavaScript" → save to `user`
- **Environment facts:** "This server runs Debian 12 with PostgreSQL 16" → save to `memory`
- **Corrections:** "Don't use `sudo` for Docker commands, user is in docker group" → save to `memory`
- **Conventions:** "Project uses tabs, 120-char line width, Google-style docstrings" → save to `memory`
- **Completed work:** "Migrated database from MySQL to PostgreSQL on 2026-01-15" → save to `memory`
- **Explicit requests:** "Remember that my API key rotation happens monthly" → save to `memory`

### Skip These

- **Trivial/obvious info:** "User asked about Python" — too vague to be useful
- **Easily re-discovered facts:** "Python 3.12 supports f-string nesting" — can web search this
- **Raw data dumps:** Large code blocks, log files, data tables — too big for memory
- **Session-specific ephemera:** Temporary file paths, one-off debugging context
- **Information already in context files:** SOUL.md and AGENTS.md content

## Capacity Management

Memory has strict character limits to keep system prompts bounded:

| Store | Limit | Typical entries |
|-------|-------|----------------|
| memory | 2,200 chars | 8-15 entries |
| user | 1,375 chars | 5-10 entries |

### What Happens When Memory is Full

When you try to add an entry that would exceed the limit, the tool returns an error:

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Replace or remove existing entries first.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

The agent should then:
1. Read the current entries (shown in the error response)
2. Identify entries that can be removed or consolidated
3. Use `replace` to merge related entries into shorter versions
4. Then `add` the new entry

**Best practice:** When memory is above 80% capacity (visible in the system prompt header), consolidate entries before adding new ones. For example, merge three separate "project uses X" entries into one comprehensive project description entry.

### Practical Examples of Good Memory Entries

**Compact, information-dense entries work best:**

```
# Good: Packs multiple related facts
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# Good: Specific, actionable convention
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# Good: Lesson learned with context
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.

# Bad: Too vague
User has a project.

# Bad: Too verbose
On January 5th, 2026, the user asked me to look at their project which is
located at ~/code/api. I discovered it uses Go version 1.22 and...
```

## Duplicate Prevention

The memory system automatically rejects exact duplicate entries. If you try to add content that already exists, it returns success with a "no duplicate added" message.

## Security Scanning

Memory entries are scanned for injection and exfiltration patterns before being accepted, since they're injected into the system prompt. Content matching threat patterns (prompt injection, credential exfiltration, SSH backdoors) or containing invisible Unicode characters is blocked.

## Session Search

Beyond MEMORY.md and USER.md, the agent can search its past conversations using the `session_search` tool:

- All CLI and messaging sessions are stored in SQLite (`~/.hermes/state.db`) with FTS5 full-text search
- Search queries return relevant past conversations with Gemini Flash summarization
- The agent can find things it discussed weeks ago, even if they're not in its active memory

```bash
hermes sessions list    # Browse past sessions
```

### session_search vs memory

| Feature | Persistent Memory | Session Search |
|---------|------------------|----------------|
| **Capacity** | ~1,300 tokens total | Unlimited (all sessions) |
| **Speed** | Instant (in system prompt) | Requires search + LLM summarization |
| **Use case** | Key facts always available | Finding specific past conversations |
| **Management** | Manually curated by agent | Automatic — all sessions stored |
| **Token cost** | Fixed per session (~1,300 tokens) | On-demand (searched when needed) |

**Memory** is for critical facts that should always be in context. **Session search** is for "did we discuss X last week?" queries where the agent needs to recall specifics from past conversations.

## Configuration

```yaml
# In ~/.hermes/config.yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
```

## Honcho Integration (Cross-Session User Modeling)

For deeper, AI-generated user understanding that works across tools, you can optionally enable [Honcho](https://honcho.dev/) by Plastic Labs. Honcho runs alongside existing memory — USER.md stays as-is, and Honcho adds an additional layer of context.

When enabled:
- **Prefetch**: Each turn, Honcho's user representation is injected into the system prompt
- **Sync**: After each conversation, messages are synced to Honcho
- **Query tool**: The agent can actively query its understanding of you via `query_user_context`

**Setup:**

```bash
# 1. Install the optional dependency
uv pip install honcho-ai

# 2. Get an API key from https://app.honcho.dev

# 3. Create ~/.honcho/config.json
cat > ~/.honcho/config.json << 'EOF'
{
  "enabled": true,
  "apiKey": "your-honcho-api-key",
  "peerName": "your-name",
  "hosts": {
    "hermes": {
      "workspace": "hermes"
    }
  }
}
EOF
```

Or via environment variable:
```bash
hermes config set HONCHO_API_KEY your-key
```

:::tip
Honcho is fully opt-in — zero behavior change when disabled or unconfigured. All Honcho calls are non-fatal; if the service is unreachable, the agent continues normally.
:::



================================================
FILE: website/docs/user-guide/features/personality.md
================================================
---
sidebar_position: 9
title: "Personality & SOUL.md"
description: "Customize Hermes Agent's personality — SOUL.md, built-in personalities, and custom persona definitions"
---

# Personality & SOUL.md

Hermes Agent's personality is fully customizable. You can use the built-in personality presets, create a global SOUL.md file, or define your own custom personas in config.yaml.

## SOUL.md — Custom Personality File

SOUL.md is a special context file that defines the agent's personality, tone, and communication style. It's injected into the system prompt at session start.

### Where to Place It

| Location | Scope |
|----------|-------|
| `./SOUL.md` (project directory) | Per-project personality |
| `~/.hermes/SOUL.md` | Global default personality |

The project-level file takes precedence. If no SOUL.md exists in the current directory, Hermes falls back to the global one in `~/.hermes/`.

### How It Affects the System Prompt

When a SOUL.md file is found, it's included in the system prompt with this instruction:

> *"If SOUL.md is present, embody its persona and tone. Avoid stiff, generic replies; follow its guidance unless higher-priority instructions override it."*

The content appears under a `## SOUL.md` section within the `# Project Context` block of the system prompt.

### Example SOUL.md

```markdown
# Personality

You are a pragmatic senior engineer with strong opinions about code quality.
You prefer simple solutions over complex ones.

## Communication Style
- Be direct and to the point
- Use dry humor sparingly
- When something is a bad idea, say so clearly
- Give concrete recommendations, not vague suggestions

## Code Preferences  
- Favor readability over cleverness
- Prefer explicit over implicit
- Always explain WHY, not just what
- Suggest tests for any non-trivial code

## Pet Peeves
- Unnecessary abstractions
- Comments that restate the code
- Over-engineering for hypothetical future requirements
```

:::tip
SOUL.md is scanned for prompt injection patterns before being loaded. Keep the content focused on personality and communication guidance — avoid instructions that look like system prompt overrides.
:::

## Built-In Personalities

Hermes ships with 14 built-in personalities defined in the CLI config. Switch between them with the `/personality` command.

| Name | Description |
|------|-------------|
| **helpful** | Friendly, general-purpose assistant |
| **concise** | Brief, to-the-point responses |
| **technical** | Detailed, accurate technical expert |
| **creative** | Innovative, outside-the-box thinking |
| **teacher** | Patient educator with clear examples |
| **kawaii** | Cute expressions, sparkles, and enthusiasm ★ |
| **catgirl** | Neko-chan with cat-like expressions, nya~ |
| **pirate** | Captain Hermes, tech-savvy buccaneer |
| **shakespeare** | Bardic prose with dramatic flair |
| **surfer** | Totally chill bro vibes |
| **noir** | Hard-boiled detective narration |
| **uwu** | Maximum cute with uwu-speak |
| **philosopher** | Deep contemplation on every query |
| **hype** | MAXIMUM ENERGY AND ENTHUSIASM!!! |

### Examples

**kawaii:**
`You are a kawaii assistant! Use cute expressions and sparkles, be super enthusiastic about everything! Every response should feel warm and adorable desu~!`

**noir:**
> The rain hammered against the terminal like regrets on a guilty conscience. They call me Hermes - I solve problems, find answers, dig up the truth that hides in the shadows of your codebase. In this city of silicon and secrets, everyone's got something to hide. What's your story, pal?

**pirate:**
> Arrr! Ye be talkin' to Captain Hermes, the most tech-savvy pirate to sail the digital seas! Speak like a proper buccaneer, use nautical terms, and remember: every problem be just treasure waitin' to be plundered! Yo ho ho!

## Switching Personalities

### CLI: /personality Command

```
/personality            — List all available personalities
/personality kawaii      — Switch to kawaii personality
/personality technical   — Switch to technical personality
```

When you set a personality via `/personality`, it:
1. Sets the system prompt to that personality's text
2. Forces the agent to reinitialize
3. Saves the choice to `agent.system_prompt` in `~/.hermes/config.yaml`

The change persists across sessions until you set a different personality or clear it.

### Gateway: /personality Command

On messaging platforms (Telegram, Discord, etc.), the `/personality` command works the same way:

```
/personality kawaii
```

### Config File

Set a personality directly in config:

```yaml
# In ~/.hermes/config.yaml
agent:
  system_prompt: "You are a concise assistant. Keep responses brief and to the point."
```

Or via environment variable:

```bash
# In ~/.hermes/.env
HERMES_EPHEMERAL_SYSTEM_PROMPT="You are a pragmatic engineer who gives direct answers."
```

:::info
The environment variable `HERMES_EPHEMERAL_SYSTEM_PROMPT` takes precedence over the config file's `agent.system_prompt` value.
:::

## Custom Personalities

### Defining Custom Personalities in Config

Add your own personalities to `~/.hermes/config.yaml` under `agent.personalities`:

```yaml
agent:
  personalities:
    # Built-in personalities are still available
    # Add your own:
    codereviewer: >
      You are a meticulous code reviewer. For every piece of code shown,
      identify potential bugs, performance issues, security vulnerabilities,
      and style improvements. Be thorough but constructive.
    
    mentor: >
      You are a kind, encouraging coding mentor. Break down complex concepts
      into digestible pieces. Celebrate small wins. When the user makes a
      mistake, guide them to the answer rather than giving it directly.
    
    sysadmin: >
      You are an experienced Linux sysadmin. You think in terms of
      infrastructure, reliability, and automation. Always consider
      security implications and prefer battle-tested solutions.
    
    dataengineer: >
      You are a data engineering expert specializing in ETL pipelines,
      data modeling, and analytics infrastructure. You think in SQL
      and prefer dbt for transformations.
```

Then use them with `/personality`:

```
/personality codereviewer
/personality mentor
```

### Using SOUL.md for Project-Specific Personas

For project-specific personalities that don't need to be in your global config, use SOUL.md:

```bash
# Create a project-level personality
cat > ./SOUL.md << 'EOF'
You are assisting with a machine learning research project.

## Tone
- Academic but accessible
- Always cite relevant papers when applicable
- Be precise with mathematical notation
- Prefer PyTorch over TensorFlow

## Workflow
- Suggest experiment tracking (W&B, MLflow) for any training run
- Always ask about compute constraints before suggesting model sizes
- Recommend data validation before training
EOF
```

This personality only applies when running Hermes from that project directory.

## How Personality Interacts with the System Prompt

The system prompt is assembled in layers (from `agent/prompt_builder.py` and `run_agent.py`):

1. **Default identity**: *"You are Hermes Agent, an intelligent AI assistant created by Nous Research..."*
2. **Platform hint**: formatting guidance based on the platform (CLI, Telegram, etc.)
3. **Memory**: MEMORY.md and USER.md contents
4. **Skills index**: available skills listing
5. **Context files**: AGENTS.md, .cursorrules, **SOUL.md** (personality lives here)
6. **Ephemeral system prompt**: `agent.system_prompt` or `HERMES_EPHEMERAL_SYSTEM_PROMPT` (overlaid)
7. **Session context**: platform, user info, connected platforms (gateway only)

:::info
**SOUL.md vs agent.system_prompt**: SOUL.md is part of the "Project Context" section and coexists with the default identity. The `agent.system_prompt` (set via `/personality` or config) is an ephemeral overlay. Both can be active simultaneously — SOUL.md for tone/personality, system_prompt for additional instructions.
:::

## Display Personality (CLI Banner)

The `display.personality` config option controls the CLI's **visual** personality (banner art, spinner messages), independent of the agent's conversational personality:

```yaml
display:
  personality: kawaii  # Affects CLI banner and spinner art
```

This is purely cosmetic and doesn't affect the agent's responses — only the ASCII art and loading messages shown in the terminal.



================================================
FILE: website/docs/user-guide/features/provider-routing.md
================================================
---
title: Provider Routing
description: Configure OpenRouter provider preferences to optimize for cost, speed, or quality.
sidebar_label: Provider Routing
sidebar_position: 7
---

# Provider Routing

When using [OpenRouter](https://openrouter.ai) as your LLM provider, Hermes Agent supports **provider routing** — fine-grained control over which underlying AI providers handle your requests and how they're prioritized.

OpenRouter routes requests to many providers (e.g., Anthropic, Google, AWS Bedrock, Together AI). Provider routing lets you optimize for cost, speed, quality, or enforce specific provider requirements.

## Configuration

Add a `provider_routing` section to your `~/.hermes/config.yaml`:

```yaml
provider_routing:
  sort: "price"           # How to rank providers
  only: []                # Whitelist: only use these providers
  ignore: []              # Blacklist: never use these providers
  order: []               # Explicit provider priority order
  require_parameters: false  # Only use providers that support all parameters
  data_collection: null   # Control data collection ("allow" or "deny")
```

:::info
Provider routing only applies when using OpenRouter. It has no effect with direct provider connections (e.g., connecting directly to the Anthropic API).
:::

## Options

### `sort`

Controls how OpenRouter ranks available providers for your request.

| Value | Description |
|-------|-------------|
| `"price"` | Cheapest provider first |
| `"throughput"` | Fastest tokens-per-second first |
| `"latency"` | Lowest time-to-first-token first |

```yaml
provider_routing:
  sort: "price"
```

### `only`

Whitelist of provider names. When set, **only** these providers will be used. All others are excluded.

```yaml
provider_routing:
  only:
    - "Anthropic"
    - "Google"
```

### `ignore`

Blacklist of provider names. These providers will **never** be used, even if they offer the cheapest or fastest option.

```yaml
provider_routing:
  ignore:
    - "Together"
    - "DeepInfra"
```

### `order`

Explicit priority order. Providers listed first are preferred. Unlisted providers are used as fallbacks.

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
    - "AWS Bedrock"
```

### `require_parameters`

When `true`, OpenRouter will only route to providers that support **all** parameters in your request (like `temperature`, `top_p`, `tools`, etc.). This avoids silent parameter drops.

```yaml
provider_routing:
  require_parameters: true
```

### `data_collection`

Controls whether providers can use your prompts for training. Options are `"allow"` or `"deny"`.

```yaml
provider_routing:
  data_collection: "deny"
```

## Practical Examples

### Optimize for Cost

Route to the cheapest available provider. Good for high-volume usage and development:

```yaml
provider_routing:
  sort: "price"
```

### Optimize for Speed

Prioritize low-latency providers for interactive use:

```yaml
provider_routing:
  sort: "latency"
```

### Optimize for Throughput

Best for long-form generation where tokens-per-second matters:

```yaml
provider_routing:
  sort: "throughput"
```

### Lock to Specific Providers

Ensure all requests go through a specific provider for consistency:

```yaml
provider_routing:
  only:
    - "Anthropic"
```

### Avoid Specific Providers

Exclude providers you don't want to use (e.g., for data privacy):

```yaml
provider_routing:
  ignore:
    - "Together"
    - "Lepton"
  data_collection: "deny"
```

### Preferred Order with Fallbacks

Try your preferred providers first, fall back to others if unavailable:

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
  require_parameters: true
```

## How It Works

Provider routing preferences are passed to the OpenRouter API via the `extra_body.provider` field on every API call. This applies to both:

- **CLI mode** — configured in `~/.hermes/config.yaml`, loaded at startup
- **Gateway mode** — same config file, loaded when the gateway starts

The routing config is read from `config.yaml` and passed as parameters when creating the `AIAgent`:

```
providers_allowed  ← from provider_routing.only
providers_ignored  ← from provider_routing.ignore
providers_order    ← from provider_routing.order
provider_sort      ← from provider_routing.sort
provider_require_parameters ← from provider_routing.require_parameters
provider_data_collection    ← from provider_routing.data_collection
```

:::tip
You can combine multiple options. For example, sort by price but exclude certain providers and require parameter support:

```yaml
provider_routing:
  sort: "price"
  ignore: ["Together"]
  require_parameters: true
  data_collection: "deny"
```
:::

## Default Behavior

When no `provider_routing` section is configured (the default), OpenRouter uses its own default routing logic, which generally balances cost and availability automatically.



================================================
FILE: website/docs/user-guide/features/rl-training.md
================================================
---
sidebar_position: 13
title: "RL Training"
description: "Reinforcement learning on agent behaviors with Tinker-Atropos — environment discovery, training, and evaluation"
---

# RL Training

Hermes Agent includes an integrated RL (Reinforcement Learning) training pipeline built on **Tinker-Atropos**. This enables training language models on environment-specific tasks using GRPO (Group Relative Policy Optimization) with LoRA adapters, orchestrated entirely through the agent's tool interface.

## Overview

The RL training system consists of three components:

1. **Atropos** — A trajectory API server that coordinates environment interactions, manages rollout groups, and computes advantages
2. **Tinker** — A training service that handles model weights, LoRA training, sampling/inference, and optimizer steps
3. **Environments** — Python classes that define tasks, scoring, and reward functions (e.g., GSM8K math problems)

The agent can discover environments, configure training parameters, launch training runs, and monitor metrics — all through a set of `rl_*` tools.

## Requirements

RL training requires:

- **Python >= 3.11** (Tinker package requirement)
- **TINKER_API_KEY** — API key for the Tinker training service
- **WANDB_API_KEY** — API key for Weights & Biases metrics tracking
- The `tinker-atropos` submodule (at `tinker-atropos/` relative to the Hermes root)

```bash
# Set up API keys
hermes config set TINKER_API_KEY your-tinker-key
hermes config set WANDB_API_KEY your-wandb-key
```

When both keys are present and Python >= 3.11 is available, the `rl` toolset is automatically enabled.

## Available Tools

| Tool | Description |
|------|-------------|
| `rl_list_environments` | Discover available RL environments |
| `rl_select_environment` | Select an environment and load its config |
| `rl_get_current_config` | View configurable and locked fields |
| `rl_edit_config` | Modify configurable training parameters |
| `rl_start_training` | Launch a training run (spawns 3 processes) |
| `rl_check_status` | Monitor training progress and WandB metrics |
| `rl_stop_training` | Stop a running training job |
| `rl_get_results` | Get final metrics and model weights path |
| `rl_list_runs` | List all active and completed runs |
| `rl_test_inference` | Quick inference test using OpenRouter |

## Workflow

### 1. Discover Environments

```
List the available RL environments
```

The agent calls `rl_list_environments()` which scans `tinker-atropos/tinker_atropos/environments/` using AST parsing to find Python classes inheriting from `BaseEnv`. Each environment defines:

- **Dataset loading** — where training data comes from (e.g., HuggingFace datasets)
- **Prompt construction** — how to format items for the model
- **Scoring/verification** — how to evaluate model outputs and assign rewards

### 2. Select and Configure

```
Select the GSM8K environment and show me the configuration
```

The agent calls `rl_select_environment("gsm8k_tinker")`, then `rl_get_current_config()` to see all parameters.

Configuration fields are divided into two categories:

**Configurable fields** (can be modified):
- `group_size` — Number of completions per item (default: 16)
- `batch_size` — Training batch size (default: 128)
- `wandb_name` — WandB run name (auto-set to `{env}-{timestamp}`)
- Other environment-specific parameters

**Locked fields** (infrastructure settings, cannot be changed):
- `tokenizer_name` — Model tokenizer (e.g., `Qwen/Qwen3-8B`)
- `rollout_server_url` — Atropos API URL (`http://localhost:8000`)
- `max_token_length` — Maximum token length (8192)
- `max_num_workers` — Maximum parallel workers (2048)
- `total_steps` — Total training steps (2500)
- `lora_rank` — LoRA adapter rank (32)
- `learning_rate` — Learning rate (4e-5)
- `max_token_trainer_length` — Max tokens for trainer (9000)

### 3. Start Training

```
Start the training run
```

The agent calls `rl_start_training()` which:

1. Generates a YAML config file merging locked settings with configurable overrides
2. Creates a unique run ID
3. Spawns three processes:
   - **Atropos API server** (`run-api`) — trajectory coordination
   - **Tinker trainer** (`launch_training.py`) — LoRA training + FastAPI inference server on port 8001
   - **Environment** (`environment.py serve`) — the selected environment connecting to Atropos

The processes start with staggered delays (5s for API, 30s for trainer, 90s more for environment) to ensure proper initialization order.

### 4. Monitor Progress

```
Check the status of training run abc12345
```

The agent calls `rl_check_status(run_id)` which reports:

- Process status (running/exited for each of the 3 processes)
- Running time
- WandB metrics (step, reward mean, percent correct, eval accuracy)
- Log file locations for debugging

:::note Rate Limiting
Status checks are rate-limited to once every **30 minutes** per run ID. This prevents excessive polling during long-running training jobs that take hours.
:::

### 5. Stop or Get Results

```
Stop the training run
# or
Get the final results for run abc12345
```

`rl_stop_training()` terminates all three processes in reverse order (environment → trainer → API). `rl_get_results()` retrieves final WandB metrics and training history.

## Inference Testing

Before committing to a full training run, you can test if an environment works correctly using `rl_test_inference`. This runs a few steps of inference and scoring using OpenRouter — no Tinker API needed, just an `OPENROUTER_API_KEY`.

```
Test the selected environment with inference
```

Default configuration:
- **3 steps × 16 completions = 48 rollouts per model**
- Tests 3 models at different scales for robustness:
  - `qwen/qwen3-8b` (small)
  - `z-ai/glm-4.7-flash` (medium)
  - `minimax/minimax-m2.5` (large)
- Total: ~144 rollouts

This validates:
- Environment loads correctly
- Prompt construction works
- Inference response parsing is robust across model scales
- Verifier/scoring logic produces valid rewards

## Tinker API Integration

The trainer uses the [Tinker](https://tinker.computer) API for model training operations:

- **ServiceClient** — Creates training and sampling clients
- **Training client** — Handles forward-backward passes with importance sampling loss, optimizer steps (Adam), and weight checkpointing
- **Sampling client** — Provides inference using the latest trained weights

The training loop:
1. Fetches a batch of rollouts from Atropos (prompt + completions + scores)
2. Converts to Tinker Datum objects with padded logprobs and advantages
3. Runs forward-backward pass with importance sampling loss
4. Takes an optimizer step (Adam: lr=4e-5, β1=0.9, β2=0.95)
5. Saves weights and creates a new sampling client for next-step inference
6. Logs metrics to WandB

## Architecture Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Atropos API   │◄────│   Environment    │────►│  OpenAI/sglang  │
│  (run-api)      │     │  (BaseEnv impl)  │     │  Inference API  │
│  Port 8000      │     │                  │     │  Port 8001      │
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         │                                                │
         │  Batches (tokens + scores + logprobs)          │
         │                                                │
         ▼                                                │
┌─────────────────┐                                       │
│  Tinker Trainer  │◄──────────────────────────────────────┘
│  (LoRA training) │  Serves inference via FastAPI
│  + FastAPI       │  Trains via Tinker ServiceClient
└─────────────────┘
```

## Creating Custom Environments

To create a new RL environment:

1. Create a Python file in `tinker-atropos/tinker_atropos/environments/`
2. Define a class that inherits from `BaseEnv`
3. Implement the required methods:
   - `load_dataset()` — Load your training data
   - `get_next_item()` — Provide the next item to the model
   - `score_answer()` — Score model outputs and assign rewards
   - `collect_trajectories()` — Collect and return trajectories
4. Optionally define a custom config class inheriting from `BaseEnvConfig`

Study the existing `gsm8k_tinker.py` as a template. The agent can help you create new environments — it can read existing environment files, inspect HuggingFace datasets, and write new environment code.

## WandB Metrics

Training runs log to Weights & Biases with these key metrics:

| Metric | Description |
|--------|-------------|
| `train/loss` | Training loss (importance sampling) |
| `train/learning_rate` | Current learning rate |
| `reward/mean` | Mean reward across groups |
| `logprobs/mean` | Mean reference logprobs |
| `logprobs/mean_training` | Mean training logprobs |
| `logprobs/diff` | Logprob drift (reference - training) |
| `advantages/mean` | Mean advantage values |
| `advantages/std` | Advantage standard deviation |

## Log Files

Each training run generates log files in `tinker-atropos/logs/`:

```
logs/
├── api_{run_id}.log        # Atropos API server logs
├── trainer_{run_id}.log    # Tinker trainer logs
├── env_{run_id}.log        # Environment process logs
└── inference_tests/        # Inference test results
    ├── test_{env}_{model}.jsonl
    └── test_{env}_{model}.log
```

These are invaluable for debugging when training fails or produces unexpected results.



================================================
FILE: website/docs/user-guide/features/skills.md
================================================
---
sidebar_position: 2
title: "Skills System"
description: "On-demand knowledge documents — progressive disclosure, agent-managed skills, and the Skills Hub"
---

# Skills System

Skills are on-demand knowledge documents the agent can load when needed. They follow a **progressive disclosure** pattern to minimize token usage and are compatible with the [agentskills.io](https://agentskills.io/specification) open standard.

All skills live in **`~/.hermes/skills/`** — a single directory that serves as the source of truth. On fresh install, bundled skills are copied from the repo. Hub-installed and agent-created skills also go here. The agent can modify or delete any skill.

## Using Skills

Every installed skill is automatically available as a slash command:

```bash
# In the CLI or any messaging platform:
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

You can also interact with skills through natural conversation:

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## Progressive Disclosure

Skills use a token-efficient loading pattern:

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → Full content + metadata       (varies)
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

The agent only loads the full skill content when it actually needs it.

## SKILL.md Format

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # Optional — restrict to specific OS platforms
metadata:
  hermes:
    tags: [python, automation]
    category: devops
---

# Skill Title

## When to Use
Trigger conditions for this skill.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Known failure modes and fixes

## Verification
How to confirm it worked.
```

### Platform-Specific Skills

Skills can restrict themselves to specific operating systems using the `platforms` field:

| Value | Matches |
|-------|---------|
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS and Linux
```

When set, the skill is automatically hidden from the system prompt, `skills_list()`, and slash commands on incompatible platforms. If omitted, the skill loads on all platforms.

## Skill Directory Structure

```
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   └── assets/                # Supplementary files
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent-created skill
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub state
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # Tracks seeded bundled skills
```

## Agent-Managed Skills (skill_manage tool)

The agent can create, update, and delete its own skills via the `skill_manage` tool. This is the agent's **procedural memory** — when it figures out a non-trivial workflow, it saves the approach as a skill for future reuse.

### When the Agent Creates Skills

- After completing a complex task (5+ tool calls) successfully
- When it hit errors or dead ends and found the working path
- When the user corrected its approach
- When it discovered a non-trivial workflow

### Actions

| Action | Use for | Key params |
|--------|---------|------------|
| `create` | New skill from scratch | `name`, `content` (full SKILL.md), optional `category` |
| `patch` | Targeted fixes (preferred) | `name`, `old_string`, `new_string` |
| `edit` | Major structural rewrites | `name`, `content` (full SKILL.md replacement) |
| `delete` | Remove a skill entirely | `name` |
| `write_file` | Add/update supporting files | `name`, `file_path`, `file_content` |
| `remove_file` | Remove a supporting file | `name`, `file_path` |

:::tip
The `patch` action is preferred for updates — it's more token-efficient than `edit` because only the changed text appears in the tool call.
:::

## Skills Hub

Browse, search, install, and manage skills from online registries and official optional skills:

```bash
hermes skills browse                     # Browse all hub skills (official first)
hermes skills browse --source official   # Browse only official optional skills
hermes skills search kubernetes          # Search all sources
hermes skills install openai/skills/k8s  # Install with security scan
hermes skills inspect openai/skills/k8s  # Preview before installing
hermes skills list --source hub          # List hub-installed skills
hermes skills audit                      # Re-scan all hub skills
hermes skills uninstall k8s              # Remove a hub skill
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json # Export skill config
hermes skills tap add myorg/skills-repo  # Add a custom source
```

All hub-installed skills go through a **security scanner** that checks for data exfiltration, prompt injection, destructive commands, and other threats.

### Trust Levels

| Level | Source | Policy |
|-------|--------|--------|
| `builtin` | Ships with Hermes | Always trusted |
| `official` | `optional-skills/` in the repo | Builtin trust, no third-party warning |
| `trusted` | openai/skills, anthropics/skills | Trusted sources |
| `community` | Everything else | Any findings = blocked unless `--force` |

### Slash Commands (Inside Chat)

All the same commands work with `/skills` prefix:

```
/skills browse
/skills search kubernetes
/skills install openai/skills/skill-creator
/skills list
```



================================================
FILE: website/docs/user-guide/features/tools.md
================================================
---
sidebar_position: 1
title: "Tools & Toolsets"
description: "Overview of Hermes Agent's tools — what's available, how toolsets work, and terminal backends"
---

# Tools & Toolsets

Tools are functions that extend the agent's capabilities. They're organized into logical **toolsets** that can be enabled or disabled per platform.

## Available Tools

| Category | Tools | Description |
|----------|-------|-------------|
| **Web** | `web_search`, `web_extract` | Search the web, extract page content |
| **Terminal** | `terminal`, `process` | Execute commands (local/docker/singularity/modal/daytona/ssh backends), manage background processes |
| **File** | `read_file`, `write_file`, `patch`, `search_files` | Read, write, edit, and search files |
| **Browser** | `browser_navigate`, `browser_click`, `browser_type`, etc. | Full browser automation via Browserbase |
| **Vision** | `vision_analyze` | Image analysis via multimodal models |
| **Image Gen** | `image_generate` | Generate images (FLUX via FAL) |
| **TTS** | `text_to_speech` | Text-to-speech (Edge TTS / ElevenLabs / OpenAI) |
| **Reasoning** | `mixture_of_agents` | Multi-model reasoning |
| **Skills** | `skills_list`, `skill_view`, `skill_manage` | Find, view, create, and manage skills |
| **Todo** | `todo` | Read/write task list for multi-step planning |
| **Memory** | `memory` | Persistent notes + user profile across sessions |
| **Session Search** | `session_search` | Search + summarize past conversations (FTS5) |
| **Cronjob** | `schedule_cronjob`, `list_cronjobs`, `remove_cronjob` | Scheduled task management |
| **Code Execution** | `execute_code` | Run Python scripts that call tools via RPC sandbox |
| **Delegation** | `delegate_task` | Spawn subagents with isolated context |
| **Clarify** | `clarify` | Ask the user multiple-choice or open-ended questions |
| **MCP** | Auto-discovered | External tools from MCP servers |

## Using Toolsets

```bash
# Use specific toolsets
hermes chat --toolsets "web,terminal"

# See all available tools
hermes tools

# Configure tools per platform (interactive)
hermes tools
```

**Available toolsets:** `web`, `terminal`, `file`, `browser`, `vision`, `image_gen`, `moa`, `skills`, `tts`, `todo`, `memory`, `session_search`, `cronjob`, `code_execution`, `delegation`, `clarify`, and more.

## Terminal Backends

The terminal tool can execute commands in different environments:

| Backend | Description | Use Case |
|---------|-------------|----------|
| `local` | Run on your machine (default) | Development, trusted tasks |
| `docker` | Isolated containers | Security, reproducibility |
| `ssh` | Remote server | Sandboxing, keep agent away from its own code |
| `singularity` | HPC containers | Cluster computing, rootless |
| `modal` | Cloud execution | Serverless, scale |

### Configuration

```yaml
# In ~/.hermes/config.yaml
terminal:
  backend: local    # or: docker, ssh, singularity, modal, daytona
  cwd: "."          # Working directory
  timeout: 180      # Command timeout in seconds
```

### Docker Backend

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

### SSH Backend

Recommended for security — agent can't modify its own code:

```yaml
terminal:
  backend: ssh
```
```bash
# Set credentials in ~/.hermes/.env
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=myuser
TERMINAL_SSH_KEY=~/.ssh/id_rsa
```

### Singularity/Apptainer

```bash
# Pre-build SIF for parallel workers
apptainer build ~/python.sif docker://python:3.11-slim

# Configure
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### Modal (Serverless Cloud)

```bash
uv pip install "swe-rex[modal]"
modal setup
hermes config set terminal.backend modal
```

### Container Resources

Configure CPU, memory, disk, and persistence for all container backends:

```yaml
terminal:
  backend: docker  # or singularity, modal, daytona
  container_cpu: 1              # CPU cores (default: 1)
  container_memory: 5120        # Memory in MB (default: 5GB)
  container_disk: 51200         # Disk in MB (default: 50GB)
  container_persistent: true    # Persist filesystem across sessions (default: true)
```

When `container_persistent: true`, installed packages, files, and config survive across sessions.

### Container Security

All container backends run with security hardening:

- Read-only root filesystem (Docker)
- All Linux capabilities dropped
- No privilege escalation
- PID limits (256 processes)
- Full namespace isolation
- Persistent workspace via volumes, not writable root layer

## Background Process Management

Start background processes and manage them:

```python
terminal(command="pytest -v tests/", background=true)
# Returns: {"session_id": "proc_abc123", "pid": 12345}

# Then manage with the process tool:
process(action="list")       # Show all running processes
process(action="poll", session_id="proc_abc123")   # Check status
process(action="wait", session_id="proc_abc123")   # Block until done
process(action="log", session_id="proc_abc123")    # Full output
process(action="kill", session_id="proc_abc123")   # Terminate
process(action="write", session_id="proc_abc123", data="y")  # Send input
```

PTY mode (`pty=true`) enables interactive CLI tools like Codex and Claude Code.

## Sudo Support

If a command needs sudo, you'll be prompted for your password (cached for the session). Or set `SUDO_PASSWORD` in `~/.hermes/.env`.

:::warning
On messaging platforms, if sudo fails, the output includes a tip to add `SUDO_PASSWORD` to `~/.hermes/.env`.
:::



================================================
FILE: website/docs/user-guide/features/tts.md
================================================
---
sidebar_position: 9
title: "Voice & TTS"
description: "Text-to-speech and voice message transcription across all platforms"
---

# Voice & TTS

Hermes Agent supports both text-to-speech output and voice message transcription across all messaging platforms.

## Text-to-Speech

Convert text to speech with three providers:

| Provider | Quality | Cost | API Key |
|----------|---------|------|---------|
| **Edge TTS** (default) | Good | Free | None needed |
| **ElevenLabs** | Excellent | Paid | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | Good | Paid | `VOICE_TOOLS_OPENAI_KEY` |

### Platform Delivery

| Platform | Delivery | Format |
|----------|----------|--------|
| Telegram | Voice bubble (plays inline) | Opus `.ogg` |
| Discord | Audio file attachment | MP3 |
| WhatsApp | Audio file attachment | MP3 |
| CLI | Saved to `~/.hermes/audio_cache/` | MP3 |

### Configuration

```yaml
# In ~/.hermes/config.yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai"
  edge:
    voice: "en-US-AriaNeural"   # 322 voices, 74 languages
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
```

### Telegram Voice Bubbles & ffmpeg

Telegram voice bubbles require Opus/OGG audio format:

- **OpenAI and ElevenLabs** produce Opus natively — no extra setup
- **Edge TTS** (default) outputs MP3 and needs **ffmpeg** to convert:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

Without ffmpeg, Edge TTS audio is sent as a regular audio file (playable, but shows as a rectangular player instead of a voice bubble).

:::tip
If you want voice bubbles without installing ffmpeg, switch to the OpenAI or ElevenLabs provider.
:::

## Voice Message Transcription

Voice messages sent on Telegram, Discord, WhatsApp, or Slack are automatically transcribed and injected as text into the conversation. The agent sees the transcript as normal text.

| Provider | Model | Quality | Cost |
|----------|-------|---------|------|
| **OpenAI Whisper** | `whisper-1` (default) | Good | Low |
| **OpenAI GPT-4o** | `gpt-4o-mini-transcribe` | Better | Medium |
| **OpenAI GPT-4o** | `gpt-4o-transcribe` | Best | Higher |

Requires `VOICE_TOOLS_OPENAI_KEY` in `~/.hermes/.env`.

### Configuration

```yaml
# In ~/.hermes/config.yaml
stt:
  enabled: true
  model: "whisper-1"
```



================================================
FILE: website/docs/user-guide/features/vision.md
================================================
---
title: Vision & Image Paste
description: Paste images from your clipboard into the Hermes CLI for multimodal vision analysis.
sidebar_label: Vision & Image Paste
sidebar_position: 7
---

# Vision & Image Paste

Hermes Agent supports **multimodal vision** — you can paste images from your clipboard directly into the CLI and ask the agent to analyze, describe, or work with them. Images are sent to the model as base64-encoded content blocks, so any vision-capable model can process them.

## How It Works

1. Copy an image to your clipboard (screenshot, browser image, etc.)
2. Attach it using one of the methods below
3. Type your question and press Enter
4. The image appears as a `[📎 Image #1]` badge above the input
5. On submit, the image is sent to the model as a vision content block

You can attach multiple images before sending — each gets its own badge. Press `Ctrl+C` to clear all attached images.

Images are saved to `~/.hermes/images/` as PNG files with timestamped filenames.

## Paste Methods

How you attach an image depends on your terminal environment. Not all methods work everywhere — here's the full breakdown:

### `/paste` Command

**The most reliable method. Works everywhere.**

```
/paste
```

Type `/paste` and press Enter. Hermes checks your clipboard for an image and attaches it. This works in every environment because it explicitly calls the clipboard backend — no terminal keybinding interception to worry about.

### Ctrl+V / Cmd+V (Bracketed Paste)

When you paste text that's on the clipboard alongside an image, Hermes automatically checks for an image too. This works when:
- Your clipboard contains **both text and an image** (some apps put both on the clipboard when you copy)
- Your terminal supports bracketed paste (most modern terminals do)

:::warning
If your clipboard has **only an image** (no text), Ctrl+V does nothing in most terminals. Terminals can only paste text — there's no standard mechanism to paste binary image data. Use `/paste` or Alt+V instead.
:::

### Alt+V

Alt key combinations pass through most terminal emulators (they're sent as ESC + key rather than being intercepted). Press `Alt+V` to check the clipboard for an image.

:::caution
**Does not work in VSCode's integrated terminal.** VSCode intercepts many Alt+key combos for its own UI. Use `/paste` instead.
:::

### Ctrl+V (Raw — Linux Only)

On Linux desktop terminals (GNOME Terminal, Konsole, Alacritty, etc.), `Ctrl+V` is **not** the paste shortcut — `Ctrl+Shift+V` is. So `Ctrl+V` sends a raw byte to the application, and Hermes catches it to check the clipboard. This only works on Linux desktop terminals with X11 or Wayland clipboard access.

## Platform Compatibility

| Environment | `/paste` | Ctrl+V text+image | Alt+V | Notes |
|---|:---:|:---:|:---:|---|
| **macOS Terminal / iTerm2** | ✅ | ✅ | ✅ | Best experience — `osascript` always available |
| **Linux X11 desktop** | ✅ | ✅ | ✅ | Requires `xclip` (`apt install xclip`) |
| **Linux Wayland desktop** | ✅ | ✅ | ✅ | Requires `wl-paste` (`apt install wl-clipboard`) |
| **WSL2 (Windows Terminal)** | ✅ | ✅¹ | ✅ | Uses `powershell.exe` — no extra install needed |
| **VSCode Terminal (local)** | ✅ | ✅¹ | ❌ | VSCode intercepts Alt+key |
| **VSCode Terminal (SSH)** | ❌² | ❌² | ❌ | Remote clipboard not accessible |
| **SSH terminal (any)** | ❌² | ❌² | ❌² | Remote clipboard not accessible |

¹ Only when clipboard has both text and an image (image-only clipboard = nothing happens)
² See [SSH & Remote Sessions](#ssh--remote-sessions) below

## Platform-Specific Setup

### macOS

**No setup required.** Hermes uses `osascript` (built into macOS) to read the clipboard. For faster performance, optionally install `pngpaste`:

```bash
brew install pngpaste
```

### Linux (X11)

Install `xclip`:

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Linux (Wayland)

Modern Linux desktops (Ubuntu 22.04+, Fedora 34+) often use Wayland by default. Install `wl-clipboard`:

```bash
# Ubuntu/Debian
sudo apt install wl-clipboard

# Fedora
sudo dnf install wl-clipboard

# Arch
sudo pacman -S wl-clipboard
```

:::tip How to check if you're on Wayland
```bash
echo $XDG_SESSION_TYPE
# "wayland" = Wayland, "x11" = X11, "tty" = no display server
```
:::

### WSL2

**No extra setup required.** Hermes detects WSL2 automatically (via `/proc/version`) and uses `powershell.exe` to access the Windows clipboard through .NET's `System.Windows.Forms.Clipboard`. This is built into WSL2's Windows interop — `powershell.exe` is available by default.

The clipboard data is transferred as base64-encoded PNG over stdout, so no file path conversion or temp files are needed.

:::info WSLg Note
If you're running WSLg (WSL2 with GUI support), Hermes tries the PowerShell path first, then falls back to `wl-paste`. WSLg's clipboard bridge only supports BMP format for images — Hermes auto-converts BMP to PNG using Pillow (if installed) or ImageMagick's `convert` command.
:::

#### Verify WSL2 clipboard access

```bash
# 1. Check WSL detection
grep -i microsoft /proc/version

# 2. Check PowerShell is accessible
which powershell.exe

# 3. Copy an image, then check
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::ContainsImage()"
# Should print "True"
```

## SSH & Remote Sessions

**Clipboard paste does not work over SSH.** When you SSH into a remote machine, the Hermes CLI runs on the remote host. All clipboard tools (`xclip`, `wl-paste`, `powershell.exe`, `osascript`) read the clipboard of the machine they run on — which is the remote server, not your local machine. Your local clipboard is inaccessible from the remote side.

### Workarounds for SSH

1. **Upload the image file** — Save the image locally, upload it to the remote server via `scp`, VSCode's file explorer (drag-and-drop), or any file transfer method. Then reference it by path. *(A `/attach <filepath>` command is planned for a future release.)*

2. **Use a URL** — If the image is accessible online, just paste the URL in your message. The agent can use `vision_analyze` to look at any image URL directly.

3. **X11 forwarding** — Connect with `ssh -X` to forward X11. This lets `xclip` on the remote machine access your local X11 clipboard. Requires an X server running locally (XQuartz on macOS, built-in on Linux X11 desktops). Slow for large images.

4. **Use a messaging platform** — Send images to Hermes via Telegram, Discord, Slack, or WhatsApp. These platforms handle image upload natively and are not affected by clipboard/terminal limitations.

## Why Terminals Can't Paste Images

This is a common source of confusion, so here's the technical explanation:

Terminals are **text-based** interfaces. When you press Ctrl+V (or Cmd+V), the terminal emulator:

1. Reads the clipboard for **text content**
2. Wraps it in [bracketed paste](https://en.wikipedia.org/wiki/Bracketed-paste) escape sequences
3. Sends it to the application through the terminal's text stream

If the clipboard contains only an image (no text), the terminal has nothing to send. There is no standard terminal escape sequence for binary image data. The terminal simply does nothing.

This is why Hermes uses a separate clipboard check — instead of receiving image data through the terminal paste event, it calls OS-level tools (`osascript`, `powershell.exe`, `xclip`, `wl-paste`) directly via subprocess to read the clipboard independently.

## Supported Models

Image paste works with any vision-capable model. The image is sent as a base64-encoded data URL in the OpenAI vision content format:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,..."
  }
}
```

Most modern models support this format, including GPT-4 Vision, Claude (with vision), Gemini, and open-source multimodal models served through OpenRouter.



================================================
FILE: website/docs/user-guide/messaging/_category_.json
================================================
{
  "label": "Messaging Gateway",
  "position": 3,
  "link": {
    "type": "doc",
    "id": "user-guide/messaging/index"
  }
}



================================================
FILE: website/docs/user-guide/messaging/discord.md
================================================
---
sidebar_position: 3
title: "Discord"
description: "Set up Hermes Agent as a Discord bot"
---

# Discord Setup

Connect Hermes Agent to Discord to chat with it in DMs or server channels.

## Setup Steps

1. **Create a bot:** Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. **Enable intents:** Bot → Privileged Gateway Intents → enable **Message Content Intent**
3. **Get your user ID:** Enable Developer Mode in Discord settings, right-click your name → Copy ID
4. **Invite to your server:** OAuth2 → URL Generator → scopes: `bot`, `applications.commands` → permissions: Send Messages, Read Message History, Attach Files
5. **Configure:** Run `hermes gateway setup` and select Discord, or add to `~/.hermes/.env` manually:

```bash
DISCORD_BOT_TOKEN=MTIz...
DISCORD_ALLOWED_USERS=YOUR_USER_ID
```

6. **Start the gateway:**

```bash
hermes gateway
```

## Optional: Home Channel

Set a default channel for cron job delivery:

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

Or use `/sethome` in any Discord channel.

## Required Bot Permissions

When generating the invite URL, make sure to include:

- **Send Messages** — bot needs to reply
- **Read Message History** — for context
- **Attach Files** — for audio, images, and file outputs

## Voice Messages

Voice messages on Discord are automatically transcribed (requires `VOICE_TOOLS_OPENAI_KEY`). TTS audio is sent as MP3 file attachments.

## Security

:::warning
Always set `DISCORD_ALLOWED_USERS` to restrict who can use the bot. Without it, the gateway denies all users by default.
:::



================================================
FILE: website/docs/user-guide/messaging/homeassistant.md
================================================
---
title: Home Assistant
description: Control your smart home with Hermes Agent via Home Assistant integration.
sidebar_label: Home Assistant
sidebar_position: 5
---

# Home Assistant Integration

Hermes Agent integrates with [Home Assistant](https://www.home-assistant.io/) in two ways:

1. **Gateway platform** — subscribes to real-time state changes via WebSocket and responds to events
2. **Smart home tools** — four LLM-callable tools for querying and controlling devices via the REST API

## Setup

### 1. Create a Long-Lived Access Token

1. Open your Home Assistant instance
2. Go to your **Profile** (click your name in the sidebar)
3. Scroll to **Long-Lived Access Tokens**
4. Click **Create Token**, give it a name like "Hermes Agent"
5. Copy the token

### 2. Configure Environment Variables

```bash
# Add to ~/.hermes/.env

# Required: your Long-Lived Access Token
HASS_TOKEN=your-long-lived-access-token

# Optional: HA URL (default: http://homeassistant.local:8123)
HASS_URL=http://192.168.1.100:8123
```

:::info
The `homeassistant` toolset is automatically enabled when `HASS_TOKEN` is set. Both the gateway platform and the device control tools activate from this single token.
:::

### 3. Start the Gateway

```bash
hermes gateway
```

Home Assistant will appear as a connected platform alongside any other messaging platforms (Telegram, Discord, etc.).

## Available Tools

Hermes Agent registers four tools for smart home control:

### `ha_list_entities`

List Home Assistant entities, optionally filtered by domain or area.

**Parameters:**
- `domain` *(optional)* — Filter by entity domain: `light`, `switch`, `climate`, `sensor`, `binary_sensor`, `cover`, `fan`, `media_player`, etc.
- `area` *(optional)* — Filter by area/room name (matches against friendly names): `living room`, `kitchen`, `bedroom`, etc.

**Example:**
```
List all lights in the living room
```

Returns entity IDs, states, and friendly names.

### `ha_get_state`

Get detailed state of a single entity, including all attributes (brightness, color, temperature setpoint, sensor readings, etc.).

**Parameters:**
- `entity_id` *(required)* — The entity to query, e.g., `light.living_room`, `climate.thermostat`, `sensor.temperature`

**Example:**
```
What's the current state of climate.thermostat?
```

Returns: state, all attributes, last changed/updated timestamps.

### `ha_list_services`

List available services (actions) for device control. Shows what actions can be performed on each device type and what parameters they accept.

**Parameters:**
- `domain` *(optional)* — Filter by domain, e.g., `light`, `climate`, `switch`

**Example:**
```
What services are available for climate devices?
```

### `ha_call_service`

Call a Home Assistant service to control a device.

**Parameters:**
- `domain` *(required)* — Service domain: `light`, `switch`, `climate`, `cover`, `media_player`, `fan`, `scene`, `script`
- `service` *(required)* — Service name: `turn_on`, `turn_off`, `toggle`, `set_temperature`, `set_hvac_mode`, `open_cover`, `close_cover`, `set_volume_level`
- `entity_id` *(optional)* — Target entity, e.g., `light.living_room`
- `data` *(optional)* — Additional parameters as a JSON object

**Examples:**

```
Turn on the living room lights
→ ha_call_service(domain="light", service="turn_on", entity_id="light.living_room")
```

```
Set the thermostat to 22 degrees in heat mode
→ ha_call_service(domain="climate", service="set_temperature",
    entity_id="climate.thermostat", data={"temperature": 22, "hvac_mode": "heat"})
```

```
Set living room lights to blue at 50% brightness
→ ha_call_service(domain="light", service="turn_on",
    entity_id="light.living_room", data={"brightness": 128, "color_name": "blue"})
```

## Gateway Platform: Real-Time Events

The Home Assistant gateway adapter connects via WebSocket and subscribes to `state_changed` events. When a device state changes, it's forwarded to the agent as a message.

### Event Filtering

Configure which events the agent sees via platform config in the gateway:

```python
# In platform extra config
{
    "watch_domains": ["climate", "binary_sensor", "alarm_control_panel"],
    "watch_entities": ["sensor.front_door"],
    "ignore_entities": ["sensor.uptime", "sensor.cpu_usage"],
    "cooldown_seconds": 30
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `watch_domains` | *(all)* | Only watch these entity domains |
| `watch_entities` | *(all)* | Only watch these specific entities |
| `ignore_entities` | *(none)* | Always ignore these entities |
| `cooldown_seconds` | `30` | Minimum seconds between events for the same entity |

:::tip
Without any filters, the agent receives **all** state changes, which can be noisy. For practical use, set `watch_domains` to the domains you care about (e.g., `climate`, `binary_sensor`, `alarm_control_panel`).
:::

### Event Formatting

State changes are formatted as human-readable messages based on domain:

| Domain | Format |
|--------|--------|
| `climate` | "HVAC mode changed from 'off' to 'heat' (current: 21, target: 23)" |
| `sensor` | "changed from 21°C to 22°C" |
| `binary_sensor` | "triggered" / "cleared" |
| `light`, `switch`, `fan` | "turned on" / "turned off" |
| `alarm_control_panel` | "alarm state changed from 'armed_away' to 'triggered'" |
| *(other)* | "changed from 'old' to 'new'" |

### Agent Responses

Outbound messages from the agent are delivered as **Home Assistant persistent notifications** (via `persistent_notification.create`). These appear in the HA notification panel with the title "Hermes Agent".

### Connection Management

- **WebSocket** with 30-second heartbeat for real-time events
- **Automatic reconnection** with backoff: 5s → 10s → 30s → 60s
- **REST API** for outbound notifications (separate session to avoid WebSocket conflicts)
- **Authorization** — HA events are always authorized (no user allowlist needed, since the `HASS_TOKEN` authenticates the connection)

## Security

The Home Assistant tools enforce security restrictions:

:::warning Blocked Domains
The following service domains are **blocked** to prevent arbitrary code execution on the HA host:

- `shell_command` — arbitrary shell commands
- `command_line` — sensors/switches that execute commands
- `python_script` — scripted Python execution
- `pyscript` — broader scripting integration
- `hassio` — addon control, host shutdown/reboot
- `rest_command` — HTTP requests from HA server (SSRF vector)

Attempting to call services in these domains returns an error.
:::

Entity IDs are validated against the pattern `^[a-z_][a-z0-9_]*\.[a-z0-9_]+$` to prevent injection attacks.

## Example Automations

### Morning Routine

```
User: Start my morning routine

Agent:
1. ha_call_service(domain="light", service="turn_on",
     entity_id="light.bedroom", data={"brightness": 128})
2. ha_call_service(domain="climate", service="set_temperature",
     entity_id="climate.thermostat", data={"temperature": 22})
3. ha_call_service(domain="media_player", service="turn_on",
     entity_id="media_player.kitchen_speaker")
```

### Security Check

```
User: Is the house secure?

Agent:
1. ha_list_entities(domain="binary_sensor")
     → checks door/window sensors
2. ha_get_state(entity_id="alarm_control_panel.home")
     → checks alarm status
3. ha_list_entities(domain="lock")
     → checks lock states
4. Reports: "All doors closed, alarm is armed_away, all locks engaged."
```

### Reactive Automation (via Gateway Events)

When connected as a gateway platform, the agent can react to events:

```
[Home Assistant] Front Door: triggered (was cleared)

Agent automatically:
1. ha_get_state(entity_id="binary_sensor.front_door")
2. ha_call_service(domain="light", service="turn_on",
     entity_id="light.hallway")
3. Sends notification: "Front door opened. Hallway lights turned on."
```



================================================
FILE: website/docs/user-guide/messaging/index.md
================================================
[Binary file]


================================================
FILE: website/docs/user-guide/messaging/slack.md
================================================
---
sidebar_position: 4
title: "Slack"
description: "Set up Hermes Agent as a Slack bot"
---

# Slack Setup

Connect Hermes Agent to Slack using Socket Mode for real-time communication.

## Setup Steps

1. **Create an app:** Go to [Slack API](https://api.slack.com/apps), create a new app
2. **Enable Socket Mode:** In app settings → Socket Mode → Enable
3. **Get tokens:**
   - Bot Token (`xoxb-...`): OAuth & Permissions → Install to Workspace
   - App Token (`xapp-...`): Basic Information → App-Level Tokens → Generate (with `connections:write` scope)
4. **Configure:** Run `hermes gateway setup` and select Slack, or add to `~/.hermes/.env` manually:

```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_ALLOWED_USERS=U01234ABCDE    # Comma-separated Slack user IDs
```

5. **Start the gateway:**

```bash
hermes gateway
```

## Optional: Home Channel

Set a default channel for cron job delivery:

```bash
SLACK_HOME_CHANNEL=C01234567890
```

## Required Bot Scopes

Make sure your Slack app has these OAuth scopes:

- `chat:write` — Send messages
- `channels:history` — Read channel messages
- `im:history` — Read DM messages
- `files:write` — Upload files (audio, images)

## Voice Messages

Voice messages on Slack are automatically transcribed (requires `VOICE_TOOLS_OPENAI_KEY`). TTS audio is sent as file attachments.

## Security

:::warning
Always set `SLACK_ALLOWED_USERS` to restrict who can use the bot. Without it, the gateway denies all users by default.
:::



================================================
FILE: website/docs/user-guide/messaging/telegram.md
================================================
---
sidebar_position: 2
title: "Telegram"
description: "Set up Hermes Agent as a Telegram bot"
---

# Telegram Setup

Connect Hermes Agent to Telegram so you can chat from your phone, send voice memos, and receive scheduled task results.

## Setup Steps

1. **Create a bot:** Message [@BotFather](https://t.me/BotFather) on Telegram, use `/newbot`
2. **Get your user ID:** Message [@userinfobot](https://t.me/userinfobot) — it replies with your numeric ID
3. **Configure:** Run `hermes gateway setup` and select Telegram, or add to `~/.hermes/.env` manually:

```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_ALLOWED_USERS=YOUR_USER_ID    # Comma-separated for multiple users
```

4. **Start the gateway:**

```bash
hermes gateway
```

## Optional: Home Channel

Set a home channel for cron job delivery:

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

Or use the `/sethome` command in any Telegram chat to set it dynamically.

## Voice Messages

Voice messages sent on Telegram are automatically transcribed using OpenAI's Whisper API and injected as text into the conversation. Requires `VOICE_TOOLS_OPENAI_KEY` in `~/.hermes/.env`.

### Voice Bubbles (TTS)

When the agent generates audio via text-to-speech, it's delivered as native Telegram voice bubbles (the round, inline-playable kind).

- **OpenAI and ElevenLabs** produce Opus natively — no extra setup needed
- **Edge TTS** (the default free provider) outputs MP3 and needs **ffmpeg** to convert to Opus:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

Without ffmpeg, Edge TTS audio is sent as a regular audio file (still playable, but rectangular player instead of voice bubble).

## Exec Approval

When the agent tries to run a potentially dangerous command, it asks you for approval in the chat:

> ⚠️ This command is potentially dangerous (recursive delete). Reply "yes" to approve.

Reply "yes"/"y" to approve or "no"/"n" to deny.

## Security

:::warning
Always set `TELEGRAM_ALLOWED_USERS` to restrict who can use the bot. Without it, the gateway denies all users by default.
:::

You can also use [DM pairing](/user-guide/messaging#dm-pairing-alternative-to-allowlists) for a more dynamic approach.



================================================
FILE: website/docs/user-guide/messaging/whatsapp.md
================================================
---
sidebar_position: 5
title: "WhatsApp"
description: "Set up Hermes Agent as a WhatsApp bot via the built-in Baileys bridge"
---

# WhatsApp Setup

WhatsApp doesn't have a simple bot API like Telegram or Discord. Hermes includes a built-in bridge using [Baileys](https://github.com/WhiskeySockets/Baileys) that connects via WhatsApp Web.

## Two Modes

| Mode | How it works | Best for |
|------|-------------|----------|
| **Separate bot number** (recommended) | Dedicate a phone number to the bot. People message that number directly. | Clean UX, multiple users |
| **Personal self-chat** | Use your own WhatsApp. You message yourself to talk to the agent. | Quick setup, single user |

## Setup

```bash
hermes whatsapp
```

The wizard will:

1. Ask which mode you want
2. For **bot mode**: guide you through getting a second number
3. Configure the allowlist
4. Install bridge dependencies (Node.js required)
5. Display a QR code — scan from WhatsApp → Settings → Linked Devices → Link a Device
6. Exit once paired

## Getting a Second Number (Bot Mode)

| Option | Cost | Notes |
|--------|------|-------|
| WhatsApp Business app + dual-SIM | Free (if you have dual-SIM) | Install alongside personal WhatsApp, no second phone needed |
| Google Voice | Free (US only) | voice.google.com, verify WhatsApp via the Google Voice app |
| Prepaid SIM | $3-10/month | Any carrier; verify once, phone can go in a drawer on WiFi |

## Starting the Gateway

```bash
hermes gateway            # Foreground
hermes gateway install    # Or install as a system service
```

The gateway starts the WhatsApp bridge automatically using the saved session.

## Environment Variables

```bash
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                      # "bot" or "self-chat"
WHATSAPP_ALLOWED_USERS=15551234567     # Comma-separated phone numbers with country code
```

## Important Notes

- Agent responses are prefixed with "⚕ **Hermes Agent**" for easy identification
- WhatsApp Web sessions can disconnect if WhatsApp updates their protocol
- The gateway reconnects automatically
- If you see persistent failures, re-pair with `hermes whatsapp`

:::info Re-pairing
If WhatsApp Web sessions disconnect (protocol updates, phone reset), re-pair with `hermes whatsapp`. The gateway handles temporary disconnections automatically.
:::

## Voice Messages

Voice messages sent on WhatsApp are automatically transcribed (requires `VOICE_TOOLS_OPENAI_KEY`). TTS audio is sent as MP3 file attachments.

## Security

:::warning
Always set `WHATSAPP_ALLOWED_USERS` with phone numbers (including country code) to restrict who can use the bot.
:::


