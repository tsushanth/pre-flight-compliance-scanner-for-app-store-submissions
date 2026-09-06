# Pre-Flight Compliance Scanner (Local MVP)

A CLI tool that statically scans an iOS app's source, `Info.plist`,
entitlements, and privacy manifest for patterns that commonly get App Store
submissions rejected — before you submit. Each finding includes the Apple
Review Guideline it maps to, a confidence score, the evidence line, and a
suggested fix.

This is a local MVP: no server, no App Store Connect API calls, no account
system. See `plan.md` for the full scope and rationale.

## What it checks

| Guideline | Check |
|---|---|
| 4.3 Spam | App display name stuffed with search keywords |
| 2.1 App Completeness | Force-unwrapped optionals and unhandled `try!` (crash-prone patterns) |
| 5.1.1 Data Collection | Missing `PrivacyInfo.xcprivacy`, or a required-reason API (e.g. `UserDefaults`) used without a declared reason |
| 2.5.6 Hardware/Accessory Use | Bluetooth or HomeKit APIs used without the matching `Info.plist` usage-description string |
| 1.2 User-Generated Content | Chat/comment/upload features found with no report/block/moderation logic anywhere in the project |

All detection is static pattern-matching over source/config text — there's
no binary disassembly, no code signing validation, and no LLM call involved.

## Requirements

Python 3.9+, standard library only. No `pip install` needed to run the
scanner. `pytest` is only required to run the test suite.

## Usage

Scan the included synthetic fixture app and print a findings table:

```sh
python3 -m scanner.cli scan sample_app/
```

The command exits non-zero if any high-confidence (≥ 0.6) finding is
present, so it's usable as a CI gate without any extra wiring.

Print findings as JSON instead of a table:

```sh
python3 -m scanner.cli scan sample_app/ --json
```

Generate the static HTML "dashboard" view and open it in a browser:

```sh
python3 -m scanner.cli scan sample_app/ --out report.html
open report.html
```

You can also point it at a `.ipa` file — it will be unzipped to a temp
directory and scanned in place:

```sh
python3 -m scanner.cli scan MyApp.ipa
```

## Proving the detections are real, not noise

Copy `sample_app/` somewhere, fix each flagged issue (de-stuff the app name,
replace `try!`/force-unwraps with safe unwrapping, declare the
`UserDefaults` reason in `PrivacyInfo.xcprivacy`, add the Bluetooth/HomeKit
usage-description strings, add report/block methods), and re-scan — the
finding count drops to zero. This is the actual proof that the rules detect
meaningful issues rather than firing unconditionally.

## Running the tests

```sh
python3 -m pytest tests/
```

Each rule module has one test asserting it stays silent on a clean snippet
and one asserting it fires correctly on a known-bad snippet, plus a smoke
test for the JSON/HTML report rendering.

## Layout

```
scanner/
├── cli.py                 # argparse entry point (`scan <path> [--out report.html] [--json]`)
├── models.py               # Finding + Project (parses Info.plist/entitlements/xcprivacy/source)
├── report.py                # findings -> JSON / static HTML
├── ruleset/guidelines.json  # static Apple guideline reference data
└── rules/                   # one module per rejection-trigger category
sample_app/                  # synthetic fixture iOS project used for the demo
tests/                        # pytest suite
```
