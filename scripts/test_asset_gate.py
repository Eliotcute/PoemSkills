#!/usr/bin/env python3
"""Regression tests for final-vs-draft asset requirements."""

from __future__ import annotations

import json
import hashlib
import tempfile
from pathlib import Path

from PIL import Image

from validate_card_spec import validate
from render_card import programmatic_asset


def base_spec() -> dict:
    return {
        "card_role": "interior",
        "source_ref": "浏览器代理测试原文",
        "source_excerpt": "代理会打开来源、采集信息、截图并把结果填写到表单。",
        "card_claim": "浏览器代理开始执行网页任务",
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
    with tempfile.TemporaryDirectory(prefix="poemskills-asset-gate-") as raw_root:
        root = Path(raw_root)
        final_missing = base_spec()
        final_errors = validate(final_missing, root, allow_legacy=True)

        draft = base_spec()
        draft["render_mode"] = "draft"
        draft_errors = validate(draft, root, allow_legacy=True)

        supplied_path = root / "asset.png"
        Image.new("RGB", (80, 80), "white").save(supplied_path)
        supplied = base_spec()
        supplied["assets"][0]["path"] = str(supplied_path)
        supplied_errors = validate(supplied, root, allow_legacy=True)

        motif_errors = {}
        motif_digests = {}
        for motif in ("solid", "sequence", "boundary", "index"):
            color_block = base_spec()
            color_block["assets"][0].update({"type": "color-block", "path": None, "motif": motif})
            motif_errors[motif] = validate(color_block, root, allow_legacy=True)
            rendered = programmatic_asset(color_block["assets"][0], (240, 180), (61, 98, 112), 17)
            motif_digests[motif] = hashlib.sha256(rendered.tobytes()).hexdigest()

        misspelled = base_spec()
        misspelled["assets"][0].update({"type": "color-block", "path": None, "motif": "sequnce"})
        misspelled_errors = validate(misspelled, root, allow_legacy=True)

        motifs_valid = all(not errors for errors in motif_errors.values()) and len(set(motif_digests.values())) == 4
        valid = bool(final_errors) and not draft_errors and not supplied_errors and motifs_valid and bool(misspelled_errors)
        print(json.dumps({
            "valid": valid,
            "final_missing_rejected": bool(final_errors),
            "draft_allowed": not draft_errors,
            "supplied_allowed": not supplied_errors,
            "color_block_motifs_valid": motifs_valid,
            "color_block_outputs_distinct": len(set(motif_digests.values())) == 4,
            "misspelled_motif_rejected": bool(misspelled_errors),
        }, ensure_ascii=False, indent=2))
        return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
