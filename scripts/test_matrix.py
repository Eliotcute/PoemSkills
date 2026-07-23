#!/usr/bin/env python3
"""Exercise every canvas preset against every layout in an isolated directory."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

from validate_card_spec import CANVAS_PRESETS, LAYOUTS


SCRIPT_DIR = Path(__file__).resolve().parent
ZONES = [
    "upper-left", "upper-right", "middle-left", "middle-right", "lower-left",
    "lower-right", "upper-center", "lower-center", "center",
]


def main() -> int:
    python = sys.executable
    cases: list[dict[str, object]] = []
    keep_dir = os.environ.get("WHOLE_EARTH_MATRIX_DIR")
    context = None if keep_dir else tempfile.TemporaryDirectory(prefix="poemskills-card-matrix-")
    raw_dir = keep_dir or context.name
    try:
        root = Path(raw_dir)
        root.mkdir(parents=True, exist_ok=True)
        for preset_index, (preset, dimensions) in enumerate(CANVAS_PRESETS.items()):
            if preset == "custom":
                dimensions = (1376, 768)
            assert dimensions is not None
            width, height = dimensions
            for layout_index, layout in enumerate(sorted(LAYOUTS)):
                case_id = f"{preset}--{layout}"
                if min(width, height) <= 600:
                    title = "把问题缩小到今天能够开始"
                    body = "保留一个入口，再完成一个看得见的动作。"
                else:
                    title = "把复杂问题缩小到今天能够开始"
                    body = "先保留一个清楚入口，再完成一个可以看见的动作。稳定往往来自更少选择，以及能够重复的小结构。"
                spec = {
                    "card_role": "interior",
                    "source_ref": "画布矩阵测试原文",
                    "source_excerpt": "减少选择并保留一个入口，会让具体行动更容易开始。",
                    "card_claim": title,
                    "series_id": "matrix",
                    "variant_id": case_id,
                    "card_number": 1,
                    "canvas_preset": preset,
                    "width": width,
                    "height": height,
                    "priority": "balanced",
                    "render_mode": "draft",
                    "layout": layout,
                    "cluster_zone": ZONES[(preset_index + layout_index) % len(ZONES)],
                    "paper": "pale-white-fiber",
                    "accent": "blue",
                    "title": title,
                    "body": body,
                    "assets": [{
                        "type": "silhouette" if layout == "silhouette-field" else "relief-print",
                        "subject": "从复杂枝叶中被清理出来的一条路径",
                        "semantic_role": "explain",
                        "semantic_reason": "用清晰路径解释减少选择后更容易开始具体行动",
                        "path": None,
                    }],
                    "annotations": ["FIELD NOTE / BEGIN", "remove · choose · act"],
                    "output": f"{case_id}.png",
                }
                spec_path = root / f"{case_id}.json"
                spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
                result = subprocess.run(
                    [python, str(SCRIPT_DIR / "run_pipeline.py"), "--legacy-v0.6", str(spec_path)],
                    text=True,
                    capture_output=True,
                )
                cases.append({
                    "case": case_id,
                    "valid": result.returncode == 0,
                    "stdout": result.stdout[-1600:],
                    "stderr": result.stderr[-1600:],
                })
    finally:
        if context is not None:
            context.cleanup()

    failures = [case for case in cases if not case["valid"]]
    print(json.dumps({"valid": not failures, "case_count": len(cases), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
