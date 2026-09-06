"""Privacy manifest gaps: PrivacyInfo.xcprivacy presence, plus a check that
"required reason" APIs used in source are actually declared with a reason."""

import re

from ..models import Finding

GUIDELINE = "5.1.1"

# A small slice of Apple's "required reason" API categories -- enough to
# demonstrate the source-vs-manifest cross-check without cataloguing all of
# Apple's required-reason API list.
API_PATTERNS = {
    "UserDefaults": re.compile(r"\bUserDefaults\b"),
}
API_CATEGORY = {
    "UserDefaults": "NSPrivacyAccessedAPICategoryUserDefaults",
}


def check_manifest_presence(present: bool):
    if present:
        return None
    return Finding(
        guideline=GUIDELINE,
        title="Missing PrivacyInfo.xcprivacy",
        confidence=0.7,
        evidence="No PrivacyInfo.xcprivacy file found in the app bundle.",
        fix="Add a PrivacyInfo.xcprivacy file declaring data collection "
        "and any required-reason API usage.",
        file="PrivacyInfo.xcprivacy",
    )


def check_declared_reasons(source_files: dict, manifest: dict):
    declared_types = {
        entry.get("NSPrivacyAccessedAPIType")
        for entry in manifest.get("NSPrivacyAccessedAPITypes", [])
        if isinstance(entry, dict)
    }

    findings = []
    for api_name, pattern in API_PATTERNS.items():
        category = API_CATEGORY[api_name]
        if category in declared_types:
            continue
        for path, text in source_files.items():
            match = pattern.search(text)
            if not match:
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    guideline=GUIDELINE,
                    title=f"{api_name} used without a declared privacy-manifest reason",
                    confidence=0.6,
                    evidence=f"{api_name} is used in source but "
                    f"{category} is not declared in PrivacyInfo.xcprivacy.",
                    fix=f"Add an NSPrivacyAccessedAPITypes entry for {category} "
                    "with an approved reason code, or remove the API usage.",
                    file=path,
                    line=line_no,
                )
            )
            break  # one finding per undeclared API is enough signal
    return findings


def run(project):
    absence = check_manifest_presence(project.privacy_manifest_present)
    if absence:
        return [absence]
    return check_declared_reasons(project.source_files, project.privacy_manifest)
