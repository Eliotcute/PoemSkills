#!/usr/bin/env python3
"""Regression tests for declared image-text intersections."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent


def write_case(root: Path, name: str, asset_path: Path, mode: str, limit: float) -> tuple[Path, Path]:
    image_path = root / f"{name}.png"
    Image.new("RGB", (400, 400), "#FAFAF7").save(image_path)
    spec = {
        "canvas_preset": "custom",
        "width": 400,
        "height": 400,
        "priority": "balanced",
        "layout": "quiet-specimen",
        "cluster_zone": "center",
        "title": "受控相交必须保持正文清楚",
        "body": "文字可以进入素材布局区域，但不能压住大面积不透明图像内容。",
        "assets": [{
            "type": "relief-print",
            "subject": "测试用透明素材",
            "semantic_role": "explain",
            "semantic_reason": "测试透明区域与不透明区域的碰撞差异",
            "path": str(asset_path),
        }],
        "intentional_intersection": {
            "mode": mode,
            "reason": "让文字穿过素材透明区域以形成受控图文关系",
            "asset_indices": [0],
            "max_opaque_overlap": limit,
        },
        "output": str(image_path),
    }
    spec_path = root / f"{name}.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    meta = {
        "canvas": {"width": 400, "height": 400, "preset": "custom"},
        "safe_area": [20, 20, 380, 380],
        "priority": "balanced",
        "layout": "quiet-specimen",
        "cluster_zone": "center",
        "asset_count": 1,
        "accent": "blue",
        "accent_rgb": [61, 98, 112],
        "font_sizes": {"title": 32, "body": 24, "micro": 15},
        "title_boxes": [[120, 120, 260, 155]],
        "body_boxes": [[120, 170, 280, 200]],
        "micro_boxes": [],
        "asset_boxes": [[80, 80, 320, 240]],
        "asset_opaque_boxes": [[240, 80, 320, 240]],
        "asset_alpha_paths": [str(asset_path)],
        "output": str(image_path),
    }
    image_path.with_suffix(image_path.suffix + ".layout.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return spec_path, image_path


def main() -> int:
    python = sys.executable
    with tempfile.TemporaryDirectory(prefix="whole-earth-intersection-") as raw_root:
        root = Path(raw_root)
        asset_path = root / "transparent-asset.png"
        asset = Image.new("RGBA", (240, 160), (0, 0, 0, 0))
        draw = ImageDraw.Draw(asset)
        draw.rectangle((160, 0, 239, 159), fill=(17, 17, 15, 255))
        asset.save(asset_path)

        transparent_spec, transparent_image = write_case(
            root, "transparent-pass", asset_path, "transparent-only", 0.0
        )
        validator = subprocess.run(
            [python, str(SCRIPT_DIR / "validate_card_spec.py"), str(transparent_spec)],
            text=True, capture_output=True,
        )
        transparent_result = subprocess.run(
            [python, str(SCRIPT_DIR / "qa_card.py"), str(transparent_spec), str(transparent_image)],
            text=True, capture_output=True,
        )

        opaque_spec, opaque_image = write_case(
            root, "opaque-reject", asset_path, "controlled-overlap", 0.03
        )
        opaque_meta_path = opaque_image.with_suffix(opaque_image.suffix + ".layout.json")
        opaque_meta = json.loads(opaque_meta_path.read_text(encoding="utf-8"))
        opaque_meta["asset_opaque_boxes"] = [[120, 80, 320, 240]]
        opaque_asset_path = root / "opaque-asset.png"
        Image.new("L", (240, 160), 255).save(opaque_asset_path)
        opaque_meta["asset_alpha_paths"] = [str(opaque_asset_path)]
        opaque_meta_path.write_text(json.dumps(opaque_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        opaque_result = subprocess.run(
            [python, str(SCRIPT_DIR / "qa_card.py"), str(opaque_spec), str(opaque_image)],
            text=True, capture_output=True,
        )

        valid = validator.returncode == 0 and transparent_result.returncode == 0 and opaque_result.returncode != 0
        report = {
            "valid": valid,
            "contract_validated": validator.returncode == 0,
            "transparent_region_passed": transparent_result.returncode == 0,
            "opaque_region_rejected": opaque_result.returncode != 0,
            "transparent_output": transparent_result.stdout[-1200:],
            "opaque_output": opaque_result.stdout[-1200:],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
