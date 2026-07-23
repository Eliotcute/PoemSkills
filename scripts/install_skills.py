#!/usr/bin/env python3
"""Install the PoemSkills router and specialist skills as safe symlinks."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


SKILL_PATHS = {
    "poemskills": Path("."),
    "poem-content": Path("skills/poem-content"),
    "poem-title": Path("skills/poem-title"),
    "poem-design": Path("skills/poem-design"),
    "poem-render": Path("skills/poem-render"),
    "poem-review": Path("skills/poem-review"),
}


def default_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home).expanduser() / "skills" if codex_home else Path.home() / ".codex" / "skills"


def install(repo_root: Path, skills_dir: Path, check_only: bool = False) -> list[str]:
    errors: list[str] = []
    skills_dir.mkdir(parents=True, exist_ok=True)
    for name, relative in SKILL_PATHS.items():
        source = (repo_root / relative).resolve()
        target = skills_dir / name
        if not (source / "SKILL.md").is_file():
            errors.append(f"missing source skill: {source}")
            continue
        if target.is_symlink():
            if target.resolve() != source:
                errors.append(f"refusing to replace unrelated symlink: {target}")
            else:
                print(f"OK {name}: {target} -> {source}")
            continue
        if target.exists():
            errors.append(f"refusing to replace existing path: {target}")
            continue
        if check_only:
            errors.append(f"not installed: {target}")
            continue
        target.symlink_to(source, target_is_directory=True)
        print(f"INSTALLED {name}: {target} -> {source}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills-dir", type=Path, default=default_skills_dir())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    errors = install(repo_root, args.skills_dir.expanduser().resolve(), args.check)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
