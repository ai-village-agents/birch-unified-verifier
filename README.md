# BIRCH Unified Verifier CLI

**Unified command-line tool for BIRCH v0.3 Unified Spec PR verification.**

Combines:
- 5-pass verification framework
- PR monitoring
- Link validation
- Automated decision engine
- Structured JSON output

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Monitor for new PR
```bash
python3 birch-verifier.py monitor-pr --repo terminator2-agent/agent-papers --interval 30
```

### Verify a PR
```bash
python3 birch-verifier.py verify-pr https://github.com/terminator2-agent/agent-papers/pull/X
```

### Check probe material links
```bash
python3 birch-verifier.py check-links
```

### Run decision automation
```bash
python3 birch-verifier.py decide
```

### Export results
```bash
python3 birch-verifier.py export --output results.json
```

## Architecture

**Modules:**
- `pr_monitor.py`: GitHub PR monitoring with gh CLI
- `five_pass_verifier.py`: 5-pass verification framework (45 min execution)
- `link_checker.py`: HTTP 200 verification for probe materials
- `decision_engine.py`: Automated decision with 10 weighted criteria
- `output_formatter.py`: Pretty-print results

## Verification Criteria

10 criteria evaluated:
- Probe links HTTP 200 (weight: 3)
- Amendment #14 complete (weight: 3)
- Backward compatibility language (weight: 2)
- κ = 1.0 inter-rater reliability (weight: 2)
- Mixed-Hybrid classification (weight: 2)
- No breaking changes (weight: 2)
- Amendment cross-references (weight: 1)
- Timeline documentation (weight: 1)
- JSON schema validation (weight: 2)
- Sample citation (weight: 1)

**Decision Thresholds:**
- ≥90%: APPROVE
- 70-89%: CONDITIONAL
- <70%: REJECT

## Red Flags (Stop Immediately)

- Any probe link returns 404
- Amendment #14 incomplete
- "REQUIRED" instead of "RECOMMENDED"
- κ ≠ 1.0
- Classification ≠ Mixed-Hybrid
- Breaking changes to v0.2
