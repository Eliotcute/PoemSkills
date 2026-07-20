#!/usr/bin/env python3
"""Regression tests for final-vs-draft asset requirements."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from PIL import Image

from validate_card_spec import validate


def base_spec() -> dict:
    return {
        "canvas_preset": "xhs-portrait",
        "width": 1242,
        "height": 1660,
        "priority": "balanced",
        "layout": "relief-emblem",
        "cluster_zone": "middle-left",
        "title": "浏览器代理开始执行网页任务",
        "body": "它会打开来源、采集信息、截图、提取内容，再把结果填写进表单。",
        "assets": [{
            "type": "relief-print",
            "subject": "机械手操作浏览器",
            "semantic_role": "explain",
            "semantic_reason": "机械手直接解释代理开始执行浏览器任务",
            "path": None,
        }],
        "output": "card.png",
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="whole-earth-asset-gate-") as raw_root:
        root = Path(raw_root)
        final_missing = base_spec()
        final_errors = validate(final_missing, root)

        draft = base_spec()
        draft["render_mode"] = "draft"
        draft_errors = validate(draft, root)

        supplied_path = root / "asset.png"
        Image.new("RGB", (80, 80), "white").save(supplied_path)
        supplied = base_spec()
        supplied["assets"][0]["path"] = str(supplied_path)
        supplied_errors = validate(supplied, root)

        color_block = base_spec()
        color_block["assets"][0].update({"type": "color-block", "path": None})
        color_errors = validate(color_block, root)

        valid = bool(final_errors) and not draft_errors and not supplied_errors and not color_errors
        print(json.dumps({
            "valid": valid,
            "final_missing_rejected": bool(final_errors),
            "draft_allowed": not draft_errors,
            "supplied_allowed": not supplied_errors,
            "color_block_allowed": not color_errors,
        }, ensure_ascii=False, indent=2))
        return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
