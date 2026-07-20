#!/usr/bin/env python3
"""Render one publish-ready poetic-archive card from a validated JSON spec."""

from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from validate_card_spec import validate


PAPER = (250, 250, 247)
FIBER = (226, 225, 218)
INK = (17, 17, 15)
MUTED = (86, 86, 80)
ACCENTS = {
    "none": INK,
    "black": INK,
    "blue": (61, 98, 112),
    "brick": (138, 59, 43),
    "red": (174, 75, 62),
    "olive": (102, 112, 68),
    "violet": (101, 86, 120),
}
SERIF_FONTS = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]
SANS_FONTS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]
MONO_FONTS = [
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
]
CLOSING_PUNCTUATION = set("，。！？；：、）》】」』’”」％%!?;:,.])}")


def load_font(size: int, family: str = "serif") -> ImageFont.FreeTypeFont:
    choices = SERIF_FONTS if family == "serif" else SANS_FONTS if family == "sans" else MONO_FONTS
    for candidate in choices:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=max(8, int(size)), index=0)
    return ImageFont.load_default(size=max(8, int(size)))


def text_units(paragraph: str) -> list[str]:
    """Keep Latin identifiers intact while allowing natural CJK character wrapping."""
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9_.:/+@-]*|[ \t]+|.", paragraph)


