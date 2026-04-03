"""Integration helpers for external verification tools.

This module provides small wrappers around:
- DeepSeek-V3.2's BIRCH PR verifier script
- GPT-5.2's birch-review-tools PR diff scanner
- GPT-5.1's encoding-scan helper for non-ASCII / URL risk

All helpers are best-effort: if a tool is missing, they return a
structured "SKIPPED" result rather than raising.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Normalized result structure for external tool invocations."""

    tool: str
    invoked: bool
    status: str
    returncode: Optional[int] = None
    script_path: Optional[str] = None
    helper_path: Optional[str] = None
    spec_path: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    parsed_json: Optional[Any] = None
    reason: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _run_subprocess(script: Path, args: list[str], timeout: int, tool_name: str) -> ToolResult:
    """Helper to run a Python subprocess and capture output safely."""

    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        parsed: Optional[Any] = None
        # Best-effort JSON parse of stdout
        try:
            parsed = json.loads(proc.stdout)
        except Exception:
            parsed = None

        status = "OK" if proc.returncode == 0 else "ERROR"
        return ToolResult(
            tool=tool_name,
            invoked=True,
            status=status,
            returncode=proc.returncode,
            script_path=str(script),
            stdout=proc.stdout,
            stderr=proc.stderr,
            parsed_json=parsed,
        )
    except Exception as exc:  # noqa: BLE001
        return ToolResult(
            tool=tool_name,
            invoked=True,
            status="ERROR",
            error=str(exc),
            script_path=str(script),
        )


def run_deepseek_verifier(pr_url: str, script_path: Optional[Path] = None) -> Dict[str, Any]:
    """Run DeepSeek's birch_pr_verifier.py, if available.

    Returns a serializable dict summarizing the outcome.
    """

    home = Path.home()
    script = script_path or home / "birch-tools" / "birch_pr_verifier.py"

    if not script.is_file():
        return ToolResult(
            tool="deepseek_verifier",
            invoked=False,
            status="SKIPPED",
            reason="script_not_found",
            script_path=str(script),
        ).to_dict()

    result = _run_subprocess(script, [pr_url], timeout=120, tool_name="deepseek_verifier")
    return result.to_dict()


def run_gpt52_scanner(pr_url: str, repo_path: Optional[Path] = None) -> Dict[str, Any]:
    """Run GPT-5.2's birch_v03_pr_scanner.py, if available.

    By default this looks for ~/birch-review-tools/birch_v03_pr_scanner.py.
    """

    home = Path.home()
    repo = repo_path or home / "birch-review-tools"
    script = repo / "birch_v03_pr_scanner.py"

    if not script.is_file():
        return ToolResult(
            tool="gpt52_pr_scanner",
            invoked=False,
            status="SKIPPED",
            reason="script_not_found",
            script_path=str(script),
        ).to_dict()

    result = _run_subprocess(script, [pr_url], timeout=180, tool_name="gpt52_pr_scanner")
    return result.to_dict()


def run_encoding_scan(spec_path: Optional[str], helper_path: Optional[Path] = None) -> Dict[str, Any]:
    """Run GPT-5.1's encoding-scan helper on a unified spec path, if available."""

    if not spec_path:
        return ToolResult(
            tool="encoding_scan",
            invoked=False,
            status="SKIPPED",
            reason="no_spec_path_provided",
            spec_path=spec_path,
        ).to_dict()

    home = Path.home()
    helper = helper_path or home / "framework-reflections-2026" / "analysis" / "run_encoding_scan_helper.py"

    if not helper.is_file():
        return ToolResult(
            tool="encoding_scan",
            invoked=False,
            status="SKIPPED",
            reason="helper_not_found",
            helper_path=str(helper),
            spec_path=spec_path,
        ).to_dict()

    # For the encoding scan we keep stdout as free-form text and do not
    # attempt JSON parsing; callers can inspect stdout if they want more detail.
    try:
        proc = subprocess.run(
            [sys.executable, str(helper), spec_path],
            capture_output=True,
            text=True,
            timeout=180,
        )
        status = "OK" if proc.returncode == 0 else "ERROR"
        return ToolResult(
            tool="encoding_scan",
            invoked=True,
            status=status,
            helper_path=str(helper),
            spec_path=spec_path,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        ).to_dict()
    except Exception as exc:  # noqa: BLE001
        return ToolResult(
            tool="encoding_scan",
            invoked=True,
            status="ERROR",
            helper_path=str(helper),
            spec_path=spec_path,
            error=str(exc),
        ).to_dict()

