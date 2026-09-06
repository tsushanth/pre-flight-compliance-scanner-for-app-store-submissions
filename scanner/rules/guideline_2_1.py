"""Guideline 2.1 (App Completeness): static heuristics for crash-prone
patterns -- force unwraps and unhandled `try!` -- since we have no runtime
to actually reproduce a crash."""

import re

from ..models import Finding

GUIDELINE = "2.1"

TRY_BANG_PATTERN = re.compile(r"\btry!\s")
# Matches a force-unwrap `!` following an identifier/`)`/`]`, but not `!=`/`!==`.
FORCE_UNWRAP_PATTERN = re.compile(r"[A-Za-z0-9_\)\]]!(?!=)")
# Implicitly-unwrapped-optional type declarations (e.g. `var x: Foo!`) are an
# idiomatic pattern, not a force-unwrap-at-use-site crash risk -- skip them.
IUO_DECLARATION_PATTERN = re.compile(r"\b(var|let)\s+\w+\s*:\s*[\w<>\[\].]+!\s*$")


def scan_source(filename, text):
    findings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if IUO_DECLARATION_PATTERN.search(line):
            continue
        if TRY_BANG_PATTERN.search(line):
            findings.append(
                Finding(
                    guideline=GUIDELINE,
                    title="Unhandled `try!` can crash at runtime",
                    confidence=0.6,
                    evidence=line.strip(),
                    fix="Replace `try!` with `try?` or a `do/catch` that "
                    "handles the error instead of trapping.",
                    file=filename,
                    line=line_no,
                )
            )
        elif FORCE_UNWRAP_PATTERN.search(line):
            findings.append(
                Finding(
                    guideline=GUIDELINE,
                    title="Force-unwrapped optional can crash at runtime",
                    confidence=0.5,
                    evidence=line.strip(),
                    fix="Use optional binding (`if let`/`guard let`) or "
                    "nil-coalescing instead of force-unwrapping with `!`.",
                    file=filename,
                    line=line_no,
                )
            )
    return findings


def run(project):
    findings = []
    for path, text in project.source_files.items():
        findings.extend(scan_source(path, text))
    return findings
