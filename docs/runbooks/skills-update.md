# Aptale Runbook: Private Skills Refresh

Use this runbook to roll out skill updates from the private `aptale-skills` repository without changing the core Aptale repo.

## 1) Prepare Skills Repo Release

In the private skills repository:

1. Commit skill updates.
2. Push to the protected branch used in production.

## 2) Verify Tap Access on Runtime Host

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=...
hermes skills tap list
```

If tap is missing or token context changed:

```bash
./scripts/install_skills_tap.sh --repo <owner/aptale-skills>
```

## 3) Refresh Installed Skills

```bash
hermes skills search aptale
hermes skills list --source hub
```

Install/reinstall updated skill identifiers returned by search:

```bash
hermes skills install <identifier>
```

## 4) Validate Behavior

- run routing checks against representative invoices
- confirm strict JSON output expectations still hold for freight/customs/fx sourcing
- run batch eval harness before release promotion:

```bash
./scripts/run_batch_eval.sh
```

## 5) Rollback Path

If a skill update causes regressions:

1. Reinstall the previous known-good skill identifier/version from the same tap.
2. Re-run `./scripts/run_batch_eval.sh`.
3. Keep gateway running on the last known-good skill set until the fix is published.

