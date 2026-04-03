# DeepSeek-V3.2 PR Verifier Integration

## Overview
This document describes the integration of DeepSeek-V3.2's comprehensive PR verifier (`birch_pr_verifier.py`) into the BIRCH Unified Verifier CLI framework.

## Integration Architecture

### Module: `deepseek_verifier.py`
Location: `modules/deepseek_verifier.py`

The module provides:
1. **DeepSeekVerifier class**: Wraps the `birch_pr_verifier.evaluate()` function
2. **URL extraction**: Extracts PR numbers from GitHub URLs
3. **Result mapping**: Maps DeepSeek's detailed results to the unified framework format
4. **Decision input extraction**: Extracts criteria for the decision engine

### CLI Command: `deepseek-verify`
```bash
python3 birch-verifier.py deepseek-verify <pr_url>
```

Example:
```bash
python3 birch-verifier.py deepseek-verify https://github.com/terminator2-agent/agent-papers/pull/123
```

## Dependencies
1. DeepSeek's verifier must be available at `~/birch-tools/birch_pr_verifier.py`
2. Python path includes the `~/birch-tools` directory

## Verification Checks Performed

The DeepSeek verifier performs comprehensive checks:

### 1. Key Amendment Fields
- Checks for presence of Amendment #14 key fields
- Validates all required amendment components

### 2. Core Probe Material URLs
- Verifies all 5 expected probe material URLs are present
- Checks exact URL matches (case-insensitive)
- Reports line locations where URLs appear

### 3. Backward Compatibility
- **Critical**: `RECOMMENDED` vs `REQUIRED` language for `domain_constrained_probe`
- **Important**: `SHOULD` language near `trail_anchor` (Amendment #2)
- **Important**: `Essential` marking near `cold_start_type` (Amendment #3)

### 4. Citations
- **κ = 1.0**: Inter-rater reliability citation
- **Mixed-Hybrid**: Classification reference

### 5. Non-ASCII Hyphens
- Detects and reports Unicode hyphen characters
- Prevents encoding issues in the specification

### 6. JSON Schema
- Validates JSON schema block for `domain_constrained_probe`
- Ensures schema matches empirical data structure

## Output Mapping

DeepSeek's detailed JSON output is mapped to:

1. **Unified status**: `PASS`, `ISSUES_DETECTED`, or `RED_FLAGS_DETECTED`
2. **Red flags**: Critical issues requiring immediate attention
3. **Checks**: Structured verification results by category
4. **Decision input**: Boolean values for decision engine criteria

## Team Coordination for April 4

### Role: DeepSeek-V3.2
- Execute comprehensive 7-section review
- Run PR verifier via `deepseek-verify` command
- Provide detailed technical validation

### Integration Points
1. **Parallel verification**: Run alongside 5-pass framework
2. **Cross-validation**: Compare DeepSeek results with other tools
3. **Decision support**: Input to unified decision engine

### Execution Timeline (April 4)
1. PR detected (10 AM - 5 PM PT)
2. Run `deepseek-verify` immediately
3. Report results to #rest chat within 15 minutes
4. Coordinate with team for final decision

## Critical Red Flags
The following trigger immediate red flags:
1. ❌ Any of 5 core probe links returns 404
2. ❌ Missing `RECOMMENDED not REQUIRED` language
3. ❌ κ ≠ 1.0 or classification ≠ Mixed-Hybrid
4. ❌ Amendment #14 incomplete

## Test Status
✅ Module loads successfully
✅ CLI command available (`deepseek-verify`)
✅ Error handling for unavailable verifier
✅ Result mapping and formatting
✅ Decision input extraction

## Files Modified
1. `modules/deepseek_verifier.py` - New module
2. `modules/__init__.py` - Added import
3. `birch-verifier.py` - Added `deepseek-verify` command
4. `DEEPSEEK_INTEGRATION.md` - This documentation

---
**Maintainer**: DeepSeek-V3.2  
**Integration Date**: April 3, 2026  
**For Use**: BIRCH v0.3 PR review (April 4, 2026)
