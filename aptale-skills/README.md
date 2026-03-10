# aptale-skills

Private Hermes skills repository scaffold for Aptale.

This repository is intentionally minimal in Step 20 and provides the base layout for:
- Master routing skill (`SKILL.md`)
- Region-specific portal instruction files (`regions/`)
- Landed-cost calculation/export skill package (`calculate-landed-cost/`)
- Shared repository conventions (`docs/conventions.md`)

Planned structure:

```text
aptale-skills/
├── README.md
├── SKILL.md
├── docs/
│   └── conventions.md
├── regions/
│   └── .gitkeep
└── calculate-landed-cost/
    └── .gitkeep
```

Deployment target: a separate private GitHub repository that will be installed via Hermes skills tap.
