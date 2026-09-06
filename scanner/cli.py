"""argparse entry point: `python3 -m scanner.cli scan <path> [--out report.html]`"""

import argparse
import sys
from pathlib import Path

from .models import Project
from .report import findings_to_html, findings_to_json
from .rules import RULES

HIGH_CONFIDENCE_THRESHOLD = 0.6


def build_parser():
    parser = argparse.ArgumentParser(
        prog="scanner",
        description="Pre-Flight Compliance Scanner for App Store Submissions",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan an iOS app project for likely App Store rejection triggers")
    scan_parser.add_argument("path", help="Path to the app project directory (or a .ipa file)")
    scan_parser.add_argument("--out", help="Write an HTML report to this path", default=None)
    scan_parser.add_argument("--json", action="store_true", help="Print findings as JSON instead of a table")

    return parser


def collect_findings(project):
    findings = []
    for rule in RULES:
        findings.extend(rule.run(project))
    findings.sort(key=lambda f: f.confidence, reverse=True)
    return findings


def print_table(findings):
    if not findings:
        print("No likely rejection triggers found.")
        return

    header = f"{'GUIDELINE':<10}{'CONF':<6}{'TITLE':<50}{'LOCATION'}"
    print(header)
    print("-" * len(header))
    for finding in findings:
        location = finding.file + (f":{finding.line}" if finding.line else "")
        print(f"{finding.guideline:<10}{finding.confidence:<6.2f}{finding.title[:50]:<50}{location}")
        print(f"    evidence: {finding.evidence}")
        print(f"    fix:      {finding.fix}")
        print()


def run_scan(args):
    project = Project.load(args.path)
    findings = collect_findings(project)

    if args.json:
        print(findings_to_json(findings))
    else:
        print_table(findings)

    if args.out:
        html_report = findings_to_html(findings, source=args.path)
        Path(args.out).write_text(html_report, encoding="utf-8")
        print(f"\nWrote HTML report to {args.out}")

    high_confidence_count = sum(1 for f in findings if f.confidence >= HIGH_CONFIDENCE_THRESHOLD)
    return 1 if high_confidence_count else 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