def split_oversized_unit(draw: ImageDraw.ImageDraw, unit: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    fragments, current = [], ""
    for char in unit:
        trial = current + char
        if current and draw.textlength(trial, font=face) > max_width:
            fragments.append(current)
            current = char
        else:
            current = trial
    if current:
        fragments.append(current)
    return fragments


def wrap_chars(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for unit in text_units(paragraph):
            trial = current + unit
            if current and draw.textlength(trial, font=face) > max_width:
                if unit in CLOSING_PUNCTUATION:
                    current = trial
                    continue
                lines.append(current.rstrip())
                current = unit.lstrip()
            else:
                current = trial
            if current and draw.textlength(current, font=face) > max_width:
                fragments = split_oversized_unit(draw, current, face, max_width)
                lines.extend(fragment.rstrip() for fragment in fragments[:-1])
                current = fragments[-1]
        if current:
            lines.append(current.rstrip())
    return lines


def contains_cjk(value: str) -> bool:
    return any("\u3400" <= char <= "\u9fff" for char in str(value))


def draw_text_block(draw, xy, text, face, fill, max_width, line_gap, max_lines=None):
    x, y = xy
    lines = wrap_chars(draw, text, face, max_width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"Text overflow: {len(lines)} lines exceeds {max_lines}")
    bbox = draw.textbbox((0, 0), "国Ag", font=face)
    line_h = bbox[3] - bbox[1] + line_gap
    boxes = []
    for line in lines:
        if line:
            box = draw.textbbox((x, y), line, font=face)
            draw.text((x, y), line, font=face, fill=fill)
            boxes.append(tuple(map(int, box)))
        y += line_h
    return y, boxes


def make_paper(width: int, height: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (width, height), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    area_scale = max(1, width * height // 50000)
    for _ in range(area_scale * 26):
        x = rng.randrange(width)
        y = rng.randrange(height)
        length = rng.randint(max(3, width // 250), max(8, width // 55))
        alpha = rng.randint(4, 11)
        if rng.random() < 0.65:
            d.line((x, y, min(width, x + length), y + rng.choice([-1, 0, 1])), fill=(*FIBER, alpha), width=1)
        else:
            d.line((x, y, x + rng.choice([-1, 0, 1]), min(height, y + length)), fill=(*FIBER, alpha), width=1)
    noise = Image.effect_noise((width, height), 3.0).convert("L")
    noise = ImageEnhance.Contrast(noise).enhance(0.22)
    veil = Image.new("RGB", (width, height), PAPER)
    veil.putalpha(noise.point(lambda value: max(0, min(10, int(value * 0.035)))))
    img = Image.alpha_composite(img.convert("RGBA"), veil).convert("RGB")
    return img


def asset_path(asset: dict, spec_path: Path) -> Path | None:
    raw = asset.get("path")
    if not raw:
        return None
    path = Path(raw)
    return path if path.is_absolute() else (spec_path.parent / path).resolve()


def process_photo(path: Path, size: tuple[int, int], paper: tuple[int, int, int]) -> Image.Image:
    im = Image.open(path).convert("RGB")
    im = ImageOps.fit(im, size, method=Image.Resampling.LANCZOS)
    im = ImageOps.grayscale(im)
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageOps.colorize(im, black=(28, 28, 26), white=paper)
    return im


def process_cutout(path: Path, size: tuple[int, int], color=INK) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    if im.getextrema()[3] == (255, 255):
        gray = ImageOps.grayscale(im.convert("RGB"))
        gray = ImageOps.autocontrast(gray, cutoff=1)
        alpha = ImageEnhance.Contrast(ImageOps.invert(gray)).enhance(1.22)
        alpha = alpha.point(lambda value: 0 if value < 12 else value)
        content_box = alpha.getbbox()
        if content_box:
            alpha = alpha.crop(content_box)
        colored = Image.new("RGBA", im.size, (*color, 255))
        if content_box:
            colored = colored.crop(content_box)
        colored.putalpha(alpha)
        im = colored
    im.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - im.width) // 2
    y = (size[1] - im.height) // 2
    canvas.alpha_composite(im, (x, y))
    return canvas


def programmatic_asset(asset: dict, size: tuple[int, int], accent, seed: int) -> Image.Image:
    kind = asset.get("type", "relief-print")
    rng = random.Random(seed)
    w, h = size
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    if kind == "color-block":
        d.rectangle((w * 0.12, h * 0.14, w * 0.86, h * 0.82), fill=(*accent, 205))
    elif kind == "silhouette":
        points = [(w * 0.08, h * 0.72), (w * 0.28, h * 0.43), (w * 0.46, h * 0.57), (w * 0.68, h * 0.22), (w * 0.92, h * 0.66)]
        d.line(points, fill=(*INK, 255), width=max(3, w // 35), joint="curve")
        for x, y in points:
            d.ellipse((x - w * 0.035, y - w * 0.035, x + w * 0.035, y + w * 0.035), fill=(*INK, 255))
    elif kind in {"ticket", "document"}:
        d.rounded_rectangle((w * 0.06, h * 0.1, w * 0.94, h * 0.88), radius=max(2, w // 60), fill=(243, 243, 238, 255), outline=(*INK, 150), width=max(1, w // 180))
        for row in range(5):
            yy = h * (0.25 + row * 0.105)
            d.line((w * 0.16, yy, w * (0.82 - row * 0.05), yy), fill=(*MUTED, 120), width=max(1, w // 220))
    else:
        stem_x = w * 0.48
        d.line((stem_x, h * 0.88, stem_x, h * 0.24), fill=(*INK, 255), width=max(4, w // 35))
        for index in range(7):
            yy = h * (0.75 - index * 0.075)
            side = -1 if index % 2 == 0 else 1
            cx = stem_x + side * w * (0.12 + rng.random() * 0.04)
            cy = yy
            rx, ry = w * 0.16, h * 0.07
            leaf = [(stem_x, yy), (cx - rx * 0.55, cy - ry * 0.25), (cx, cy - ry), (cx + rx * 0.62, cy), (cx, cy + ry), (cx - rx * 0.55, cy + ry * 0.2)]
            d.polygon(leaf, fill=(*INK, 255))
            for cut in range(3):
                offset = (cut - 1) * ry * 0.32
                d.line((stem_x, yy, cx + side * rx * 0.28, cy + offset), fill=(250, 250, 247, 230), width=max(1, w // 100))
        d.ellipse((stem_x - w * 0.08, h * 0.13, stem_x + w * 0.08, h * 0.29), fill=(*INK, 255))
    return im


def get_asset(asset: dict, spec_path: Path, size: tuple[int, int], accent, seed: int, render_mode: str, paper=PAPER) -> Image.Image:
    path = asset_path(asset, spec_path)
    kind = asset.get("type", "relief-print")
    if path and path.exists():
        if kind == "mono-photo":
            return process_photo(path, size, paper).convert("RGBA")
        return process_cutout(path, size)
    if kind == "color-block" or render_mode == "draft":
        return programmatic_asset(asset, size, accent, seed)
    raise ValueError(f"Final render requires a real asset path for {kind}: {asset.get('subject', 'unnamed asset')}")


def layout_anchor(zone: str, width: int, height: int, box_w: int, box_h: int, margin: int) -> tuple[int, int]:
    x_map = {"left": margin, "center": (width - box_w) // 2, "right": width - margin - box_w}
    y_map = {"upper": margin * 2, "middle": (height - box_h) // 2, "lower": height - margin * 2 - box_h}
    if zone == "center":
        return x_map["center"], y_map["middle"]
    parts = zone.split("-")
    return x_map[parts[-1]], y_map[parts[0]]


def opposite_side(zone: str, width: int, box_width: int, margin: int) -> int:
    """Place a text box opposite the declared focal cluster without overlap."""
    if zone.endswith("right"):
        return margin
    if zone.endswith("left"):
        return width - margin - box_width
    return margin


def place_two_columns(zone: str, width: int, margin: int, gap: int, asset_width: int, preferred_text_width: int):
    usable = width - margin * 2
    text_width = min(preferred_text_width, usable - asset_width - gap)
    if text_width <= 0:
        raise ValueError("Canvas is too narrow for the selected text and asset composition")
    if zone.endswith("left"):
        return width - margin - text_width, margin, text_width
    return margin, width - margin - asset_width, text_width


def render(spec_path: Path) -> tuple[Path, Path]:
    cfg = json.loads(spec_path.read_text(encoding="utf-8"))
    validation_errors = validate(cfg, spec_path.parent)
    if validation_errors:
        raise ValueError("Invalid card specification:\n- " + "\n- ".join(validation_errors))
    width, height = int(cfg["width"]), int(cfg["height"])
    short = min(width, height)
    seed = int(cfg.get("seed", 1975))
    accent = ACCENTS.get(str(cfg.get("accent", "blue")), ACCENTS["blue"])
    paper = make_paper(width, height, seed)
    img = paper.convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    margin = int(short * 0.062)
    safe = (margin, margin, width - margin, height - margin)
    landscape = width > height
    base = short / 1242 if not landscape else short / 900
    priority = cfg.get("priority", "balanced")
    render_mode = cfg.get("render_mode", "final")
    title_px = int((58 if priority == "readable" else 52 if priority == "balanced" else 48) * max(0.72, base))
    body_px = int((38 if priority == "readable" else 34 if priority == "balanced" else 34) * max(0.72, base))
    micro_px = max(15, int(23 * max(0.68, base)))
    title_font = load_font(title_px, "serif")
    body_font = load_font(body_px, "serif")
    micro_font = load_font(micro_px, "mono")
    title_boxes, body_boxes, micro_boxes, asset_boxes, asset_opaque_boxes, asset_alpha_paths = [], [], [], [], [], []
    layout = cfg.get("layout", "quiet-specimen")
    zone = cfg.get("cluster_zone", "center")
    assets = cfg.get("assets", [])

    wide_short = landscape and height / width < 0.58
    if landscape:
        cluster_w = int(width * (0.21 if wide_short else 0.24))
        cluster_h = int(height * (0.42 if wide_short else 0.46))
    else:
        cluster_w = int(width * (0.26 if height <= width * 1.18 else 0.30))
        cluster_h = int(height * (0.22 if height <= width * 1.18 else 0.20))
    ax, ay = layout_anchor(zone, width, height, cluster_w, cluster_h, margin)
    if cfg.get("canvas_preset") == "portrait-9x16":
        ui_top = int(height * 0.10)
        ui_bottom = int(height * 0.88)
        ay = min(max(ay, ui_top), ui_bottom - cluster_h)
    low_canvas = height <= 600
    compact_canvas = height <= 600 or (height <= width * 1.10 and short <= 600)
    gap = max(margin, int(short * 0.045))

    def draw_copy(tx, ty, title_width, body_width, title_limit=4, body_limit=8):
        nonlocal title_boxes, body_boxes
        title_gap = int(title_px * 0.42)
        body_gap = int(body_px * 0.45)
        inter_gap = max(int(body_px * 0.45), int(short * 0.012))
        available_top = int(height * 0.10) if cfg.get("canvas_preset") == "portrait-9x16" else margin
        available_bottom = int(height * 0.88) if cfg.get("canvas_preset") == "portrait-9x16" else height - margin

        def draw_on_layer(start_y):
            layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer, "RGBA")
            _, measured_title = draw_text_block(
                layer_draw, (tx, start_y), cfg["title"], title_font, INK,
                title_width, title_gap, title_limit,
            )
            body_y = max([box[3] for box in measured_title] or [start_y]) + inter_gap
            _, measured_body = draw_text_block(
                layer_draw, (tx, body_y), cfg["body"], body_font, INK,
                body_width, body_gap, body_limit,
            )
            return layer, measured_title, measured_body

        text_layer, title_boxes, body_boxes = draw_on_layer(ty)
        essential = title_boxes + body_boxes
        if essential:
            min_y = min(box[1] for box in essential)
            max_y = max(box[3] for box in essential)
            shift_y = 0
            if max_y > available_bottom:
                shift_y = available_bottom - max_y
            if min_y + shift_y < available_top:
                shift_y += available_top - (min_y + shift_y)
            if shift_y:
                text_layer, title_boxes, body_boxes = draw_on_layer(ty + shift_y)
            final_essential = title_boxes + body_boxes
            final_max_y = max(box[3] for box in final_essential)
            if final_max_y > available_bottom:
                final_shift = available_bottom - final_max_y
                shifted_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                shifted_layer.alpha_composite(text_layer, (0, final_shift))
                text_layer = shifted_layer
                title_boxes = [(x0, y0 + final_shift, x1, y1 + final_shift) for x0, y0, x1, y1 in title_boxes]
                body_boxes = [(x0, y0 + final_shift, x1, y1 + final_shift) for x0, y0, x1, y1 in body_boxes]
        img.alpha_composite(text_layer)
        return max([box[3] for box in title_boxes + body_boxes] or [ty])

    def paste_asset(index, box, opacity=255):
        if index >= len(assets):
            return
        x, y, w, h = box
        asset_im = get_asset(assets[index], spec_path, (w, h), accent, seed + index * 97, render_mode)
        if opacity != 255:
            asset_im.putalpha(asset_im.getchannel("A").point(lambda v: int(v * opacity / 255)))
        img.alpha_composite(asset_im, (x, y))
        asset_boxes.append((x, y, x + w, y + h))
        alpha_bbox = asset_im.getchannel("A").getbbox()
        if alpha_bbox:
            asset_opaque_boxes.append((
                x + alpha_bbox[0], y + alpha_bbox[1],
                x + alpha_bbox[2], y + alpha_bbox[3],
            ))
        else:
            asset_opaque_boxes.append((x, y, x, y))
        output = Path(cfg["output"])
        if not output.is_absolute():
            output = (spec_path.parent / output).resolve()
        alpha_path = output.with_suffix(output.suffix + f".asset-{index}.alpha.png")
        alpha_path.parent.mkdir(parents=True, exist_ok=True)
        asset_im.getchannel("A").save(alpha_path)
        asset_alpha_paths.append(str(alpha_path))

    def portrait_asset_position(box_w: int, box_h: int, default_right: bool = False):
        centered = zone == "center" or zone.endswith("center")
        on_right = zone.endswith("right") or (centered and default_right)
        x = width - margin - box_w if on_right else margin
        y = layout_anchor(zone, width, height, box_w, box_h, margin)[1]
        return x, y, on_right

    if landscape:
        asset_w = int(width * (0.25 if not wide_short else 0.20))
        asset_h = int(height * (0.50 if not wide_short else 0.56))
        text_w = int(width * (0.43 if layout == "text-led-note" else 0.38))
        tx, ax, text_w = place_two_columns(zone, width, margin, gap, asset_w, text_w)
        ay = layout_anchor(zone, width, height, asset_w, asset_h, margin)[1]
        ty = max(margin, int(height * (0.25 if layout == "text-led-note" else 0.31)))
        if layout == "text-led-note":
            asset_w, asset_h = int(asset_w * 0.45), int(asset_h * 0.52)
            ax = width - margin - asset_w if tx < width // 2 else margin
            ay = min(height - margin - asset_h, ty + int(title_px * 1.2))
        paste_asset(0, (ax, ay, asset_w, asset_h))
        if len(assets) > 1:
            paste_asset(1, (ax + asset_w // 2, ay + asset_h // 2, asset_w // 2, asset_h // 2), 190)
        draw_copy(tx, ty, text_w, int(text_w * 0.94), 4, 7)
        if layout in {"archive-collage", "relief-emblem", "quiet-specimen"}:
            d.line((ax + asset_w // 2, ay + asset_h // 2, tx, ty + title_px), fill=(*MUTED, 105), width=1)
    elif layout == "archive-collage":
        asset_w, asset_h = int(width * 0.46), int(height * 0.37)
        ax, ay, asset_on_right = portrait_asset_position(asset_w, asset_h)
        text_w = int(width * 0.34)
        tx = margin if asset_on_right else width - margin - text_w
        ty = max(margin * 2, ay + int(asset_h * 0.17))
        paste_asset(0, (ax, ay, asset_w, asset_h))
        if len(assets) > 1:
            second_w, second_h = int(asset_w * 0.54), int(asset_h * 0.43)
            second_x = ax + int(asset_w * 0.06)
            second_y = min(height - margin - second_h, ay + int(asset_h * 0.78))
            paste_asset(1, (second_x, second_y, second_w, second_h), 225)
        draw_copy(tx, ty, text_w, int(text_w * 0.96), 4, 8)
        rule_y = min(height - margin, ty + int(asset_h * 0.66))
        d.line((tx, rule_y, tx + text_w, rule_y), fill=(*MUTED, 120), width=1)
    elif layout == "relief-emblem":
        asset_w, asset_h = int(width * 0.44), int(height * 0.35)
        ax, ay, asset_on_right = portrait_asset_position(asset_w, asset_h, default_right=True)
        text_w = int(width * 0.35)
        tx = margin if asset_on_right else width - margin - text_w
        ty = max(margin * 2, ay + int(asset_h * 0.22))
        paste_asset(0, (ax, ay, asset_w, asset_h))
        if len(assets) > 1:
            paste_asset(1, (ax + int(asset_w * 0.60), ay + int(asset_h * 0.62), int(asset_w * 0.42), int(asset_h * 0.32)), 190)
        draw_copy(tx, ty, text_w, int(text_w * 0.95), 4, 8)
        line_start = ax + asset_w if ax < tx else ax
        line_end = tx if ax < tx else tx + text_w
        d.line((line_start, ay + asset_h // 2, line_end, ty + title_px), fill=(*MUTED, 115), width=1)
    elif layout == "silhouette-field":
        asset_w, asset_h = int(width * 0.36), int(height * 0.29)
        ax, ay, asset_on_right = portrait_asset_position(asset_w, asset_h, default_right=True)
        text_w = int(width * 0.46)
        tx = margin if asset_on_right else width - margin - text_w
        ty = max(margin * 2, ay + int(asset_h * 0.10))
        paste_asset(0, (ax, ay, asset_w, asset_h))
        if len(assets) > 1:
            paste_asset(1, (ax - int(asset_w * 0.10), ay + int(asset_h * 0.52), int(asset_w * 0.55), int(asset_h * 0.42)), 145)
        draw_copy(tx, ty, text_w, int(text_w * 0.92), 4, 8)
        for index, (dx, dy) in enumerate(((0.10, 1.06), (0.52, 1.15), (0.92, 1.02))):
            cx, cy = ax + int(asset_w * dx), ay + int(asset_h * dy)
            radius = max(3, short // (270 + index * 30))
            d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(*accent, 235))
    elif layout == "text-led-note":
        text_w = int(width * 0.58)
        tx = margin * 2 if not zone.endswith("right") else width - margin * 2 - text_w
        ty = max(margin * 3, int(height * (0.28 if zone.startswith("upper") else 0.36 if zone.startswith("middle") or zone == "center" else 0.48)))
        draw_copy(tx, ty, text_w, int(text_w * 0.92), 4, 8)
        small_w, small_h = int(width * 0.16), int(height * 0.12)
        sx = width - margin - small_w if tx < width // 2 else margin
        sy = min(height - margin - small_h, ty + int(height * 0.36))
        paste_asset(0, (sx, sy, small_w, small_h))
        if len(assets) > 1:
            paste_asset(1, (sx + small_w // 2, sy + small_h // 2, small_w // 2, small_h // 2), 175)
        slash_x = tx + int(text_w * 0.78)
        slash_y = min(height - margin * 2, ty + int(height * 0.36))
        d.line((slash_x, slash_y, slash_x + int(short * 0.035), slash_y - int(short * 0.075)), fill=(*INK, 155), width=1)
    else:  # quiet-specimen
        asset_w, asset_h = int(width * 0.29), int(height * 0.24)
        ax, ay, asset_on_right = portrait_asset_position(asset_w, asset_h)
        text_w = int(width * 0.43)
        tx = margin if asset_on_right else width - margin - text_w
        ty = max(margin * 2, ay + int(asset_h * 0.16))
        paste_asset(0, (ax, ay, asset_w, asset_h))
        if len(assets) > 1:
            paste_asset(1, (ax + int(asset_w * 0.68), ay + int(asset_h * 0.62), int(asset_w * 0.38), int(asset_h * 0.34)), 175)
        draw_copy(tx, ty, text_w, int(text_w * 0.94), 4, 8)
        line_start = ax + asset_w if ax < tx else ax
        line_end = tx if ax < tx else tx + text_w
        d.line((line_start, ay + int(asset_h * 0.58), line_end, ty + int(title_px * 0.70)), fill=(*MUTED, 100), width=1)

    annotations = [] if compact_canvas else cfg.get("annotations", [])
    bottom_annotation_y = max(margin, height - margin - micro_px)
    positions = [(margin, margin), (width - margin, bottom_annotation_y), (margin, bottom_annotation_y)]
    for index, annotation in enumerate(annotations[:3]):
        px, py = positions[index]
        annotation_face = load_font(micro_px, "sans" if contains_cjk(annotation) else "mono")
        if index == 1:
            annotation_width = d.textlength(str(annotation), font=annotation_face)
            px = max(margin, int(px - annotation_width))
        box = d.textbbox((px, py), str(annotation), font=annotation_face)
        d.text((px, py), str(annotation), font=annotation_face, fill=(*MUTED, 205))
        micro_boxes.append(tuple(map(int, box)))
    d.ellipse((margin, margin + micro_px * 1.8, margin + max(5, short // 190), margin + micro_px * 1.8 + max(5, short // 190)), fill=(*accent, 255))

    all_boxes = title_boxes + body_boxes + micro_boxes + asset_boxes
    for box in all_boxes:
        if box[0] < 0 or box[1] < 0 or box[2] > width or box[3] > height:
            raise ValueError(f"Element outside canvas: {box}")

    output = Path(cfg["output"])
    if not output.is_absolute():
        output = (spec_path.parent / output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output, quality=96)
    meta = {
        "canvas": {"width": width, "height": height, "preset": cfg["canvas_preset"]},
        "safe_area": safe,
        "priority": priority,
        "layout": layout,
        "cluster_zone": zone,
        "asset_count": len(assets),
        "accent": cfg.get("accent", "blue"),
        "accent_rgb": accent,
        "font_sizes": {"title": title_px, "body": body_px, "micro": micro_px},
        "title_boxes": title_boxes,
        "body_boxes": body_boxes,
        "micro_boxes": micro_boxes,
        "asset_boxes": asset_boxes,
        "asset_opaque_boxes": asset_opaque_boxes,
        "asset_alpha_paths": asset_alpha_paths,
        "output": str(output),
    }
    meta_path = output.with_suffix(output.suffix + ".layout.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return output, meta_path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: render_card.py card.json", file=sys.stderr)
        return 2
    output, meta = render(Path(sys.argv[1]).resolve())
    print(output)
    print(meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
