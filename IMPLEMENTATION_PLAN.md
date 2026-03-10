# Implementation Plan

## 1. Workspace Foundation & Canonical Project Layout

* [ ] Step 1: Create the Aptale monorepo skeleton

  * **Task**: Create the canonical repository structure for Aptale with separate areas for Hermes runtime assets, private skill content, tests, fixtures, and operational scripts. Do not add compatibility layers or migration helpers. Include a root architecture README that states the system is WhatsApp-native and Hermes-first.
  * **Files**:

    * `README.md`: Describe Aptale, core architecture, setup flow, and hard-cut policy.
    * `.gitignore`: Ignore secrets, runtime DBs, generated exports, QR/session files, logs, and caches.
    * `docs/architecture.md`: Capture the single canonical codepath, data flow, and boundaries between Hermes config, skills repo, hooks, and runtime scripts.
    * `docs/decisions/ADR-001-canonical-hermes-path.md`: Record why Aptale uses a single current-state path with fail-fast behavior.
    * `runtime/.gitkeep`: Placeholder for generated runtime assets.
    * `tests/.gitkeep`: Placeholder.
    * `fixtures/.gitkeep`: Placeholder.
    * `scripts/.gitkeep`: Placeholder.
  * **Step Dependencies**: None
  * **User Instructions**: Initialize a private Git repository for the main Aptale codebase.

* [ ] Step 2: Add environment contract and bootstrap docs

  * **Task**: Define all required environment variables and local directories used by Aptale. Separate required secrets from optional ones. Explicitly include OpenRouter, Browserbase, Honcho, WhatsApp, GitHub PAT, and admin alert webhook variables.
  * **Files**:

    * `.env.example`: Add all expected keys with comments.
    * `docs/setup/env.md`: Explain each variable, where it is used, and failure behavior when missing.
    * `scripts/bootstrap_dirs.sh`: Create expected local directories for Hermes runtime and exported artifacts.
  * **Step Dependencies**: Step 1
  * **User Instructions**: Copy `.env.example` to your real environment store, but do not commit secrets.

## 2. Hermes Runtime Configuration

* [ ] Step 3: Add Hermes configuration baseline

  * **Task**: Create the baseline Hermes configuration aligned to the spec: Docker terminal backend, persistent containers, memory enabled, user profile enabled, provider routing with parameter requirements, and code execution timeout. Keep it minimal and canonical.
  * **Files**:

    * `hermes/config/config.yaml`: Base Hermes config for Aptale.
    * `docs/setup/hermes-config.md`: Explain each Aptale-specific Hermes config choice.
  * **Step Dependencies**: Step 2
  * **User Instructions**: Copy `hermes/config/config.yaml` into `~/.hermes/config.yaml` or symlink it during deployment.

* [ ] Step 4: Define Aptale personality and context files

  * **Task**: Create the initial `SOUL.md`, `USER.md` seed template, and `MEMORY.md` seed template. The personality must enforce professional broker behavior, use WhatsApp markdown, require HS-code confirmation before quoting, append disclaimers to every quote, and avoid storing sensitive invoice data in broad logs.
  * **Files**:

    * `hermes/context/SOUL.md`: Aptale persona and operating rules.
    * `hermes/context/USER.template.md`: User profile template with currency, timezone, route preferences, and profit margin fields.
    * `hermes/context/MEMORY.template.md`: Agent memory template for non-PII durable notes.
    * `docs/setup/context-files.md`: Explain how these map into Hermes context behavior.
  * **Step Dependencies**: Step 3
  * **User Instructions**: Place `SOUL.md` in `~/.hermes/SOUL.md`. Use the templates to seed production memory files only after first user onboarding.

* [ ] Step 5: Document Hermes feature assumptions from the docs

  * **Task**: Add a concise implementation note capturing Hermes-specific constraints that codegen must honor: WhatsApp via Baileys in bot mode, gateway allowlists, cron via gateway, subagent isolation/depth limit, and Honcho as a supplement to built-in memory. This prevents later steps from drifting away from Hermes conventions. Hermes supports WhatsApp through the built-in Baileys bridge with `WHATSAPP_MODE=bot` and `WHATSAPP_ALLOWED_USERS`; cron jobs are run by the gateway and can deliver back to the message origin; subagents are isolated and cannot call `clarify` or `execute_code`; Honcho augments `USER.md`/`MEMORY.md` rather than replacing them.    
  * **Files**:

    * `docs/implementation/hermes-constraints.md`: Bulletproof reference for later steps.
  * **Step Dependencies**: Step 4
  * **User Instructions**: None

