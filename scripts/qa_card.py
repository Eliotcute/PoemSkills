#!/usr/bin/env python3
"""Pixel and layout QA for a rendered poetic-archive card."""

from __future__ import annotations

import json
import math
import sys
import unicodedata
from pathlib import Path

from PIL import Image


def intersect(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def contrast_ratio(rgb_a, rgb_b):
    def luminance(rgb):
        values = []
        for channel in rgb:
            value = channel / 255
            values.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]
    light, dark = sorted((luminance(rgb_a), luminance(rgb_b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: qa_card.py card.json card.png", file=sys.stderr)
        return 2
    spec_path, image_path = Path(sys.argv[1]), Path(sys.argv[2])
    cfg = json.loads(spec_path.read_text(encoding="utf-8"))
    im = Image.open(image_path).convert("RGB")
    meta_path = image_path.with_suffix(image_path.suffix + ".layout.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    errors, warnings = [], []
    if im.size != (int(cfg["width"]), int(cfg["height"])):
        errors.append(f"wrong dimensions: {im.size}, expected {(cfg['width'], cfg['height'])}")
    if meta.get("asset_count", 0) > 2:
        errors.append("more than two assets")
    for field in ("title", "body"):
        value = str(cfg.get(field, ""))
        if "\ufffd" in value or any(unicodedata.category(char) == "Cc" and char not in "\n\t" for char in value):
            errors.append(f"{field} contains replacement or control characters")
    safe = tuple(meta["safe_area"])
    for group in ("title_boxes", "body_boxes"):
        for box in meta.get(group, []):
            if box[0] < safe[0] or box[1] < safe[1] or box[2] > safe[2] or box[3] > safe[3]:
                errors.append(f"essential text outside safe area: {box}")
    essential = meta.get("title_boxes", []) + meta.get("body_boxes", [])
    for i, a in enumerate(essential):
        for b in essential[i + 1:]:
            if intersect(a, b) > 0:
                errors.append(f"essential text overlap: {a} / {b}")
    for text_box in essential:
        for asset_box in meta.get("asset_boxes", []):
            overlap = intersect(text_box, asset_box)
            if overlap / max(1, area(text_box)) > 0.04:
                errors.append(f"essential text materially collides with asset: {text_box} / {asset_box}")
    accent = tuple(meta.get("accent_rgb", [61, 98, 112]))
    pixels = list(im.getdata())
    accent_pixels = sum(1 for p in pixels if math.dist(p, accent) < 22)
    accent_ratio = accent_pixels / max(1, len(pixels))
    if accent_ratio > 0.055:
        errors.append(f"accent coverage too high: {accent_ratio:.2%}")
    bright_ratio = sum(1 for p in pixels if min(p) >= 238) / max(1, len(pixels))
    if bright_ratio < 0.63:
        errors.append(f"insufficient quiet pale paper area: {bright_ratio:.2%}")
    short = min(im.size)
    minimum_title = max(28, int(short * 0.038))
    minimum_body = max(22, int(short * 0.027))
    if meta["font_sizes"]["title"] < minimum_title:
        errors.append(f"title font too small: {meta['font_sizes']['title']} < {minimum_title}")
    if meta["font_sizes"]["body"] < minimum_body:
        errors.append(f"body font too small: {meta['font_sizes']['body']} < {minimum_body}")
    paper_rgb = tuple(im.getpixel((0, 0)))
    essential_contrast = contrast_ratio((17, 17, 15), paper_rgb)
    if essential_contrast < 4.5:
        errors.append(f"essential text contrast too low: {essential_contrast:.2f}:1")
    if cfg.get("canvas_preset") == "portrait-9x16":
        ui_top = int(im.height * 0.10)
        ui_bottom = int(im.height * 0.88)
        for box in essential:
            if box[1] < ui_top or box[3] > ui_bottom:
                errors.append(f"essential text enters 9:16 interface exclusion zone: {box}")
    if cfg.get("canvas_preset") == "xhs-portrait":
        preview_width, preview_height = 375, 500
    else:
        preview_width = 375 if im.width <= im.height else 640
        preview_height = round(im.height * preview_width / im.width)
    preview = im.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
    preview_path = image_path.with_name(image_path.stem + "-preview" + image_path.suffix)
    preview.save(preview_path, quality=94)
    result = {"valid": not errors, "errors": errors, "warnings": warnings, "metrics": {"accent_ratio": accent_ratio, "bright_ratio": bright_ratio, "essential_contrast": essential_contrast}, "preview": str(preview_path)}
    report_path = image_path.with_suffix(image_path.suffix + ".qa.json")
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
