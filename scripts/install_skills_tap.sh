#!/usr/bin/env bash

set -euo pipefail

log() {
  printf '[aptale skills tap] %s\n' "$1"
}

fail() {
  printf '[aptale skills tap] ERROR: %s\n' "$1" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/install_skills_tap.sh --repo <owner/repo>

Options:
  --repo <owner/repo>   Required GitHub repository path for skills tap.
  -h, --help            Show this help.

Environment:
  GITHUB_PERSONAL_ACCESS_TOKEN   Required PAT used to authenticate private tap access.
USAGE
}

normalize_repo() {
  local raw="$1"
  local repo="$raw"

  repo="${repo#https://}"
  repo="${repo#http://}"
  repo="${repo#git@}"
  repo="${repo#github.com/}"
  repo="${repo#github.com:}"
  repo="${repo#*github.com/}"
  repo="${repo%.git}"
  repo="${repo#/}"

  printf '%s' "$repo"
}

repo_arg=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || fail "--repo requires a value."
      repo_arg="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

if ! command -v hermes >/dev/null 2>&1; then
  fail "Hermes CLI is not installed or not on PATH."
fi

if [[ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
  fail "GITHUB_PERSONAL_ACCESS_TOKEN is required. Export it before running this script."
fi

if [[ -z "$repo_arg" ]]; then
  fail "Missing required --repo argument (owner/repo)."
fi

repo="$(normalize_repo "$repo_arg")"
if [[ "$repo" != */* ]]; then
  fail "Invalid repo format '$repo_arg'. Expected owner/repo."
fi

tap_url="https://${GITHUB_PERSONAL_ACCESS_TOKEN}@github.com/${repo}.git"

if hermes skills tap list 2>/dev/null | grep -Fq "$repo"; then
  log "Tap already configured for ${repo}. No action taken."
  hermes skills tap list
  exit 0
fi

log "Adding private skills tap for ${repo}."
hermes skills tap add "$tap_url"

log "Current configured taps:"
hermes skills tap list

log "Done."