## 3. Deployment, Gateway & External Service Setup

* [ ] Step 6: Add local development and deployment scripts

  * **Task**: Provide scripts for local setup, gateway start, gateway status, and doctor checks. The scripts should assume Linux/macOS/WSL2 and document Node.js requirement for browser tools and WhatsApp.
  * **Files**:

    * `scripts/setup_local.sh`: Install Hermes deps and project dependencies.
    * `scripts/start_gateway.sh`: Start Hermes gateway in foreground with Aptale config.
    * `scripts/install_gateway_service.sh`: Install gateway as a service.
    * `scripts/check_system.sh`: Run `hermes doctor`, config checks, and runtime checks.
    * `docs/setup/local-dev.md`: Local setup guide.
  * **Step Dependencies**: Step 3
  * **User Instructions**: Install Hermes with the required extras and Node dependencies. Hermes docs indicate Node is needed for browser automation and the WhatsApp bridge. 

* [ ] Step 7: Configure WhatsApp bot mode and MVP access controls

  * **Task**: Add bot-mode WhatsApp env/config examples, allowlist examples, and beta access policy. The initial implementation should only support the allowlist/whitelist path, not open access or alternate legacy auth flows. Hermes’ gateway authorization checks platform allowlists and denies by default when none are configured.  
  * **Files**:

    * `deploy/env/whatsapp.env.example`: WhatsApp-focused env fragment.
    * `docs/setup/whatsapp.md`: Pairing flow, bot mode, second number guidance, and re-pair instructions.
    * `docs/security/access-control.md`: Explain `WHATSAPP_ALLOWED_USERS` rollout policy.
  * **Step Dependencies**: Step 6
  * **User Instructions**: Run `hermes whatsapp`, pair the bot number, set `WHATSAPP_ENABLED=true`, `WHATSAPP_MODE=bot`, and `WHATSAPP_ALLOWED_USERS=...`, then start the gateway. Hermes’ recommended bot path uses a dedicated number and Baileys-based WhatsApp Web pairing. 

* [ ] Step 8: Add service configuration for Browserbase, Honcho, and provider routing

  * **Task**: Create deployment docs and env fragments for Browserbase proxies, Honcho workspace, and OpenRouter model routing. Keep the initial model recommendation fixed and explicit.
  * **Files**:

    * `deploy/env/provider.env.example`: OpenRouter variables and preferred model.
    * `deploy/env/browserbase.env.example`: Browserbase settings including proxies.
    * `deploy/env/honcho.env.example`: Honcho API key and workspace references.
    * `docs/setup/external-services.md`: Setup instructions and validation checks.
  * **Step Dependencies**: Step 6
  * **User Instructions**: Add the provider key, Browserbase creds with `BROWSERBASE_PROXIES=true`, and Honcho API key before running integration tests.

## 4. Structured Data Contracts

* [ ] Step 9: Define the canonical JSON schemas for the pipeline

  * **Task**: Define strict JSON schemas for invoice extraction, user corrections, freight result, customs result, FX result, landed-cost input, landed-cost output, and alert criteria. These schemas should be the only supported wire format between parent agent, subagents, and calculator.
  * **Files**:

    * `schemas/invoice_extraction.schema.json`
    * `schemas/invoice_correction.schema.json`
    * `schemas/freight_quote.schema.json`
    * `schemas/customs_quote.schema.json`
    * `schemas/fx_quote.schema.json`
    * `schemas/landed_cost_input.schema.json`
    * `schemas/landed_cost_output.schema.json`
    * `schemas/alert_rule.schema.json`
    * `docs/contracts/json-contracts.md`: Explain required fields, nullability, and source attribution rules.
  * **Step Dependencies**: Step 5
  * **User Instructions**: None

