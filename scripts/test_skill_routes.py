#!/usr/bin/env python3
"""Validate PoemSkills routing, specialist discovery, and brand isolation."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPECIALISTS = ("poem-content", "poem-title", "poem-design", "poem-render", "poem-review")
BANNED_ACTIVE_TERMS = (
    "Whole Earth", "全球概览", "whole-earth", "古典互联网",
    "1970s independent catalog", "1970 年代反主流文化邮购目录",
)


def frontmatter_name(text: str) -> str | None:
    match = re.search(r"^name:\s*([^\n]+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def main() -> int:
    router = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert frontmatter_name(router) == "poemskills"
    assert len(router.splitlines()) < 160
    for specialist in SPECIALISTS:
        assert f"`$%s`" % specialist in router
        skill_path = ROOT / "skills" / specialist / "SKILL.md"
        agent_path = ROOT / "skills" / specialist / "agents" / "openai.yaml"
        assert skill_path.is_file(), skill_path
        assert agent_path.is_file(), agent_path
        skill_text = skill_path.read_text(encoding="utf-8")
        assert frontmatter_name(skill_text) == specialist
        assert "PoemSkills" in skill_text.split("---", 2)[1]

    active_files = [ROOT / "SKILL.md", ROOT / "README.md", *ROOT.glob("skills/*/SKILL.md")]
    active_files.extend([
        ROOT / "references" / "style-system.md",
        ROOT / "references" / "master-prompt.md",
        ROOT / "references" / "illustration-prompts.md",
    ])
    for path in active_files:
        text = path.read_text(encoding="utf-8")
        for term in BANNED_ACTIVE_TERMS:
            assert term not in text, f"legacy brand term {term!r} remains in {path}"

    route_examples = {
        "提炼长文": "poem-content",
        "封面标题": "poem-title",
        "配图": "poem-design",
        "导出 PNG": "poem-render",
        "能否发布": "poem-review",
    }
    for phrase, specialist in route_examples.items():
        assert phrase in router and specialist in router
    master_prompt = (ROOT / "references" / "master-prompt.md").read_text(encoding="utf-8")
    assert "只要文案和逐卡提示词" in master_prompt
    assert "每张卡片各有一条独立的最终合成提示词" in master_prompt
    assert "一条最终卡片合成提示词" not in master_prompt
    assert "Do not create a DesignPlan or CardSpec" in router
    assert "three total review rounds" in router
    print("skill routes: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
