"""Registers all rule checks for the CLI to run.

Each rule module exposes a `run(project) -> list[Finding]` function.
"""

from . import guideline_2_1
from . import guideline_4_3
from . import iot_device
from . import privacy_manifest
from . import ugc_moderation

RULES = [
    guideline_4_3,
    guideline_2_1,
    privacy_manifest,
    iot_device,
    ugc_moderation,
]