* [ ] Step 10: Add shared validation utilities

  * **Task**: Implement small Python utilities to validate payloads against the schemas, normalize currencies/weights/Incoterms, and reject partial or malformed data before calculation. These utilities will be used by tests, hooks, and execution scripts.
  * **Files**:

    * `src/aptale/contracts/validate.py`
    * `src/aptale/contracts/normalize.py`
    * `src/aptale/contracts/errors.py`
    * `src/aptale/contracts/__init__.py`
    * `tests/contracts/test_validation.py`
  * **Step Dependencies**: Step 9
  * **User Instructions**: Install Python schema-validation dependencies if not already present.

## 5. Ingestion, Vision & Translation Flow

* [ ] Step 11: Implement the invoice intake orchestrator

  * **Task**: Build the parent orchestration module that receives a WhatsApp image event payload, prepares prompt context, triggers multimodal extraction, and writes the extraction result into the canonical invoice schema. It must stop before sourcing and hand off to a clarification step.
  * **Files**:

    * `src/aptale/flows/invoice_intake.py`: Intake orchestration entrypoint.
    * `src/aptale/prompts/invoice_extraction.md`: Structured extraction prompt.
    * `src/aptale/prompts/language_detection_translation.md`: Translation behavior prompt.
    * `tests/flows/test_invoice_intake.py`
  * **Step Dependencies**: Step 10
  * **User Instructions**: None

* [ ] Step 12: Implement extraction summary rendering for WhatsApp

  * **Task**: Create a formatter that turns the extracted JSON into a clean WhatsApp markdown “Extraction Summary” with numbered corrections guidance and a clear confirmation phrase. This message must be concise, copy-friendly, and designed for `clarify`.
  * **Files**:

    * `src/aptale/formatters/extraction_summary.py`
    * `src/aptale/formatters/whatsapp_markdown.py`
    * `tests/formatters/test_extraction_summary.py`
    * `docs/ux/whatsapp-formatting.md`
  * **Step Dependencies**: Step 11
  * **User Instructions**: None

* [ ] Step 13: Implement explicit confirmation/correction gating

  * **Task**: Add logic that pauses after extraction, waits for user confirmation or corrections, applies corrections to the canonical JSON, and only then marks the invoice “validated.” Do not allow freight/customs/FX sourcing to run on unconfirmed extraction.
  * **Files**:

    * `src/aptale/flows/clarify_extraction.py`
    * `src/aptale/parsers/user_corrections.py`
    * `tests/flows/test_clarify_extraction.py`
  * **Step Dependencies**: Step 12
  * **User Instructions**: None

* [ ] Step 14: Add fail-fast handling for poor image quality and missing fields

  * **Task**: Implement deterministic user-facing errors for blurry images, missing origin/destination, unreadable totals, or uncertain HS code inference. The response should ask for a clearer upload or manual typed details instead of guessing.
  * **Files**:

    * `src/aptale/errors/intake_errors.py`
    * `src/aptale/flows/intake_failure_responses.py`
    * `tests/flows/test_intake_failures.py`
  * **Step Dependencies**: Step 13
  * **User Instructions**: None

## 6. HS Code Inference & Route Resolution

* [ ] Step 15: Implement HS code inference and confidence scoring

  * **Task**: Add a dedicated inference layer that proposes HS codes per line item, scores confidence, and flags low-confidence cases for user confirmation. Keep the output inside the invoice extraction contract.
  * **Files**:

    * `src/aptale/flows/hs_code_inference.py`
    * `src/aptale/prompts/hs_code_inference.md`
    * `tests/flows/test_hs_code_inference.py`
  * **Step Dependencies**: Step 13
  * **User Instructions**: None

* [ ] Step 16: Implement route/country inference

  * **Task**: Build logic to infer origin country, destination country, ports, and local currency from document content, saved profile, and recent chat context. If unresolved, return an explicit “route required” prompt rather than silently defaulting.
  * **Files**:

    * `src/aptale/flows/route_inference.py`
    * `src/aptale/prompts/route_inference.md`
    * `tests/flows/test_route_inference.py`
  * **Step Dependencies**: Step 15
  * **User Instructions**: None

## 7. Delegated Sourcing Framework

* [ ] Step 17: Implement parent delegation planner

  * **Task**: Create the parent task builder that produces exactly three sourcing tasks—freight, customs, FX—with exhaustive context attached to each task. Hermes subagents have no memory of the parent conversation and cannot themselves call `clarify` or `execute_code`, so the parent must fully validate and package all needed inputs first. 
  * **Files**:

    * `src/aptale/delegation/build_tasks.py`
    * `src/aptale/delegation/context_builder.py`
    * `src/aptale/prompts/subagent_shared_rules.md`
    * `tests/delegation/test_build_tasks.py`
  * **Step Dependencies**: Step 16
  * **User Instructions**: None

