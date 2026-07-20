#!/usr/bin/env python3
"""Validate, render, and QA one or more independent card specifications."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: run_pipeline.py card-01.json [card-02.json ...]", file=sys.stderr)
        return 2

    specs = [Path(name).resolve() for name in sys.argv[1:]]
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
        run([python, str(SCRIPT_DIR / "render_card.py"), str(spec)])
        run([python, str(SCRIPT_DIR / "qa_card.py"), str(spec), str(output)])
        outputs.append(
            {
                "spec": str(spec),
                "image": str(output),
                "preview": str(output.with_name(output.stem + "-preview" + output.suffix)),
                "qa": str(output.with_suffix(output.suffix + ".qa.json")),
            }
        )

    print(json.dumps({"valid": True, "outputs": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
