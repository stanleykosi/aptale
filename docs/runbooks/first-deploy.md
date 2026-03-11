# Aptale Runbook: First Deploy

Use this runbook for the first production deployment of Aptale gateway.

Keep this runbook private if your operational paths, hostnames, or secret handling procedures are sensitive.

## 1) Host Prerequisites

- Linux host/VPS with high availability.
- Docker + Docker Compose plugin installed.
- Hermes runtime requirements satisfied (Node.js needed for WhatsApp/Baileys + browser tooling).

## 2) Prepare Repo and Environment

```bash
cd /opt/aptale
cp .env.example .env
```

Set required values in `.env` and validate:

- provider credentials (OpenRouter or chosen provider path)
- Browserbase credentials with `BROWSERBASE_PROXIES=true`
- WhatsApp bot settings (`WHATSAPP_ENABLED=true`, `WHATSAPP_MODE=bot`, allowlist)
- optional Honcho/admin webhook keys as needed

## 3) Prepare Hermes State Path

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,whatsapp/session}
```

## 4) Install/Verify Private Skills Tap

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=...
./scripts/install_skills_tap.sh --repo <owner/aptale-skills>
hermes skills tap list
```

## 5) Pair WhatsApp Bot

```bash
hermes whatsapp
```

Pair with QR from WhatsApp Linked Devices and confirm the bot-mode allowlist.

## 6) Start Gateway Runtime

Container path:

```bash
docker compose up -d --build aptale-gateway
docker compose ps
docker compose logs -f aptale-gateway
```

Optional systemd wrapper:

```bash
sudo cp deploy/systemd/aptale-gateway.service /etc/systemd/system/aptale-gateway.service
sudo systemctl daemon-reload
sudo systemctl enable --now aptale-gateway.service
```

## 7) Post-Deploy Validation

```bash
hermes gateway status
hermes cron status
hermes cron list
```

Operational checks:

- one allowlisted tester can message the bot
- one unauthorized number is denied
- WhatsApp monitor hook alerts are configured for persistent disconnects