* [ ] Step 18: Implement strict JSON-only subagent output handling

  * **Task**: Add a parser and validator for subagent outputs. Reject prose, partial JSON, or missing citations. Normalize successful outputs into the freight/customs/FX schemas and surface explicit errors when invalid.
  * **Files**:

    * `src/aptale/delegation/parse_results.py`
    * `src/aptale/delegation/result_models.py`
    * `tests/delegation/test_parse_results.py`
  * **Step Dependencies**: Step 17
  * **User Instructions**: None

* [ ] Step 19: Implement fail-fast error propagation for subagent failures

  * **Task**: Build the parent-side logic that detects timeouts, portal outages, CAPTCHA failures, schema violations, and empty results. It must inform the user clearly which sourcing leg failed and whether Aptale can switch to an open-web search path.
  * **Files**:

    * `src/aptale/delegation/error_policy.py`
    * `src/aptale/formatters/source_failures.py`
    * `tests/delegation/test_error_policy.py`
  * **Step Dependencies**: Step 18
  * **User Instructions**: None

## 8. Regional Routing Skill & Private Skills Repo

* [ ] Step 20: Create the private skills repository skeleton

  * **Task**: Scaffold the separate private `aptale-skills` repository with a master router skill, region-specific portal instructions, and calculation/export skills. Hermes docs recommend skills for capabilities that can be expressed as instructions plus existing tools, which fits routing and portal procedures. 
  * **Files**:

    * `aptale-skills/README.md`
    * `aptale-skills/SKILL.md`
    * `aptale-skills/regions/.gitkeep`
    * `aptale-skills/calculate-landed-cost/.gitkeep`
    * `aptale-skills/docs/conventions.md`
  * **Step Dependencies**: Step 17
  * **User Instructions**: Create this as a separate private GitHub repository.

* [ ] Step 21: Write the master routing skill

  * **Task**: Implement `SKILL.md` that teaches Hermes how to map country/route pairs to freight portals and customs portals, when to use Browserbase, when to switch to open-web discovery, how to cite sources, and how to return strict JSON. Use progressive disclosure to keep token cost down.
  * **Files**:

    * `aptale-skills/SKILL.md`
    * `aptale-skills/docs/router-examples.md`
  * **Step Dependencies**: Step 20
  * **User Instructions**: None

* [ ] Step 22: Add initial region-specific portal skill files

  * **Task**: Implement the first set of region files for the highest-value launch lanes, such as China→Nigeria, Turkey→Nigeria, and one EU route. Each file should define known portals, query patterns, expected fields, and open-web recovery instructions.
  * **Files**:

    * `aptale-skills/regions/nigeria-customs.md`
    * `aptale-skills/regions/china-freight.md`
    * `aptale-skills/regions/turkey-freight.md`
    * `aptale-skills/regions/eu-import-lane.md`
  * **Step Dependencies**: Step 21
  * **User Instructions**: Expand region coverage incrementally after MVP validation.

* [ ] Step 23: Document private tap deployment and update flow

  * **Task**: Add instructions for installing the private tap with a GitHub PAT and updating it without changing the core Aptale repo. Hermes supports adding taps from custom repositories. 
  * **Files**:

    * `docs/setup/private-skills.md`
    * `scripts/install_skills_tap.sh`
  * **Step Dependencies**: Step 20
  * **User Instructions**: Export `GITHUB_PERSONAL_ACCESS_TOKEN` and run `hermes skills tap add https://<token>@github.com/<org>/aptale-skills.git`.

## 9. Freight, Customs & FX Sourcing Prompts

* [ ] Step 24: Implement freight sourcing prompt package

  * **Task**: Write the freight subagent prompt pack, including required inputs, Browserbase-first behavior, source attribution fields, and explicit open-web search fallback instructions if the portal is unavailable.
  * **Files**:

    * `src/aptale/prompts/subagents/freight.md`
    * `tests/prompts/test_freight_prompt_contract.py`
  * **Step Dependencies**: Step 21
  * **User Instructions**: None

