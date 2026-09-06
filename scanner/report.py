"""Renders findings to JSON (stdout) and a static, self-contained HTML file
(the "dashboard")."""

import html
import json
from dataclasses import asdict

from .models import load_guidelines


def findings_to_dicts(findings):
    return [asdict(f) for f in findings]


def findings_to_json(findings):
    return json.dumps(findings_to_dicts(findings), indent=2)


def _confidence_class(confidence):
    if confidence >= 0.6:
        return "high"
    if confidence >= 0.4:
        return "medium"
    return "low"


def _row_html(finding, guidelines):
    guideline_info = guidelines.get(finding.guideline, {})
    guideline_title = html.escape(guideline_info.get("title", finding.guideline))
    location = finding.file + (f":{finding.line}" if finding.line else "")
    return f"""
    <tr class="confidence-{_confidence_class(finding.confidence)}">
      <td>{html.escape(guideline_title)}</td>
      <td>{finding.confidence:.2f}</td>
      <td>{html.escape(finding.title)}</td>
      <td><code>{html.escape(location)}</code></td>
      <td><code>{html.escape(finding.evidence)}</code></td>
      <td>{html.escape(finding.fix)}</td>
    </tr>"""


def findings_to_html(findings, source=""):
    guidelines = load_guidelines()
    rows = "".join(_row_html(f, guidelines) for f in findings)
    body = rows if findings else '<tr><td colspan="6">No likely rejection triggers found.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Pre-Flight Compliance Scanner Report</title>
<style>
  body {{ font-family: -apple-system, sans-serif; margin: 2rem; color: #1c1c1e; }}
  h1 {{ font-size: 1.4rem; }}
  .source {{ color: #666; margin-bottom: 1.5rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; vertical-align: top; }}
  th {{ background: #f5f5f7; }}
  tr.confidence-high {{ background: #fdecea; }}
  tr.confidence-medium {{ background: #fff8e1; }}
  tr.confidence-low {{ background: #f1f8f4; }}
  code {{ font-size: 0.85em; }}
</style>
</head>
<body>
  <h1>Pre-Flight Compliance Scanner Report</h1>
  <p class="source">Scanned: <code>{html.escape(str(source))}</code> &mdash; {len(findings)} finding(s)</p>
  <table>
    <thead>
      <tr>
        <th>Guideline</th>
        <th>Confidence</th>
        <th>Finding</th>
        <th>Location</th>
        <th>Evidence</th>
        <th>Suggested fix</th>
      </tr>
    </thead>
    <tbody>{body}
    </tbody>
  </table>
</body>
</html>
"""
