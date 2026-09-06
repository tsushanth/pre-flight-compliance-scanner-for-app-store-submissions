"""IoT/accessory heuristics: Bluetooth or HomeKit usage without the
matching Info.plist usage-description string."""

import re

from ..models import Finding

GUIDELINE = "2.5.6"

BLUETOOTH_PATTERN = re.compile(r"\bCoreBluetooth\b|\bCBCentralManager\b|\bCBPeripheralManager\b")
BLUETOOTH_USAGE_KEYS = ("NSBluetoothAlwaysUsageDescription", "NSBluetoothPeripheralUsageDescription")

HOMEKIT_ENTITLEMENT_PREFIX = "com.apple.developer.homekit"
HOMEKIT_USAGE_KEY = "NSHomeKitUsageDescription"


def check_bluetooth_usage(source_files: dict, info_plist: dict):
    if any(key in info_plist for key in BLUETOOTH_USAGE_KEYS):
        return None
    for path, text in source_files.items():
        match = BLUETOOTH_PATTERN.search(text)
        if match:
            line_no = text.count("\n", 0, match.start()) + 1
            return Finding(
                guideline=GUIDELINE,
                title="Bluetooth API used without a usage-description string",
                confidence=0.6,
                evidence=f"{match.group(0)} used in {path} but no "
                "NSBluetoothAlwaysUsageDescription/NSBluetoothPeripheralUsageDescription in Info.plist.",
                fix="Add NSBluetoothAlwaysUsageDescription (or "
                "NSBluetoothPeripheralUsageDescription) to Info.plist explaining the Bluetooth use.",
                file=path,
                line=line_no,
            )
    return None


def check_homekit_entitlement(entitlements: dict, info_plist: dict):
    has_homekit_entitlement = any(
        key.startswith(HOMEKIT_ENTITLEMENT_PREFIX) and value
        for key, value in entitlements.items()
    )
    if not has_homekit_entitlement or HOMEKIT_USAGE_KEY in info_plist:
        return None
    return Finding(
        guideline=GUIDELINE,
        title="HomeKit entitlement present without a usage-description string",
        confidence=0.6,
        evidence=f"{HOMEKIT_ENTITLEMENT_PREFIX} entitlement is set but "
        f"{HOMEKIT_USAGE_KEY} is missing from Info.plist.",
        fix=f"Add {HOMEKIT_USAGE_KEY} to Info.plist explaining why the app needs HomeKit access.",
        file="entitlements.plist",
    )


def run(project):
    findings = []
    bluetooth_finding = check_bluetooth_usage(project.source_files, project.info_plist)
    if bluetooth_finding:
        findings.append(bluetooth_finding)
    homekit_finding = check_homekit_entitlement(project.entitlements, project.info_plist)
    if homekit_finding:
        findings.append(homekit_finding)
    return findings
