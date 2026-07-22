#!/usr/bin/env python3
"""Regression tests for the mandatory visual-review delivery gate."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from validate_visual_review import CATEGORIES, validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review(score: float, image: Path, preview: Path, approved: bool = True) -> dict:
    return {
        "status": "approved" if approved else "pending",
        "image": str(image),
        "preview": str(preview),
        "image_sha256": digest(image),
        "preview_sha256": digest(preview),
        "scores": {category: score for category in CATEGORIES},
        "lowest_category": "composition",
        "revision_summary": "检查完整图片和手机预览，并修正最弱的构图关系。",
        "approved": approved,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="whole-earth-visual-review-") as raw_root:
        root = Path(raw_root)
        image, preview = root / "card.png", root / "card-preview.png"
        image.write_bytes(b"image")
        preview.write_bytes(b"preview")
        passing = review(8.5, image, preview)
        low_category = review(8.5, image, preview)
        low_category["scores"]["material_quality"] = 7
        low_total = review(8, image, preview)
        pending = review(9, image, preview, approved=False)
        pending_but_approved = review(9, image, preview)
        pending_but_approved["status"] = "pending"
        wrong_lowest = review(8.5, image, preview)
        wrong_lowest["scores"]["material_quality"] = 8
        stale = review(9, image, preview)
        image.write_bytes(b"changed")
        stale_errors = validate(stale)
        image.write_bytes(b"image")

        valid = (
            not validate(passing)
            and bool(validate(low_category))
            and bool(validate(low_total))
            and bool(validate(pending))
            and bool(validate(pending_but_approved))
            and bool(validate(wrong_lowest))
            and bool(stale_errors)
        )
        print(json.dumps({
            "valid": valid,
            "passing_review": not validate(passing),
            "low_category_rejected": bool(validate(low_category)),
            "low_total_rejected": bool(validate(low_total)),
            "pending_rejected": bool(validate(pending)),
            "pending_status_rejected": bool(validate(pending_but_approved)),
            "wrong_lowest_rejected": bool(validate(wrong_lowest)),
            "stale_review_rejected": bool(stale_errors),
        }, ensure_ascii=False, indent=2))
        return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
