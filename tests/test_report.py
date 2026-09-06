"""Findings -> JSON/HTML rendering smoke test."""

import json

from scanner.models import Finding
from scanner.report import findings_to_html, findings_to_json

SAMPLE_FINDINGS = [
    Finding(
        guideline="4.3",
        title="App name looks keyword-stuffed",
        confidence=0.65,
        evidence='CFBundleDisplayName = "SuperApp - Photo, Camera"',
        fix="Use a single clear app name.",
        file="Info.plist",
    ),
]


def test_findings_to_json_round_trips():
    payload = json.loads(findings_to_json(SAMPLE_FINDINGS))
    assert len(payload) == 1
    assert payload[0]["guideline"] == "4.3"
    assert payload[0]["confidence"] == 0.65


def test_findings_to_json_empty():
    assert json.loads(findings_to_json([])) == []


def test_findings_to_html_contains_finding():
    output = findings_to_html(SAMPLE_FINDINGS, source="sample_app/")
    assert "<html" in output
    assert "4.3" in output
    assert "App name looks keyword-stuffed" in output
    assert "sample_app/" in output


def test_findings_to_html_handles_no_findings():
    output = findings_to_html([], source="clean_app/")
    assert "No likely rejection triggers found." in output
