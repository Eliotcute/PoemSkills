#!/usr/bin/env python3
"""Validate, render, and QA one or more independent card specifications."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REVIEW_CATEGORIES = (
    "semantic_specificity",
    "material_quality",
    "paper_tactility",
    "composition",
    "typography",
    "image_text_relationship",
    "negative_space",
    "series_rhythm",
    "mobile_readability",
    "provenance_restraint",
)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def review_path_for(output: Path) -> Path:
    return output.with_suffix(output.suffix + ".visual-review.json")


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_pending_review(path: Path, image: Path, preview: Path) -> None:
    payload = {
        "status": "pending",
        "image": str(image),
        "preview": str(preview),
        "image_sha256": file_digest(image),
        "preview_sha256": file_digest(preview),
        "scores": {category: None for category in REVIEW_CATEGORIES},
        "lowest_category": None,
        "revision_summary": "",
        "approved": False,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    finalize = "--finalize" in sys.argv[1:]
    arguments = [value for value in sys.argv[1:] if value != "--finalize"]
    if not arguments:
        print("Usage: run_pipeline.py [--finalize] card-01.json [card-02.json ...]", file=sys.stderr)
        return 2

    specs = [Path(name).resolve() for name in arguments]
    python = sys.executable
    for spec in specs:
        run([python, str(SCRIPT_DIR / "validate_card_spec.py"), str(spec)])
    if len(specs) > 1:
        run([python, str(SCRIPT_DIR / "validate_series.py"), *map(str, specs)])

    outputs: list[dict[str, str]] = []
    for spec in specs:
        cfg = json.loads(spec.read_text(encoding="utf-8"))
        output = Path(str(cfg["output"]))
        output = output if output.is_absolute() else (spec.parent / output).resolve()
        preview = output.with_name(output.stem + "-preview" + output.suffix)
        review = review_path_for(output)
        if finalize:
            if not output.exists() or not preview.exists():
                raise FileNotFoundError(f"render and inspect the card before finalizing: {output}")
            run([python, str(SCRIPT_DIR / "validate_visual_review.py"), str(review)])
        else:
            run([python, str(SCRIPT_DIR / "render_card.py"), str(spec)])
            run([python, str(SCRIPT_DIR / "qa_card.py"), str(spec), str(output)])
            write_pending_review(review, output, preview)
        outputs.append(
            {
                "spec": str(spec),
                "image": str(output),
                "preview": str(preview),
                "qa": str(output.with_suffix(output.suffix + ".qa.json")),
                "visual_review": str(review),
            }
        )

    print(json.dumps({
        "valid": finalize,
        "rendered": True,
        "pixel_valid": True,
        "deliverable": finalize,
        "visual_review_required": not finalize,
        "outputs": outputs,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
