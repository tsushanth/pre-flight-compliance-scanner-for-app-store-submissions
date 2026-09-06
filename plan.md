# Pre-Flight Compliance Scanner — Local MVP Plan

## Goal of this MVP

Prove the core value — *point the tool at an iOS app's source/config files and get
back a list of likely App Store rejection triggers, each with a guideline
reference, a confidence score, and a suggested fix* — as a local CLI run against
a fixture project. No deployment, no real App Store Connect integration, no
dynamic/on-device analysis.

## 1. Stack

**Python 3 (stdlib only).**

Reasons:
- The inputs we need to inspect (`Info.plist`, `PrivacyInfo.xcprivacy`,
  entitlements files, `.swift`/`.m` source, an unzipped `.ipa`) are all handled
  by stdlib modules: `plistlib`, `zipfile`, `re`, `pathlib`, `json`.
- No dependency install step needed to run the demo — `python3 scanner/cli.py ...`
  just works.
- A rules engine is fundamentally "read some files, pattern-match, emit
  findings" — this doesn't need a web framework, a database, or async
  machinery.
- Avoids picking Node/TS or Go for no reason other than familiarity; Python's
  built-in plist/zip support is the deciding factor over Node (would need a
  plist-parsing package) and Go (more ceremony for a scripting task).

The "web dashboard" from the pitch is represented in this MVP as a single
static HTML file generated locally from the same JSON findings the CLI
prints — opened directly in a browser (`file://`), no server process. This is
enough to demo "dashboard shows findings with confidence + fix," which is the
actual value being tested, without standing up a web app.

## 2. Explicitly out of scope for this MVP

- Auth, accounts, billing, multi-tenancy — nothing here needs a "user."
- Hosting/deploy (no server, no cloud, no Docker) — it's a script you run
  locally.
- Real App Store Connect API integration — no API keys, no network calls.
  Guideline text/stats are a small static local JSON file, not fetched live.
- Actual binary disassembly or code signing/entitlement validation against
  Apple's real toolchain — we pattern-match on source/config text, not a real
  Mach-O parse.
- Dynamic analysis (actually launching/running the app, crash reproduction) —
  guideline 2.1 "crash" detection is static heuristic pattern-matching (e.g.
  force-unwraps, unhandled `try!`, obvious nil-deref patterns), not a real
  runtime.
- CI integration (GitHub Actions config, webhooks) — the pitch mentions CI,
  but the CLI itself is the reusable unit; wiring it into a pipeline is a
  packaging concern for later, not needed to prove the core detection value.
- Any AI/LLM-based "reviewer emulation" — the automated-reviewer-quirks angle
  is represented by a couple of specific static heuristics (e.g. metadata
  keyword stuffing for 4.3), not a model call.
- Multiple/real sample apps — one small synthetic fixture project is enough
  to exercise each rule.

The only reason any of the above would be in scope is if the core value were
*impossible* to demonstrate without it — none of them meet that bar; the
value is "static analysis finds real issues with actionable output," which a
local script fully proves.

## 3. File / directory layout

```
pre-flight-compliance-scanner-for-app-store-submis/
├── plan.md
├── scanner/
│   ├── __init__.py
│   ├── cli.py                 # argparse entry point: `scan <path> [--out report.html]`
│   ├── models.py               # Finding dataclass (guideline, title, confidence, evidence, fix)
│   ├── report.py                # renders findings -> JSON (stdout) and a static HTML file
│   ├── ruleset/
│   │   └── guidelines.json      # static reference data: guideline id/title/text/rejection-rate
│   └── rules/
│       ├── __init__.py          # registers all rule checks for the CLI to run
│       ├── guideline_4_3.py     # duplicate/spam heuristics (near-identical bundle id/name/desc patterns, keyword stuffing)
│       ├── guideline_2_1.py     # crash-prone static patterns (force unwraps, unhandled try!, etc.)
│       ├── privacy_manifest.py  # PrivacyInfo.xcprivacy presence + required-reason API usage vs declared reasons
│       ├── iot_device.py        # IoT/accessory guideline heuristics (e.g. HomeKit/Bluetooth usage without required disclosures)
│       └── ugc_moderation.py    # UGC features (chat/comments/upload) detected without visible moderation/report/block hooks
├── sample_app/                  # synthetic fixture iOS project used for the demo run
│   ├── Info.plist
│   ├── PrivacyInfo.xcprivacy
│   ├── entitlements.plist
│   └── Sources/
│       ├── ChatViewController.swift   # trips ugc_moderation (chat feature, no moderation)
│       ├── NetworkManager.swift       # trips guideline_2_1 (force unwraps) + privacy_manifest gap
│       └── AccessoryPairing.swift     # trips iot_device heuristic
└── tests/
    ├── test_rules.py            # one clean-fixture + one violation-fixture case per rule module
    └── test_report.py           # findings -> JSON/HTML rendering smoke test
```

## 4. Verification

- **Unit tests (`pytest tests/`)**: for each rule module, one test asserting
  it stays silent on a clean fixture snippet and one asserting it fires (with
  the expected guideline id and a confidence score in `[0,1]`) on a
  known-bad snippet.
- **Manual run-through**:
  1. `python3 -m scanner.cli scan sample_app/` — prints a findings table to
     stdout (guideline, confidence, evidence line, suggested fix) and exits
     non-zero if any high-confidence finding exists (proves CI-style
     usability without actually wiring CI).
  2. `python3 -m scanner.cli scan sample_app/ --out report.html && open report.html`
     — confirms the static "dashboard" view renders the same findings
     legibly in a browser.
  3. Re-run against a copy of `sample_app/` with the flagged issues fixed
     (moderation hook added, force-unwraps removed, privacy manifest entry
     added) and confirm the finding count drops to zero — this is the actual
     proof that detections are meaningful rather than always-on noise.