* [ ] Step 25: Implement customs sourcing prompt package

  * **Task**: Write the customs subagent prompt pack for official government duty lookups using HS codes, with explicit fail-fast language for offline portals and open-web fallback rules.
  * **Files**:

    * `src/aptale/prompts/subagents/customs.md`
    * `tests/prompts/test_customs_prompt_contract.py`
  * **Step Dependencies**: Step 21
  * **User Instructions**: None

* [ ] Step 26: Implement FX sourcing prompt package

  * **Task**: Write the FX subagent prompt pack that sources official rates and, where applicable, parallel/black-market rates, always labeling source type clearly and returning a structured comparison payload.
  * **Files**:

    * `src/aptale/prompts/subagents/fx.md`
    * `tests/prompts/test_fx_prompt_contract.py`
  * **Step Dependencies**: Step 21
  * **User Instructions**: None

## 10. Landed Cost Engine & Export Pipeline

* [ ] Step 27: Implement landed-cost calculation module

  * **Task**: Build a deterministic Python module that accepts validated freight/customs/FX payloads plus invoice totals and user margin, calculates landed cost, margin-adjusted sell price, and breakdown rows, and emits the landed-cost output contract.
  * **Files**:

    * `src/aptale/calc/landed_cost.py`
    * `src/aptale/calc/models.py`
    * `tests/calc/test_landed_cost.py`
  * **Step Dependencies**: Step 18, Step 26
  * **User Instructions**: None

* [ ] Step 28: Implement execute-code script templates

  * **Task**: Add the Python script template that Hermes can run via `execute_code` to perform deterministic math and create files in the workspace. Ensure it prints the absolute output path and never reaches out directly to external APIs.
  * **Files**:

    * `src/aptale/codegen/landed_cost_script.py`
    * `src/aptale/codegen/export_helpers.py`
    * `tests/codegen/test_landed_cost_script.py`
    * `docs/implementation/execute-code-contract.md`
  * **Step Dependencies**: Step 27
  * **User Instructions**: Ensure the terminal backend image contains the PDF library chosen for export.

* [ ] Step 29: Implement CSV export generation

  * **Task**: Create a CSV exporter with canonical columns, branded footer metadata row, and disclaimer row. This is the lowest-risk export format and should be available even if PDF generation is unavailable.
  * **Files**:

    * `src/aptale/export/csv_export.py`
    * `tests/export/test_csv_export.py`
  * **Step Dependencies**: Step 28
  * **User Instructions**: None

* [ ] Step 30: Implement PDF export generation with branded footer

  * **Task**: Create the PDF exporter with a simple professional footer containing Aptale/TradeWeaver branding text and the liability disclaimer. Keep the design plain and robust for a Docker environment.
  * **Files**:

    * `src/aptale/export/pdf_export.py`
    * `src/aptale/export/assets/logo.txt`
    * `tests/export/test_pdf_export.py`
    * `docs/ux/export-branding.md`
  * **Step Dependencies**: Step 28
  * **User Instructions**: Install and verify the selected PDF library in the Docker image if it is not already available.

* [ ] Step 31: Implement WhatsApp attachment return flow

  * **Task**: Add the final response assembly that returns the quote summary in WhatsApp markdown and attaches the generated PDF or CSV as a document. Include the disclaimer directly in the chat response as well, not only in the file.
  * **Files**:

    * `src/aptale/flows/send_export.py`
    * `src/aptale/formatters/quote_summary.py`
    * `tests/flows/test_send_export.py`
  * **Step Dependencies**: Step 29, Step 30
  * **User Instructions**: Validate your Hermes deployment’s file attachment behavior in WhatsApp before beta rollout.

## 11. Persistent Memory & User Profiling

* [ ] Step 32: Implement user preference persistence rules

  * **Task**: Define how Aptale writes default currency, profit margin, preferred routes, and timezone into Hermes `USER.md` and `MEMORY.md` without storing raw invoice PII. Only durable preference data should persist.
  * **Files**:

    * `src/aptale/memory/profile_updates.py`
    * `src/aptale/memory/memory_policy.py`
    * `tests/memory/test_profile_updates.py`
    * `docs/implementation/memory-policy.md`
  * **Step Dependencies**: Step 4
  * **User Instructions**: None

