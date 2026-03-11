# Aptale Production Runtime Packaging

This is the canonical Step-50 production packaging path:

- Dockerized Hermes gateway runtime
- Node.js dependency path for Browserbase + WhatsApp/Baileys bridge
- persistent Hermes state volume
- container healthcheck + systemd service wrapper

## Files

- `Dockerfile`
- `docker-compose.yml`
- `deploy/systemd/aptale-gateway.service`

## 1) Host Prerequisites

- Linux VPS/host with high availability
- Docker Engine + Docker Compose plugin
- outbound internet for provider APIs and WhatsApp Web bridge

## 2) Configure Environment

Set production values in repository `.env` and keep secrets out of git.

Required in practice:

- OpenRouter/provider keys
- Browserbase keys with `BROWSERBASE_PROXIES=true`
- Honcho key/workspace (if enabled)
- WhatsApp bot env (`WHATSAPP_ENABLED=true`, `WHATSAPP_MODE=bot`, allowlist)

## 3) Start Gateway Container

```bash
docker compose up -d --build aptale-gateway
```

Check status:

```bash
docker compose ps
docker compose logs -f aptale-gateway
```

## 4) Healthcheck Strategy

Compose healthcheck verifies the gateway process is alive:

- probe: `pgrep -f 'hermes gateway'`
- interval: 30s
- timeout: 10s
- retries: 5
- start period: 45s

This is a liveness check. It does not replace operational checks for WhatsApp session health; use the `whatsapp-monitor` hook alerts for persistent disconnect/re-pair incidents.

## 5) Persistent Volumes

Compose volumes:

- `aptale_hermes_home` -> `/home/aptale/.hermes`
- `aptale_runtime` -> `/opt/aptale/runtime`

`aptale_hermes_home` is the critical persistence boundary for:

- session/auth data
- memory/state files
- hooks/cron runtime assets
- WhatsApp pairing/session artifacts

## 6) Systemd Wrapper (Optional but Recommended)

Install unit file:

```bash
sudo cp deploy/systemd/aptale-gateway.service /etc/systemd/system/aptale-gateway.service
sudo systemctl daemon-reload
sudo systemctl enable --now aptale-gateway.service
```

Operate service:

```bash
sudo systemctl status aptale-gateway.service
sudo systemctl restart aptale-gateway.service
sudo systemctl stop aptale-gateway.service
```

This wrapper starts/stops the Docker Compose stack and keeps the deployment path explicit and simple.
