# Batch Routing Evaluation

This guide covers Aptale's Step-47 batch routing harness.

It validates the routing path against `data/eval_invoices.jsonl` by checking:

- extraction confirmation succeeds after clarification
- sourcing readiness reaches `route_resolved`
- delegation task planning is triggered with exactly `freight`, `customs`, `fx`
- subagent output JSON shape passes strict contract parsing

The harness records pass/fail metrics to a JSON file so each release has a routing-quality artifact.

## Run

```bash
./scripts/run_batch_eval.sh
```

Using custom dataset/metrics paths:

```bash
APTALE_BATCH_ROUTING_DATASET=/abs/path/eval_invoices.jsonl \
APTALE_BATCH_ROUTING_METRICS_PATH=/abs/path/batch_routing_metrics.json \
./scripts/run_batch_eval.sh
```

You can pass extra `pytest` flags through the script:

```bash
./scripts/run_batch_eval.sh -k routing -vv
```

## Output

Default metrics path:

- `runtime/evals/batch_routing_metrics.json`

Metrics include:

- evaluated case count
- pass/fail counts for:
  - extraction confirmation
  - sourcing readiness
  - delegation trigger
  - subagent JSON shape validation
- per-case status rows for troubleshooting

## Hermes Alignment

The harness follows Hermes batch-processing and delegation conventions:

- dataset remains JSONL with required `prompt` fields
- routing/delegation checks assume subagent isolation and explicit parent context
- JSON-shape validation is enforced through strict delegated result parsing

Run this before each skills-repo release to catch routing regressions early.