* [ ] Step 33: Integrate Honcho context query conventions

  * **Task**: Add the query wrapper and prompting conventions for `query_user_context` so Aptale can adapt tone, brevity, and business context from Honcho while still using `USER.md` as the canonical place for operational settings. Hermes docs position Honcho as additive, not a replacement.  
  * **Files**:

    * `src/aptale/memory/honcho_profile.py`
    * `src/aptale/prompts/honcho_query.md`
    * `tests/memory/test_honcho_profile.py`
  * **Step Dependencies**: Step 32
  * **User Instructions**: Configure `HONCHO_API_KEY` and the workspace before enabling this in production.

* [ ] Step 34: Implement timezone capture and normalization

  * **Task**: Add explicit timezone detection/capture during onboarding and before alert scheduling. Normalize to IANA timezone strings and store the value in the user profile.
  * **Files**:

    * `src/aptale/memory/timezone.py`
    * `src/aptale/flows/onboarding_timezone.py`
    * `tests/memory/test_timezone.py`
  * **Step Dependencies**: Step 32
  * **User Instructions**: None

## 12. Conversational UX & Onboarding

* [ ] Step 35: Implement merchant onboarding prompts

  * **Task**: Create the first-run onboarding flow that collects default currency, destination country, common lanes, profit margin, timezone, and preference for concise vs. detailed replies. This should happen entirely within WhatsApp.
  * **Files**:

    * `src/aptale/flows/onboarding.py`
    * `src/aptale/prompts/onboarding.md`
    * `tests/flows/test_onboarding.py`
  * **Step Dependencies**: Step 34
  * **User Instructions**: None

* [ ] Step 36: Implement WhatsApp-native response style system

  * **Task**: Add reusable formatting helpers for short broker responses, detailed broker responses, warnings, disclaimers, and correction prompts. Ensure all responses stay inside WhatsApp-friendly markdown patterns.
  * **Files**:

    * `src/aptale/formatters/responses.py`
    * `tests/formatters/test_responses.py`
  * **Step Dependencies**: Step 12
  * **User Instructions**: None

## 13. Hooks, Privacy & Operational Monitoring

* [ ] Step 37: Implement PII redaction hook

  * **Task**: Build the Hermes hook that sanitizes supplier names, street-like addresses, invoice numbers, and raw pricing fields from step/end logs before they land in activity logs. The redactor must avoid mutating the actual WhatsApp response content.
  * **Files**:

    * `hermes/hooks/pii-redactor/handler.py`
    * `hermes/hooks/pii-redactor/README.md`
    * `tests/hooks/test_pii_redactor.py`
  * **Step Dependencies**: Step 4
  * **User Instructions**: Register the hook in your Hermes runtime and verify log output manually.

* [ ] Step 38: Implement WhatsApp session monitoring hook

  * **Task**: Build the gateway/session monitoring hook that alerts an admin webhook when the Baileys session disconnects or requires re-pairing. Hermes docs note temporary disconnections can be auto-handled but persistent failures require re-pairing. 
  * **Files**:

    * `hermes/hooks/whatsapp-monitor/handler.py`
    * `hermes/hooks/whatsapp-monitor/README.md`
    * `tests/hooks/test_whatsapp_monitor.py`
  * **Step Dependencies**: Step 7
  * **User Instructions**: Set `ADMIN_ALERT_WEBHOOK_URL` to a PagerDuty/Slack-compatible endpoint.

* [ ] Step 39: Add privacy notice and retention policy responses

  * **Task**: Implement reusable privacy notice content that Aptale can send on first invoice upload or when asked about data handling. Document log flushing expectations and sensitive-data boundaries.
  * **Files**:

    * `src/aptale/formatters/privacy_notice.py`
    * `docs/security/privacy.md`
    * `tests/formatters/test_privacy_notice.py`
  * **Step Dependencies**: Step 37
  * **User Instructions**: Define your operational log-retention interval and add it to the docs.

## 14. Scheduling & Proactive Alerts

* [ ] Step 40: Implement alert rule parsing

  * **Task**: Create the logic that turns a user’s natural-language threshold request into a validated alert rule schema: monitored dimension, comparison operator, threshold, schedule, timezone, and delivery target.
  * **Files**:

    * `src/aptale/alerts/parse_rule.py`
    * `src/aptale/prompts/alert_rule.md`
    * `tests/alerts/test_parse_rule.py`
  * **Step Dependencies**: Step 34
  * **User Instructions**: None

