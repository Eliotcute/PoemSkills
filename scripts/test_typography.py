#!/usr/bin/env python3
"""Regression tests for mixed Chinese/Latin wrapping and annotation routing."""

from __future__ import annotations

import json

from PIL import Image, ImageDraw

from render_card import CLOSING_PUNCTUATION, contains_cjk, load_font, wrap_chars


def main() -> int:
    image = Image.new("RGB", (900, 300), "white")
    draw = ImageDraw.Draw(image)
    font = load_font(42, "serif")
    lines = wrap_chars(draw, "让 WorkBuddy 动手操作浏览器，安装 agent-browser 后开始采集。", font, 330)
    latin_intact = any("WorkBuddy" in line for line in lines) and any("agent-browser" in line for line in lines)
    punctuation_valid = all(not line or line[0] not in CLOSING_PUNCTUATION for line in lines)
    width_valid = all(draw.textlength(line, font=font) <= 330 for line in lines)
    cjk_detected = contains_cjk("浏览器执行层") and not contains_cjk("TOOL NOTE")
    valid = latin_intact and punctuation_valid and width_valid and cjk_detected
    print(json.dumps({"valid": valid, "lines": lines, "punctuation_valid": punctuation_valid, "width_valid": width_valid, "cjk_detected": cjk_detected}, ensure_ascii=False, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
