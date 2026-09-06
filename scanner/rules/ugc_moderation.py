"""Guideline 1.2 (User-Generated Content): chat/comment/upload features
detected without any visible moderation/report/block hooks anywhere in the
project."""

import re

from ..models import Finding

GUIDELINE = "1.2"

UGC_PATTERN = re.compile(r"\b(sendMessage|postComment|ChatViewController|uploadPhoto|Comment)\b")
MODERATION_PATTERN = re.compile(r"\b(report|block|moderate|moderation|flag)\b", re.IGNORECASE)


def check_moderation(source_files: dict):
    ugc_hit = None
    for path, text in source_files.items():
        match = UGC_PATTERN.search(text)
        if match:
            ugc_hit = (path, text, match)
            break
    if not ugc_hit:
        return []

    for text in source_files.values():
        if MODERATION_PATTERN.search(text):
            return []

    path, text, match = ugc_hit
    line_no = text.count("\n", 0, match.start()) + 1
    return [
        Finding(
            guideline=GUIDELINE,
            title="User-generated content feature without moderation hooks",
            confidence=0.55,
            evidence=f"{match.group(0)} found in {path}, but no report/block/"
            "moderation logic found anywhere in the project.",
            fix="Add a way for users to report or block abusive content/users, "
            "and a filter for objectionable material, per Guideline 1.2.",
            file=path,
            line=line_no,
        )
    ]


def run(project):
    return check_moderation(project.source_files)
