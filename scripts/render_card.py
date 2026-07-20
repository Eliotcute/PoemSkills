#!/usr/bin/env python3
"""Render one publish-ready poetic-archive card from a validated JSON spec."""

from __future__ import annotations

import json
import math
import random
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


def load_font(size: int, family: str = "serif") -> ImageFont.FreeTypeFont:
    choices = SERIF_FONTS if family == "serif" else SANS_FONTS if family == "sans" else MONO_FONTS
    for candidate in choices:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=max(8, int(size)), index=0)
    return ImageFont.load_default(size=max(8, int(size)))


def wrap_chars(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            trial = current + char
            if current and draw.textlength(trial, font=face) > max_width:
                lines.append(current.rstrip())
                current = char.lstrip()
            else:
                current = trial
        if current:
            lines.append(current.rstrip())
    return lines


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
    im.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - im.width) // 2
    y = (size[1] - im.height) // 2
    if im.getextrema()[3] == (255, 255):
        gray = ImageOps.grayscale(im.convert("RGB"))
        alpha = ImageOps.invert(gray).point(lambda value: 255 if value > 30 else 0)
        colored = Image.new("RGBA", im.size, (*color, 255))
        colored.putalpha(alpha)
        im = colored
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


def get_asset(asset: dict, spec_path: Path, size: tuple[int, int], accent, seed: int, paper=PAPER) -> Image.Image:
    path = asset_path(asset, spec_path)
    kind = asset.get("type", "relief-print")
    if path and path.exists():
        if kind == "mono-photo":
            return process_photo(path, size, paper).convert("RGBA")
        return process_cutout(path, size)
    return programmatic_asset(asset, size, accent, seed)


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
    title_px = int((68 if priority == "readable" else 60 if priority == "balanced" else 50) * max(0.72, base))
    body_px = int((42 if priority == "readable" else 38 if priority == "balanced" else 34) * max(0.72, base))
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
        asset_im = get_asset(assets[index], spec_path, (w, h), accent, seed + index * 97)
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

    if layout == "archive-collage":
        text_w = int(width * (0.40 if landscape else 0.42))
        tx, ax, text_w = place_two_columns(zone, width, margin, gap, cluster_w, text_w)
        ay = layout_anchor(zone, width, height, cluster_w, cluster_h, margin)[1]
        photo_box = (ax, ay, cluster_w, cluster_h)
        paste_asset(0, photo_box)
        if len(assets) > 1:
            second = (ax + int(cluster_w * 0.54), ay + int(cluster_h * 0.56), int(cluster_w * 0.58), int(cluster_h * 0.48))
            paste_asset(1, second)
        ty = max(margin, ay + int(cluster_h * 0.12))
        draw_copy(tx, ty, text_w, int(text_w * 0.94), 4, 8)
    elif layout == "relief-emblem":
        text_w = int(width * (0.40 if landscape else 0.40))
        tx, ax, text_w = place_two_columns(zone, width, margin, gap, cluster_w, text_w)
        ay = layout_anchor(zone, width, height, cluster_w, cluster_h, margin)[1]
        paste_asset(0, (ax, ay, cluster_w, cluster_h))
        if len(assets) > 1:
            paste_asset(1, (ax + int(cluster_w * 0.56), ay + int(cluster_h * 0.58), int(cluster_w * 0.54), int(cluster_h * 0.38)), 210)
        ty = max(margin * 2, ay + int(cluster_h * 0.18))
        draw_copy(tx, ty, text_w, int(text_w * 0.94), 4, 8)
        d.line((ax + cluster_w // 2, ay + cluster_h // 2, tx, ty + title_px), fill=(*MUTED, 110), width=max(1, short // 900))
    elif layout == "silhouette-field":
        text_w = int(width * (0.40 if landscape else 0.40))
        tx, ax, text_w = place_two_columns(zone, width, margin, gap, cluster_w, text_w)
        ay = layout_anchor(zone, width, height, cluster_w, cluster_h, margin)[1]
        paste_asset(0, (ax, ay, cluster_w, cluster_h))
        if len(assets) > 1:
            paste_asset(1, (ax + int(cluster_w * 0.4), ay - int(cluster_h * 0.12), int(cluster_w * 0.66), int(cluster_h * 0.52)), 155)
        ty = max(margin * 2, ay + int(cluster_h * 0.1))
        draw_copy(tx, ty, text_w, int(text_w * 0.94), 4, 8)
        for index in range(3):
            cx = ax + int(cluster_w * (0.18 + index * 0.34))
            cy = ay + cluster_h + int(short * 0.035 * (index % 2))
            d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=(*accent, 255))
    elif layout == "text-led-note":
        small_w, small_h = int(cluster_w * 0.48), int(cluster_h * 0.52)
        text_w = int(width * (0.50 if landscape else 0.52))
        tx, sx, text_w = place_two_columns(zone, width, margin, gap, small_w, text_w)
        ty = max(margin * 2, int(height * (0.31 if landscape else 0.28)))
        copy_bottom = draw_copy(tx, ty, text_w, int(text_w * 0.92), 4, 8)
        sy = min(height - margin - small_h, max(margin, ty + int(title_px * 1.1)))
        if sy < copy_bottom and sx < tx + text_w and sx + small_w > tx:
            sy = min(height - margin - small_h, copy_bottom + gap)
        paste_asset(0, (sx, sy, small_w, small_h))
        if len(assets) > 1:
            paste_asset(1, (sx + small_w // 2, sy + small_h // 2, small_w // 2, small_h // 2), 190)
    else:  # quiet-specimen
        text_w = int(width * (0.40 if not landscape else 0.40))
        tx, ax, text_w = place_two_columns(zone, width, margin, gap, cluster_w, text_w)
        ay = layout_anchor(zone, width, height, cluster_w, cluster_h, margin)[1]
        paste_asset(0, (ax, ay, cluster_w, cluster_h))
        if len(assets) > 1:
            paste_asset(1, (ax + int(cluster_w * 0.62), ay + int(cluster_h * 0.62), int(cluster_w * 0.44), int(cluster_h * 0.40)), 190)
        ty = int(height * 0.30) if landscape else max(margin * 2, ay + int(cluster_h * 0.10))
        draw_copy(tx, ty, text_w, int(text_w * 0.94), 4, 8)

    annotations = [] if compact_canvas else cfg.get("annotations", [])
    bottom_annotation_y = max(margin, height - margin - micro_px)
    positions = [(margin, margin), (width - margin, bottom_annotation_y), (margin, bottom_annotation_y)]
    for index, annotation in enumerate(annotations[:3]):
        px, py = positions[index]
        if index == 1:
            annotation_width = d.textlength(str(annotation), font=micro_font)
            px = max(margin, int(px - annotation_width))
        box = d.textbbox((px, py), str(annotation), font=micro_font)
        d.text((px, py), str(annotation), font=micro_font, fill=(*MUTED, 205))
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
