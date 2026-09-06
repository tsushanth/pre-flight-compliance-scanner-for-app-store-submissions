"""Data model for the scanner: a Finding (a single rejection-risk hit) and a
Project (parsed view of the on-disk app being scanned)."""

import json
import plistlib
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

SOURCE_SUFFIXES = (".swift", ".m", ".h")

GUIDELINES_PATH = Path(__file__).parent / "ruleset" / "guidelines.json"


@dataclass
class Finding:
    guideline: str
    title: str
    confidence: float  # 0.0 - 1.0
    evidence: str
    fix: str
    file: str = ""
    line: int = 0


@dataclass
class Project:
    root: Path
    info_plist: dict = field(default_factory=dict)
    entitlements: dict = field(default_factory=dict)
    privacy_manifest_present: bool = False
    privacy_manifest: dict = field(default_factory=dict)
    source_files: dict = field(default_factory=dict)  # relative path -> text

    @classmethod
    def load(cls, path):
        """Load a Project from a directory, or from a .ipa file (unzipped
        in a temp dir and pointed at the first Payload/*.app bundle)."""
        p = Path(path)

        if p.is_file() and p.suffix == ".ipa":
            tmp_dir = Path(tempfile.mkdtemp(prefix="scanner_ipa_"))
            with zipfile.ZipFile(p) as zf:
                zf.extractall(tmp_dir)
            app_dirs = sorted((tmp_dir / "Payload").glob("*.app")) if (tmp_dir / "Payload").exists() else []
            if not app_dirs:
                raise ValueError(f"No .app bundle found inside {path}")
            root = app_dirs[0]
        else:
            root = p

        info_plist = _load_plist(root / "Info.plist")
        entitlements = _load_plist(root / "entitlements.plist")

        privacy_path = root / "PrivacyInfo.xcprivacy"
        privacy_present = privacy_path.exists()
        privacy_manifest = _load_plist(privacy_path) if privacy_present else {}

        source_files = {}
        src_dir = root / "Sources"
        if src_dir.exists():
            for source_path in sorted(src_dir.rglob("*")):
                if source_path.is_file() and source_path.suffix in SOURCE_SUFFIXES:
                    rel = str(source_path.relative_to(root))
                    source_files[rel] = source_path.read_text(encoding="utf-8", errors="replace")

        return cls(
            root=root,
            info_plist=info_plist,
            entitlements=entitlements,
            privacy_manifest_present=privacy_present,
            privacy_manifest=privacy_manifest,
            source_files=source_files,
        )


def _load_plist(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return plistlib.load(f)


def load_guidelines() -> dict:
    """Static reference data: guideline id -> {title, text, rejection_rate}."""
    with open(GUIDELINES_PATH, encoding="utf-8") as f:
        return json.load(f)
