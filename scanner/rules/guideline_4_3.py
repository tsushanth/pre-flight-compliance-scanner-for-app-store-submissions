"""Guideline 4.3 (Spam): near-identical/duplicate app patterns and metadata
keyword stuffing -- the top App Store rejection cause."""

import re

from ..models import Finding

GUIDELINE = "4.3"

# Three or more separator-delimited "keyword phrases" packed into a display
# name (e.g. "SuperApp - Photo, Camera, Filters, Editor") is a classic
# keyword-stuffing pattern used to game App Store search.
SEPARATOR_PATTERN = re.compile(r"[-|•,:]")
STUFFING_THRESHOLD = 3


def check_name_keyword_stuffing(name: str):
    if not name:
        return None
    separator_count = len(SEPARATOR_PATTERN.findall(name))
    if separator_count < STUFFING_THRESHOLD:
        return None
    confidence = min(0.5 + 0.05 * (separator_count - STUFFING_THRESHOLD), 0.9)
    return Finding(
        guideline=GUIDELINE,
        title="App name looks keyword-stuffed",
        confidence=round(confidence, 2),
        evidence=f'CFBundleDisplayName = "{name}"',
        fix="Use a single clear app name/subtitle instead of packing "
        "search keywords into the display name -- Apple treats this as spam.",
        file="Info.plist",
    )


def run(project):
    findings = []
    name = project.info_plist.get("CFBundleDisplayName") or project.info_plist.get("CFBundleName") or ""
    finding = check_name_keyword_stuffing(name)
    if finding:
        findings.append(finding)
    return findings