* [ ] Step 41: Implement cron prompt builder for Aptale alerts

  * **Task**: Build the self-contained cron prompt generator. Hermes cron runs in a fresh session with zero memory of the prior chat, so the prompt must include all sourcing context, target threshold, user timezone, delivery rules, and result/no-result behavior. Hermes gateway handles cron execution and can deliver back to the message origin.  
  * **Files**:

    * `src/aptale/alerts/build_cron_prompt.py`
    * `tests/alerts/test_build_cron_prompt.py`
  * **Step Dependencies**: Step 40
  * **User Instructions**: Install `croniter` if not already present for cron-expression support. Hermes docs call this out for cron expressions. 

* [ ] Step 42: Implement scheduled arbitrage monitoring flow

  * **Task**: Add the scheduling pathway that calls `schedule_cronjob` with the built prompt, local-time schedule, and `deliver="origin"` so alerts return to the same WhatsApp chat that created them.
  * **Files**:

    * `src/aptale/alerts/schedule_alert.py`
    * `tests/alerts/test_schedule_alert.py`
  * **Step Dependencies**: Step 41
  * **User Instructions**: Run the Hermes gateway continuously in production because the gateway daemon is what ticks cron jobs. 

* [ ] Step 43: Implement alert message formatter

  * **Task**: Format triggered alerts into short WhatsApp messages showing current rate/window, threshold crossed, sources, and recommended action framing. Include a disclaimer where the alert implies a trade or sourcing opportunity.
  * **Files**:

    * `src/aptale/formatters/alert_message.py`
    * `tests/formatters/test_alert_message.py`
  * **Step Dependencies**: Step 42
  * **User Instructions**: None

## 15. Reliability, Error Handling & Recovery

* [ ] Step 44: Implement user-facing outage and degraded-mode responses

  * **Task**: Centralize responses for portal outage, persistent CAPTCHA, unsupported route, missing FX sources, export generation failure, and WhatsApp attachment failure. Recovery options should be explicit and user-visible.
  * **Files**:

    * `src/aptale/errors/user_messages.py`
    * `tests/errors/test_user_messages.py`
  * **Step Dependencies**: Step 19, Step 31
  * **User Instructions**: None

* [ ] Step 45: Add source-audit trail assembly

  * **Task**: Build a compact internal source trail object that keeps URLs, timestamps, source types, and whether the data came from official portal or open-web discovery, so the final quote/export can remain auditable.
  * **Files**:

    * `src/aptale/audit/source_trail.py`
    * `tests/audit/test_source_trail.py`
  * **Step Dependencies**: Step 18
  * **User Instructions**: None

## 16. Evaluation, Tests & Batch Validation

* [ ] Step 46: Add invoice fixture set and evaluation dataset

  * **Task**: Create representative sample invoice fixtures and a JSONL eval dataset for batch testing extraction, clarification, and routing. Include multilingual cases and failure cases.
  * **Files**:

    * `fixtures/invoices/README.md`
    * `fixtures/invoices/sample_en.json`
    * `fixtures/invoices/sample_cn.json`
    * `fixtures/invoices/sample_tr.json`
    * `fixtures/invoices/blurry_failure.json`
    * `data/eval_invoices.jsonl`
  * **Step Dependencies**: Step 14
  * **User Instructions**: Add real anonymized samples later, after internal privacy review.

* [ ] Step 47: Implement batch routing evaluation harness

  * **Task**: Add a batch-runner wrapper that verifies the routing flow triggers delegation correctly, validates subagent JSON shape, and records pass/fail metrics for extraction confirmation and sourcing readiness.
  * **Files**:

    * `tests/evals/test_batch_routing.py`
    * `scripts/run_batch_eval.sh`
    * `docs/testing/batch-eval.md`
  * **Step Dependencies**: Step 17, Step 46
  * **User Instructions**: Run batch eval against the fixture dataset before each skills-repo release.

* [ ] Step 48: Add sandbox/export unit tests

  * **Task**: Create deterministic unit tests for landed-cost calculations, CSV/PDF export generation, branded footer presence, and disclaimer injection.
  * **Files**:

    * `tests/evals/test_landed_cost_end_to_end.py`
    * `tests/evals/test_exports_end_to_end.py`
  * **Step Dependencies**: Step 30
  * **User Instructions**: None

