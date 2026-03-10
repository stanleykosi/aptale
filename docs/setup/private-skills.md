# Aptale Private Skills Tap Setup

This guide documents the private skills tap flow for Aptale.

Scope:
- Install the private `aptale-skills` tap with GitHub PAT authentication.
- Verify tap registration.
- Update skills later without changing the core Aptale repository.

## 1) Prerequisites

Required:
- Hermes CLI available on `PATH`
- `GITHUB_PERSONAL_ACCESS_TOKEN` exported in the runtime shell
- Private GitHub repository path in `owner/repo` format (for example: `your-org/aptale-skills`)

Validation checks:

```bash
command -v hermes
test -n "${GITHUB_PERSONAL_ACCESS_TOKEN:-}"
```

Fail-fast behavior:
- If Hermes CLI is missing, do not proceed.
- If `GITHUB_PERSONAL_ACCESS_TOKEN` is empty, private tap installation is blocked.

## 2) Install The Private Tap

Use the repository script:

```bash
./scripts/install_skills_tap.sh --repo <owner/aptale-skills>
```

Example:

```bash
./scripts/install_skills_tap.sh --repo your-org/aptale-skills
```

The script builds and uses:

```text
https://<token>@github.com/<owner>/aptale-skills.git
```

and then lists configured taps.

## 3) Verify Tap Registration

```bash
hermes skills tap list
```

Then verify Aptale skills are discoverable:

```bash
hermes skills search aptale
```

Install required skills by identifier returned from search output.

## 4) Update Flow (Without Changing Core Aptale Repo)

When skill content changes in the private `aptale-skills` repository:

1. Commit and push changes to the private skills repository only.
2. On the runtime host, ensure the tap is present:

```bash
hermes skills tap list
```

3. Reinstall/update the changed skills using Hermes skills install commands based on current search/list output:

```bash
hermes skills search aptale
# then run hermes skills install <identifier> for changed skills
```

4. Re-run `./scripts/install_skills_tap.sh --repo <owner/aptale-skills>` if token or repo auth context changed.

## 5) Security Notes

- Keep `GITHUB_PERSONAL_ACCESS_TOKEN` out of committed files.
- Do not hardcode tokenized tap URLs in docs, source files, or shell history artifacts.
- Rotate PAT immediately if it is exposed.
