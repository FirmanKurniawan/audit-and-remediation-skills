"""Cache-key helper.

Uses a non-cryptographic-strength digest deliberately and only for cache
bucketing, never for authentication or integrity.
"""
from __future__ import annotations

import hashlib


def cache_key(*parts: str) -> str:
    joined = "\u241f".join(parts)
    return hashlib.blake2b(joined.encode("utf-8"), digest_size=16).hexdigest()
