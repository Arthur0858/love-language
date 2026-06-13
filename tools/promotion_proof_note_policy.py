#!/usr/bin/env python3
from __future__ import annotations

import re


TRACEABLE_PROOF_TOKENS = (
    "screenshot",
    "截圖",
    "螢幕截圖",
    "screen recording",
    "recording",
    "錄影",
    "public url",
    "public link",
    "公開",
    "live url",
    "profile url",
    "post url",
    "platform url",
    "channel url",
    "video url",
    "email thread",
    "gmail thread",
    "message id",
    "mail id",
    "inbox",
    "email",
    "信件",
    "來信",
    "thread",
    "url:",
    "http://",
    "https://",
)
GENERIC_ONLY_PHRASES = {
    "manual profile link verified",
    "live profile link verified",
    "profile link manually verified",
    "manual post url verified",
    "post url and first metrics verified",
    "post url and starter metrics manually verified",
    "email request verified",
    "manual link verified",
    "verified",
}
DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def normalize_note(value: str) -> str:
    return " ".join(value.strip().lower().split())


def has_traceable_evidence(value: str) -> bool:
    normalized = normalize_note(value)
    if not normalized:
        return False
    if normalized in GENERIC_ONLY_PHRASES:
        return False
    return any(token in normalized for token in TRACEABLE_PROOF_TOKENS) or bool(DATE_RE.search(normalized))


def proof_note_issue(value: str, label: str = "proof_note") -> str:
    if has_traceable_evidence(value):
        return ""
    return (
        f"{label} must include traceable evidence such as a screenshot filename, "
        "public URL, platform URL, email thread, message id, or checked date"
    )