* [ ] Step 49: Add gateway resiliency and auth tests

  * **Task**: Add tests and scripted checks for network-drop recovery assumptions, unauthorized-number denial, and allowlist-only MVP behavior. Hermes WhatsApp gateway reconnects automatically in temporary cases, but production should still alert on session breakage.  
  * **Files**:

    * `tests/gateway/test_authorization_policy.py`
    * `tests/gateway/test_session_monitoring.py`
    * `docs/testing/gateway-resiliency.md`
  * **Step Dependencies**: Step 7, Step 38
  * **User Instructions**: Test using at least one unauthorized number and one allowed beta number.

## 17. Production Packaging & Runbooks

* [ ] Step 50: Add Docker and production runtime packaging

  * **Task**: Create the production Dockerfile and compose/service examples for Hermes gateway, Node bridge dependencies, persistent volumes, and healthcheck strategy. Keep the runtime explicit and simple.
  * **Files**:

    * `Dockerfile`
    * `docker-compose.yml`
    * `deploy/systemd/aptale-gateway.service`
    * `docs/deploy/production.md`
  * **Step Dependencies**: Step 38, Step 42
  * **User Instructions**: Use a highly available host/VPS and mount persistent volumes for `~/.hermes`.

* [ ] Step 51: Add operator runbooks

  * **Task**: Write runbooks for first deploy, WhatsApp re-pair, private skill refresh, gateway restart, portal outage handling, and safe log cleanup.
  * **Files**:

    * `docs/runbooks/first-deploy.md`
    * `docs/runbooks/whatsapp-repair.md`
    * `docs/runbooks/skills-update.md`
    * `docs/runbooks/incident-portal-outage.md`
    * `docs/runbooks/log-rotation.md`
  * **Step Dependencies**: Step 50
  * **User Instructions**: Keep these runbooks private if they contain operational endpoints or secret locations.

* [ ] Step 52: Add launch checklist and phased beta controls

  * **Task**: Create the final launch checklist covering allowlist population, webhook alerts, skills tap auth, Browserbase proxy test, Honcho connectivity, export generation test, and cron alert smoke test.
  * **Files**:

    * `docs/release/beta-launch-checklist.md`
    * `docs/release/post-launch-observability.md`
  * **Step Dependencies**: Step 51
  * **User Instructions**: Complete the checklist before admitting each new beta tester.

## 18. Optional Post-MVP Extensions

* [ ] Step 53: Add additional lane packs and customs coverage expansion

  * **Task**: Extend the skills repo with more country/route skills based on beta traffic patterns, keeping the same JSON contracts and fail-fast rules.
  * **Files**:

    * `aptale-skills/regions/<new-region>.md`: New region skills as needed.
    * `docs/release/coverage-roadmap.md`: Expansion priorities.
  * **Step Dependencies**: Step 52
  * **User Instructions**: Prioritize only lanes that appear repeatedly in beta usage.

* [ ] Step 54: Add quote-history summarization without storing raw invoice data

  * **Task**: Implement an optional feature that stores aggregate quote metrics and lane trends without retaining supplier-identifying raw invoice content.
  * **Files**:

    * `src/aptale/analytics/quote_metrics.py`
    * `tests/analytics/test_quote_metrics.py`
    * `docs/security/aggregate-analytics.md`
  * **Step Dependencies**: Step 39
  * **User Instructions**: Review privacy implications before enabling.

This plan treats Aptale as a Hermes-native, WhatsApp-only agent system rather than a traditional dashboard app. The implementation order starts with runtime structure and Hermes setup, then locks in strict JSON contracts, then builds the invoice→clarify→delegate→calculate→export loop, and only after that adds memory, hooks, alerts, testing, and production packaging.

Key considerations:

* Keep one canonical path everywhere; do not add legacy compatibility branches.
* Validate extraction before any expensive subagent work.
* Pass exhaustive context to every delegated task because Hermes children are isolated and restricted. 
* Use skills for routing/procedural sourcing logic, not custom core tools, unless a capability truly requires new integrated tooling. 
* Treat cron prompts as self-contained fresh sessions, and keep the gateway running for both WhatsApp and scheduled alerts. 
* Keep PII out of logs and durable memory, while using `USER.md` plus Honcho for durable preference modeling.
