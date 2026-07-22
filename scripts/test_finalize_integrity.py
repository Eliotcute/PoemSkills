#!/usr/bin/env python3
"""Regression tests that finalization is bound to current spec and pixel QA."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CATEGORIES = (
    "semantic_specificity", "material_quality", "paper_tactility", "composition",
    "typography", "image_text_relationship", "negative_space", "series_rhythm",
    "mobile_readability", "provenance_restraint",
)


def run(spec: Path, finalize: bool = False) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(SCRIPT_DIR / "run_pipeline.py")]
    if finalize:
        args.append("--finalize")
    args.append(str(spec))
    return subprocess.run(args, text=True, capture_output=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="poemskills-finalize-") as raw_root:
        root = Path(raw_root)
        title = "把注意力还给\n重要的事"
        payload = {
            "card_role": "cover",
            "source_ref": "用户提供的注意力原文",
            "source_excerpt": "减少无关入口，可以把注意力重新还给真正重要的事情。",
            "card_claim": title,
            "canvas_preset": "xhs-portrait",
            "width": 1242,
            "height": 1660,
            "priority": "balanced",
            "render_mode": "final",
            "layout": "text-led-note",
            "cluster_zone": "middle-left",
            "paper": "pale-white-fiber",
            "accent": "blue",
            "title": title,
            "body": "从减少一个无关入口开始管理注意力",
            "assets": [],
            "output": "cover.png",
        }
        spec = root / "cover.json"
        spec.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        rendered = run(spec)

        review_path = root / "cover.png.visual-review.json"
        review = json.loads(review_path.read_text(encoding="utf-8"))
        review.update({
            "status": "approved",
            "scores": {category: 8.5 for category in CATEGORIES},
            "lowest_category": "composition",
            "revision_summary": "检查完整图片与手机预览，并确认封面字号、留白和图文关系。",
            "approved": True,
        })
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
        finalized = run(spec, finalize=True)

        payload["source_excerpt"] = "修改后的来源摘录仍然有效，但已不再对应原来的像素检查。"
        spec.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        stale_spec = run(spec, finalize=True)

        payload["source_excerpt"] = "减少无关入口，可以把注意力重新还给真正重要的事情。"
        spec.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        (root / "cover.png.qa.json").unlink()
        missing_qa = run(spec, finalize=True)

    valid = rendered.returncode == 0 and finalized.returncode == 0 and stale_spec.returncode != 0 and missing_qa.returncode != 0
    print(json.dumps({
        "valid": valid,
        "render_passed": rendered.returncode == 0,
        "finalize_passed": finalized.returncode == 0,
        "stale_spec_rejected": stale_spec.returncode != 0,
        "missing_qa_rejected": missing_qa.returncode != 0,
    }, ensure_ascii=False, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
