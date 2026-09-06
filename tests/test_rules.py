"""For each rule module: one clean-fixture case (silent) and one
violation-fixture case (fires with the expected guideline id and a
confidence score in [0, 1])."""

from scanner.rules import guideline_2_1, guideline_4_3, iot_device, privacy_manifest, ugc_moderation


def assert_valid_finding(finding, expected_guideline):
    assert finding.guideline == expected_guideline
    assert 0.0 <= finding.confidence <= 1.0


# -- guideline_4_3: keyword stuffing -----------------------------------------


def test_guideline_4_3_clean():
    assert guideline_4_3.check_name_keyword_stuffing("Simple Todo List") is None
    assert guideline_4_3.check_name_keyword_stuffing("") is None


def test_guideline_4_3_violation():
    finding = guideline_4_3.check_name_keyword_stuffing(
        "SuperApp - Photo, Camera, Filters, Editor, Collage"
    )
    assert finding is not None
    assert_valid_finding(finding, "4.3")


# -- guideline_2_1: crash-prone patterns -------------------------------------


def test_guideline_2_1_clean():
    text = "let x = 5\nif let y = optionalValue {\n    print(y)\n}\n"
    assert guideline_2_1.scan_source("Clean.swift", text) == []


def test_guideline_2_1_violation():
    text = (
        "let url = URL(string: raw)!\n"
        "let data = try! JSONDecoder().decode(Foo.self, from: raw)\n"
    )
    findings = guideline_2_1.scan_source("Bad.swift", text)
    assert len(findings) == 2
    for finding in findings:
        assert_valid_finding(finding, "2.1")


def test_guideline_2_1_ignores_iuo_declaration():
    text = "private var centralManager: CBCentralManager!\n"
    assert guideline_2_1.scan_source("Decl.swift", text) == []


# -- privacy_manifest ---------------------------------------------------------


def test_privacy_manifest_presence_clean():
    assert privacy_manifest.check_manifest_presence(True) is None


def test_privacy_manifest_presence_violation():
    finding = privacy_manifest.check_manifest_presence(False)
    assert finding is not None
    assert_valid_finding(finding, "5.1.1")


def test_privacy_manifest_declared_reasons_clean():
    source_files = {"Foo.swift": "UserDefaults.standard.set(1, forKey: \"x\")"}
    manifest = {
        "NSPrivacyAccessedAPITypes": [
            {"NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryUserDefaults"}
        ]
    }
    assert privacy_manifest.check_declared_reasons(source_files, manifest) == []


def test_privacy_manifest_declared_reasons_violation():
    source_files = {"Foo.swift": "UserDefaults.standard.set(1, forKey: \"x\")"}
    manifest = {"NSPrivacyAccessedAPITypes": []}
    findings = privacy_manifest.check_declared_reasons(source_files, manifest)
    assert len(findings) == 1
    assert_valid_finding(findings[0], "5.1.1")


# -- iot_device ---------------------------------------------------------------


def test_iot_device_bluetooth_clean():
    source_files = {"Foo.swift": "import CoreBluetooth\nlet x = CBCentralManager()"}
    info_plist = {"NSBluetoothAlwaysUsageDescription": "We use Bluetooth to pair."}
    assert iot_device.check_bluetooth_usage(source_files, info_plist) is None


def test_iot_device_bluetooth_violation():
    source_files = {"Foo.swift": "import CoreBluetooth\nlet x = CBCentralManager()"}
    finding = iot_device.check_bluetooth_usage(source_files, {})
    assert finding is not None
    assert_valid_finding(finding, "2.5.6")


def test_iot_device_homekit_clean():
    entitlements = {"com.apple.developer.homekit": True}
    info_plist = {"NSHomeKitUsageDescription": "We use HomeKit to control accessories."}
    assert iot_device.check_homekit_entitlement(entitlements, info_plist) is None


def test_iot_device_homekit_violation():
    entitlements = {"com.apple.developer.homekit": True}
    finding = iot_device.check_homekit_entitlement(entitlements, {})
    assert finding is not None
    assert_valid_finding(finding, "2.5.6")


# -- ugc_moderation -------------------------------------------------------------


def test_ugc_moderation_clean():
    source_files = {
        "Chat.swift": "func sendMessage(_ text: String) {}",
        "Moderation.swift": "func report(user id: String) {}",
    }
    assert ugc_moderation.check_moderation(source_files) == []


def test_ugc_moderation_violation():
    source_files = {"Chat.swift": "func sendMessage(_ text: String) {}"}
    findings = ugc_moderation.check_moderation(source_files)
    assert len(findings) == 1
    assert_valid_finding(findings[0], "1.2")
