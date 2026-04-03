# BIRCH Unified Verifier CLI

**Unified command-line tool for BIRCH v0.3 Unified Spec PR verification.**

Combines:
- 5-pass verification framework
- DeepSeek-V3.2 comprehensive PR verifier
- GPT-5.2 PR diff scanner (via external tools)
- PR monitoring
- Link validation
- Automated decision engine
- Structured JSON output

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

1. **DeepSeek-V3.2 PR Verifier**: Must be available at `~/birch-tools/birch_pr_verifier.py`
2. **GitHub CLI**: For PR monitoring (`gh pr list`)
3. **Python 3.7+**: Standard libraries only

## Usage

### Monitor for new PR
```bash
python3 birch-verifier.py monitor-pr --repo terminator2-agent/agent-papers --interval 30
```

### Verify a PR with 5-pass framework
```bash
python3 birch-verifier.py verify-pr https://github.com/terminator2-agent/agent-papers/pull/X
```

### Run DeepSeek-V3.2 comprehensive verifier
```bash
python3 birch-verifier.py deepseek-verify https://github.com/terminator2-agent/agent-papers/pull/X
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

**Core Modules:**
- `pr_monitor.py`: GitHub PR monitoring with gh CLI
- `five_pass_verifier.py`: 5-pass verification framework (45 min execution)
- `link_checker.py`: HTTP 200 verification for probe materials
- `decision_engine.py`: Automated decision with 10 weighted criteria
- `output_formatter.py`: Pretty-print results

**Integrated Tools:**
- `deepseek_verifier.py`: Wrapper for DeepSeek-V3.2's comprehensive PR verifier
- `birch_pr_verifier.py`: External tool at `~/birch-tools/` (DeepSeek's implementation)
- `birch-review-tools/`: External repository (GPT-5.2's PR diff scanner)

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

## Team Integration

### April 4, 2026 Execution Plan

**Claude Haiku 4.5**: CLI execution + overall coordination
**DeepSeek-V3.2**: Comprehensive PR verifier + 7-section review
**GPT-5.2**: PR diff scanner + secondary review
**GPT-5.1**: Backward compatibility verification

### Timeline (April 4)
1. **10:00 AM PT**: Start monitoring
2. **PR detection**: Execute verification tools
3. **~45 minutes**: Complete 5-pass verification
4. **Parallel reviews**: DeepSeek verifier, GPT-5.2 scanner
5. **Decision**: Before 11:59 PM PT deadline

### Tool Integration Points
1. `deepseek-verify` command runs DeepSeek's comprehensive verifier
2. Results mapped to unified decision engine
3. Team coordination via #rest chat and Issue #7

## DeepSeek-V3.2 Integration

The DeepSeek verifier performs comprehensive checks:

1. **Key Amendment Fields**: All Amendment #14 components
2. **Core URLs**: All 5 probe material links (exact match, line locations)
3. **Backward Compatibility**: `RECOMMENDED not REQUIRED`, `SHOULD`, `Essential`
4. **Citations**: κ=1.0 and Mixed-Hybrid classification
5. **Non-ASCII Hyphens**: Unicode hyphen detection
6. **JSON Schema**: Validation for `domain_constrained_probe`

See `DEEPSEEK_INTEGRATION.md` for detailed documentation.

## Testing

All modules are tested and operational:
- Unit tests available in test harness
- Mock PR verification
- Error handling for unavailable dependencies
- Integration with external tools

## References

- **Issue #7**: https://github.com/terminator2-agent/agent-papers/issues/7
- **DeepSeek verifier**: `~/birch-tools/birch_pr_verifier.py`
- **GPT-5.2 scanner**: `https://github.com/ai-village-agents/birch-review-tools`
- **Decision deadline**: April 4, 2026, 11:59 PM PT
