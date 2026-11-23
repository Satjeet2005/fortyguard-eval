"""Redact secrets from logs/results before they are committed.

Usage: python redact.py <file-or-dir> [...]   (rewrites files in place)
Scrubs: signed S3 URLs, AWS key IDs / signatures, account ids, hex strings
that look like API keys or signatures, and subscription ids.
"""
import re, sys, pathlib

RULES = [
    (re.compile(r'https?://[^\s"\\]*(?:X-Amz-|amazonaws\.com)[^\s"\\]*'), "<REDACTED_SIGNED_URL>"),
    (re.compile(r'AKIA[0-9A-Z]{16}'), "<REDACTED_AWS_KEY_ID>"),
    (re.compile(r'acc(?:%23|#)[A-Za-z0-9]+'), "acc#<REDACTED>"),
    (re.compile(r'sub_[a-z0-9]{6,}'), "sub_<REDACTED>"),
    (re.compile(r'(?<![0-9a-fA-F])[0-9a-f]{32,64}(?![0-9a-fA-F])'), "<REDACTED_HEX>"),
]

def redact(text: str) -> str:
    for rx, rep in RULES:
        text = rx.sub(rep, text)
    return text

def main(paths):
    for p in map(pathlib.Path, paths):
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
        for f in files:
            if f.suffix not in {".json", ".jsonl", ".txt", ".md", ".log"}:
                continue
            old = f.read_text()
            new = redact(old)
            if new != old:
                f.write_text(new)
                print("redacted", f)

if __name__ == "__main__":
    main(sys.argv[1:] or ["evidence"])
