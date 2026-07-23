#!/usr/bin/env python3
"""Validate versioned PoemSkills stage artifacts and upstream digests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CONTRACTS = {
    "poem-content-plan/v1": {
        "output_scope",
        "source_ref",
        "source_digest",
        "topic",
        "reader_tension",
        "reader_payoff",
        "strongest_evidence",
        "boundaries",
        "desired_action",
        "cover_direction",
        "cards",
    },
    "poem-title-plan/v1": {
        "content_plan_digest",
        "cover_candidates",
        "selected_cover",
        "publishing_titles",
        "selected_publishing_title",
        "publication_package",
    },
    "poem-design-plan/v1": {
        "content_plan_digest",
        "canvas",
        "reference_contract",
        "variants",
        "selected_variant",
        "production_ready",
        "card_specs",
    },
    "poem-artifact-manifest/v1": {"card_specs_digest", "outputs"},
    "poem-review-report/v1": {
        "artifact_manifest_digest",
        "approved",
        "deliverable",
        "scores",
        "lowest_category",
        "revision_summary",
        "remaining_risk",
    },
}
UPSTREAM_DIGEST_FIELDS = {
    "poem-title-plan/v1": "content_plan_digest",
    "poem-artifact-manifest/v1": "card_specs_digest",
    "poem-review-report/v1": "artifact_manifest_digest",
}
UPSTREAM_COUNTS = {
    "poem-title-plan/v1": (1, 1),
    "poem-design-plan/v1": (1, 2),
    "poem-artifact-manifest/v1": (1, None),
    "poem-review-report/v1": (1, 1),
}


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def combined_digest(paths: list[Path]) -> str:
    if len(paths) == 1:
        return file_digest(paths[0])
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item.resolve())):
        digest.update(str(path.resolve()).encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def require_text(payload: dict, field: str, errors: list[str]) -> None:
    if not isinstance(payload.get(field), str) or not payload[field].strip():
        errors.append(f"{field} must be a non-empty string")


def validate_content_plan(payload: dict, errors: list[str]) -> None:
    output_scope = payload.get("output_scope")
    allowed_scopes = {"cover-only", "cover-plus-interiors", "interiors-only"}
    if output_scope not in allowed_scopes:
        errors.append(f"output_scope must be one of {sorted(allowed_scopes)}")
    for field in (
        "source_ref", "topic", "reader_tension", "reader_payoff",
        "strongest_evidence", "boundaries", "desired_action", "cover_direction",
    ):
        require_text(payload, field, errors)
    if not SHA256_RE.fullmatch(str(payload.get("source_digest", ""))):
        errors.append("source_digest must be a lowercase SHA-256 digest")
    cards = payload.get("cards")
    if not isinstance(cards, list):
        errors.append("cards must be a list")
        return
    if output_scope == "cover-only" and cards:
        errors.append("cover-only ContentPlan must not contain interior cards")
    if output_scope != "cover-only" and not cards:
        errors.append("cards must be non-empty unless output_scope is cover-only")
        return
    required = {
        "card_id", "role", "claim", "source_excerpt", "body",
        "reason_to_exist", "image_need", "image_role",
    }
    card_ids: list[str] = []
    allowed_roles = {"context", "claim", "mechanism", "evidence", "use", "source"}
    allowed_image_roles = {"none", "explain", "evidence", "compare", "locate", "sequence", "symbolize", "document"}
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            errors.append(f"cards[{index}] must be an object")
            continue
        missing = required - card.keys()
        if missing:
            errors.append(f"cards[{index}] missing fields: {sorted(missing)}")
        for field in ("card_id", "role", "claim", "source_excerpt", "body", "reason_to_exist", "image_role"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                errors.append(f"cards[{index}].{field} must be a non-empty string")
        if isinstance(card.get("card_id"), str) and card["card_id"].strip():
            card_ids.append(card["card_id"].strip())
        if card.get("role") not in allowed_roles:
            errors.append(f"cards[{index}].role must be one of {sorted(allowed_roles)}")
        image_need = card.get("image_need")
        image_role = card.get("image_role")
        if not isinstance(image_need, bool):
            errors.append(f"cards[{index}].image_need must be boolean")
        if image_role not in allowed_image_roles:
            errors.append(f"cards[{index}].image_role must be one of {sorted(allowed_image_roles)}")
        elif image_need is False and image_role != "none":
            errors.append(f"cards[{index}].image_role must be none when image_need is false")
        elif image_need is True and image_role == "none":
            errors.append(f"cards[{index}].image_role must explain why the requested image exists")
    if len(card_ids) != len(set(card_ids)):
        errors.append("cards[].card_id values must be unique")


def validate_title_plan(payload: dict, errors: list[str]) -> None:
    candidates = payload.get("cover_candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        errors.append("cover_candidates must contain exactly three candidates")
    else:
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, str) or not candidate.strip():
                errors.append(f"cover_candidates[{index}] must be a non-empty string")
        normalized_candidates = [re.sub(r"\s+", "", candidate) for candidate in candidates if isinstance(candidate, str)]
        if len(normalized_candidates) != len(set(normalized_candidates)):
            errors.append("cover_candidates must be three distinct candidates")
    selected = payload.get("selected_cover")
    if not isinstance(selected, dict):
        errors.append("selected_cover must be an object")
    else:
        missing = {"title", "lines", "subtitle", "selection_reason"} - selected.keys()
        if missing:
            errors.append(f"selected_cover missing fields: {sorted(missing)}")
        for field in ("title", "selection_reason"):
            if not isinstance(selected.get(field), str) or not selected[field].strip():
                errors.append(f"selected_cover.{field} must be a non-empty string")
        if not isinstance(selected.get("subtitle"), str):
            errors.append("selected_cover.subtitle must be a string")
        lines = selected.get("lines")
        if not isinstance(lines, list) or not 2 <= len(lines) <= 4:
            errors.append("selected_cover.lines must contain two to four deliberate lines")
        elif any(not isinstance(line, str) or not line.strip() for line in lines):
            errors.append("selected_cover.lines must contain only non-empty strings")
        elif isinstance(selected.get("title"), str) and re.sub(r"\s+", "", selected["title"]) != re.sub(r"\s+", "", "".join(lines)):
            errors.append("selected_cover.lines must reproduce selected_cover.title exactly")
        if isinstance(candidates, list) and isinstance(selected.get("title"), str):
            selected_title = re.sub(r"\s+", "", selected["title"])
            normalized_candidates = {re.sub(r"\s+", "", value) for value in candidates if isinstance(value, str)}
            if selected_title not in normalized_candidates:
                errors.append("selected_cover.title must match one cover candidate")
    titles = payload.get("publishing_titles")
    if not isinstance(titles, list) or not titles:
        errors.append("publishing_titles must be a non-empty list")
    else:
        for index, title in enumerate(titles):
            if not isinstance(title, str) or not title.strip():
                errors.append(f"publishing_titles[{index}] must be a non-empty string")
    require_text(payload, "selected_publishing_title", errors)
    if isinstance(titles, list) and payload.get("selected_publishing_title") not in titles:
        errors.append("selected_publishing_title must match one publishing title candidate")

    package = payload.get("publication_package")
    if not isinstance(package, dict):
        errors.append("publication_package must be an object")
        return
    xhs = package.get("xiaohongshu")
    wechat = package.get("wechat")
    if not isinstance(xhs, dict):
        errors.append("publication_package.xiaohongshu must be an object")
    else:
        for field in ("title", "body"):
            if not isinstance(xhs.get(field), str) or not xhs[field].strip():
                errors.append(f"publication_package.xiaohongshu.{field} must be a non-empty string")
        tags = xhs.get("tags")
        if not isinstance(tags, list) or not tags or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
            errors.append("publication_package.xiaohongshu.tags must be a non-empty list of strings")
        if isinstance(xhs.get("title"), str) and xhs["title"] != payload.get("selected_publishing_title"):
            errors.append("publication_package.xiaohongshu.title must match selected_publishing_title")
    if not isinstance(wechat, dict):
        errors.append("publication_package.wechat must be an object")
    else:
        for field in ("title", "summary"):
            if not isinstance(wechat.get(field), str) or not wechat[field].strip():
                errors.append(f"publication_package.wechat.{field} must be a non-empty string")
    if not isinstance(package.get("alt_text"), str) or not package["alt_text"].strip():
        errors.append("publication_package.alt_text must be a non-empty string")


def validate_expected_artifact(
    path: Path,
    expected_contract: str,
    label: str,
    errors: list[str],
) -> dict | None:
    try:
        upstream = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label} is not a readable JSON artifact: {exc}")
        return None
    if not isinstance(upstream, dict):
        errors.append(f"{label} must contain a JSON object")
        return None
    if upstream.get("contract") != expected_contract:
        errors.append(f"{label} must use contract {expected_contract}")
    if upstream.get("status") != "validated":
        errors.append(f"{label} must have status: validated")
    return upstream


def validate_design_plan(
    payload: dict,
    errors: list[str],
    artifact_path: Path | None = None,
) -> None:
    require_text(payload, "canvas", errors)
    if not isinstance(payload.get("reference_contract"), dict) or not payload["reference_contract"]:
        errors.append("reference_contract must be a non-empty object")
    variants = payload.get("variants")
    required = {"variant_id", "name", "layout_family", "allowed_layouts", "asset_strategy", "composition", "why"}
    from validate_card_spec import LAYOUTS as card_layouts
    if not isinstance(variants, list) or not variants:
        errors.append("variants must be a non-empty list")
    else:
        for index, variant in enumerate(variants):
            if not isinstance(variant, dict):
                errors.append(f"variants[{index}] must be an object")
                continue
            missing = required - variant.keys()
            if missing:
                errors.append(f"variants[{index}] missing fields: {sorted(missing)}")
            for field in ("variant_id", "name", "layout_family", "asset_strategy", "composition", "why"):
                if not isinstance(variant.get(field), str) or not variant[field].strip():
                    errors.append(f"variants[{index}].{field} must be a non-empty string")
            allowed = variant.get("allowed_layouts")
            if not isinstance(allowed, list) or not allowed:
                errors.append(f"variants[{index}].allowed_layouts must be a non-empty list")
            elif any(layout not in card_layouts for layout in allowed):
                errors.append(f"variants[{index}].allowed_layouts contains an unsupported CardSpec layout")
        ids = [variant.get("variant_id") for variant in variants if isinstance(variant, dict)]
        if len(ids) != len(set(ids)):
            errors.append("variant_id values must be unique")
    ready = payload.get("production_ready")
    if not isinstance(ready, bool):
        errors.append("production_ready must be boolean")
    selected = payload.get("selected_variant")
    specs = payload.get("card_specs")
    if not isinstance(specs, list):
        errors.append("card_specs must be a list")
    elif ready:
        if not isinstance(selected, str) or not selected.strip() or not specs:
            errors.append("production-ready DesignPlan requires selected_variant and card_specs")
        elif isinstance(variants, list) and selected not in {variant.get("variant_id") for variant in variants if isinstance(variant, dict)}:
            errors.append("selected_variant must match one of the declared variants")
        if artifact_path is None:
            errors.append("production-ready DesignPlan requires its artifact path for CardSpec binding")
        elif isinstance(specs, list):
            design_digest = file_digest(artifact_path)
            for index, raw_spec in enumerate(specs):
                if not isinstance(raw_spec, str) or not raw_spec.strip():
                    errors.append(f"card_specs[{index}] must be a path string")
                    continue
                spec_path = Path(raw_spec)
                spec_path = spec_path if spec_path.is_absolute() else artifact_path.parent / spec_path
                if not spec_path.is_file():
                    errors.append(f"card_specs[{index}] does not exist: {spec_path}")
                    continue
                try:
                    spec = json.loads(spec_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"card_specs[{index}] is not valid JSON: {exc}")
                    continue
                if not isinstance(spec, dict):
                    errors.append(f"card_specs[{index}] must contain a JSON object")
                    continue
                if spec.get("contract") != "poem-card-spec/v1" or spec.get("status") != "validated":
                    errors.append(f"card_specs[{index}] must be a validated poem-card-spec/v1")
                if spec.get("design_plan_digest") != design_digest:
                    errors.append(f"card_specs[{index}] is stale or belongs to a different DesignPlan")
                if spec.get("design_variant_id") != selected:
                    errors.append(f"card_specs[{index}].design_variant_id must match selected_variant")
                selected_plan = next(
                    (variant for variant in variants if isinstance(variant, dict) and variant.get("variant_id") == selected),
                    None,
                ) if isinstance(variants, list) else None
                allowed = selected_plan.get("allowed_layouts") if isinstance(selected_plan, dict) else None
                if not isinstance(allowed, list) or spec.get("layout") not in allowed:
                    errors.append(f"card_specs[{index}].layout is not allowed by selected_variant")
                from validate_card_spec import validate as validate_card_spec
                for error in validate_card_spec(spec, spec_path.parent, artifact_path=spec_path):
                    errors.append(f"card_specs[{index}]: {error}")
    else:
        if specs:
            errors.append("non-production DesignPlan must not contain render-ready card_specs")
        if selected not in (None, ""):
            errors.append("non-production DesignPlan must not select a variant")
        if isinstance(variants, list) and not 2 <= len(variants) <= 3:
            errors.append("planning DesignPlan must contain two or three variants")


def resolve_artifact_path(raw_path: str, artifact_path: Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else artifact_path.parent / path


def read_json_artifact(path: Path, label: str, errors: list[str]) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label} is not readable JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{label} must contain a JSON object")
        return None
    return payload


def validate_manifest(
    payload: dict,
    errors: list[str],
    artifact_path: Path | None = None,
) -> None:
    outputs = payload.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        errors.append("outputs must be a non-empty list")
        return
    required_paths = {"spec", "image", "preview", "qa", "layout", "visual_review"}
    evidence_digests = {
        "qa": "qa_sha256",
        "layout": "layout_sha256",
        "visual_review": "visual_review_sha256",
    }
    required = required_paths | set(evidence_digests.values())
    output_spec_paths: list[Path] = []
    for index, output in enumerate(outputs):
        if not isinstance(output, dict):
            errors.append(f"outputs[{index}] must be an object")
            continue
        missing = required - output.keys()
        if missing:
            errors.append(f"outputs[{index}] missing fields: {sorted(missing)}")
            continue
        if artifact_path is None:
            errors.append("ArtifactManifest requires its artifact path to verify output evidence")
            continue
        resolved: dict[str, Path] = {}
        for field in required_paths:
            raw_path = str(output.get(field, "")).strip()
            if not raw_path:
                errors.append(f"outputs[{index}].{field} must be a non-empty path")
                continue
            path = resolve_artifact_path(raw_path, artifact_path)
            resolved[field] = path
            if not path.is_file():
                errors.append(f"outputs[{index}].{field} does not exist: {path}")
        if not required_paths.issubset(resolved) or any(not path.is_file() for path in resolved.values()):
            continue
        output_spec_paths.append(resolved["spec"].resolve())
        for field, digest_field in evidence_digests.items():
            expected_digest = str(output.get(digest_field, ""))
            if not SHA256_RE.fullmatch(expected_digest):
                errors.append(f"outputs[{index}].{digest_field} must be a lowercase SHA-256 digest")
            elif expected_digest != file_digest(resolved[field]):
                errors.append(f"outputs[{index}].{field} changed after ArtifactManifest creation")
        qa = read_json_artifact(resolved["qa"], f"outputs[{index}].qa", errors)
        read_json_artifact(resolved["layout"], f"outputs[{index}].layout", errors)
        read_json_artifact(resolved["visual_review"], f"outputs[{index}].visual_review", errors)
        if qa is None:
            continue
        if qa.get("valid") is not True:
            errors.append(f"outputs[{index}].qa must report valid: true")
        for field, digest_field in (
            ("spec", "spec_sha256"),
            ("image", "image_sha256"),
            ("preview", "preview_sha256"),
            ("layout", "layout_sha256"),
        ):
            if qa.get(digest_field) != file_digest(resolved[field]):
                errors.append(f"outputs[{index}].qa is stale for {field}")
    manifest_digest = str(payload.get("card_specs_digest", ""))
    if not SHA256_RE.fullmatch(manifest_digest):
        errors.append("card_specs_digest must be a lowercase SHA-256 digest")
    elif len(output_spec_paths) == len(outputs):
        if len(set(output_spec_paths)) != len(output_spec_paths):
            errors.append("ArtifactManifest outputs must not reuse a CardSpec path")
        elif manifest_digest != combined_digest(output_spec_paths):
            errors.append("card_specs_digest does not match ArtifactManifest outputs[].spec")


def validate_release_evidence(
    manifest: dict,
    manifest_path: Path,
    errors: list[str],
    report: dict,
) -> None:
    if manifest.get("finalized") is not True or manifest.get("deliverable") is not True:
        errors.append("deliverable ReviewReport requires a finalized, deliverable ArtifactManifest")
    if manifest.get("pixel_valid") is not True:
        errors.append("deliverable ReviewReport requires pixel_valid: true")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, list):
        return
    from validate_visual_review import CATEGORIES, validate as validate_visual_review
    reviewed_scores: list[dict] = []
    for index, output in enumerate(outputs):
        if not isinstance(output, dict):
            continue
        raw_review = str(output.get("visual_review", "")).strip()
        if not raw_review:
            continue
        review_path = resolve_artifact_path(raw_review, manifest_path)
        if not review_path.is_file():
            continue
        review = read_json_artifact(review_path, f"outputs[{index}].visual_review", errors)
        if review is None:
            continue
        if isinstance(review.get("scores"), dict):
            reviewed_scores.append(review["scores"])
        for error in validate_visual_review(review):
            errors.append(f"outputs[{index}].visual_review: {error}")
    report_scores = report.get("scores")
    if len(reviewed_scores) == len(outputs) and isinstance(report_scores, dict):
        for category in CATEGORIES:
            values = [scores.get(category) for scores in reviewed_scores]
            if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
                expected = min(float(value) for value in values)
                actual = report_scores.get(category)
                if not isinstance(actual, (int, float)) or isinstance(actual, bool) or float(actual) != expected:
                    errors.append(
                        f"scores.{category} must equal the lowest score across bound visual reviews ({expected:g})"
                    )


def validate_review(payload: dict, errors: list[str]) -> None:
    from validate_visual_review import CATEGORIES

    if not isinstance(payload.get("approved"), bool):
        errors.append("approved must be boolean")
    if not isinstance(payload.get("deliverable"), bool):
        errors.append("deliverable must be boolean")
    if payload.get("deliverable") and not payload.get("approved"):
        errors.append("deliverable cannot be true when approved is false")
    scores = payload.get("scores")
    if not isinstance(scores, dict) or set(scores) != set(CATEGORIES):
        errors.append("scores must contain exactly the visual review categories")
    else:
        for category in CATEGORIES:
            score = scores[category]
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                errors.append(f"scores.{category} must be numeric")
            elif not 0 <= float(score) <= 10:
                errors.append(f"scores.{category} must be between 0 and 10")
        numeric = {
            category: float(scores[category])
            for category in CATEGORIES
            if isinstance(scores[category], (int, float)) and not isinstance(scores[category], bool)
        }
        lowest = payload.get("lowest_category")
        if lowest not in CATEGORIES:
            errors.append("lowest_category must name one scored category")
        elif len(numeric) == len(CATEGORIES) and numeric[lowest] != min(numeric.values()):
            errors.append("lowest_category must name a category with the actual minimum score")
        if payload.get("approved") is True and len(numeric) == len(CATEGORIES):
            if min(numeric.values()) < 8 or sum(numeric.values()) < 85:
                errors.append("approved ReviewReport must pass every visual score gate")
    if len(str(payload.get("revision_summary", "")).strip()) < 8:
        errors.append("revision_summary must describe the inspection or revision")
    if len(str(payload.get("remaining_risk", "")).strip()) < 2:
        errors.append("remaining_risk must state the remaining risk or explicitly say none")


def validate(
    payload: dict,
    upstreams: list[Path] | None = None,
    source: Path | None = None,
    artifact_path: Path | None = None,
) -> list[str]:
    if not isinstance(payload, dict):
        return ["artifact must contain a JSON object"]
    errors: list[str] = []
    contract = payload.get("contract")
    if contract not in CONTRACTS:
        return [f"contract must be one of {sorted(CONTRACTS)}"]
    if payload.get("status") != "validated":
        errors.append("file-backed stage artifacts require status: validated")
    missing = CONTRACTS[contract] - payload.keys()
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    if contract == "poem-content-plan/v1":
        validate_content_plan(payload, errors)
    elif contract == "poem-title-plan/v1":
        validate_title_plan(payload, errors)
    elif contract == "poem-design-plan/v1":
        validate_design_plan(payload, errors, artifact_path)
    elif contract == "poem-artifact-manifest/v1":
        validate_manifest(payload, errors, artifact_path)
    elif contract == "poem-review-report/v1":
        validate_review(payload, errors)

    upstreams = upstreams or []
    count_rule = UPSTREAM_COUNTS.get(contract)
    if count_rule:
        minimum, maximum = count_rule
        if len(upstreams) < minimum:
            errors.append(f"{contract} requires at least {minimum} upstream artifact(s)")
        elif maximum is not None and len(upstreams) > maximum:
            errors.append(f"{contract} accepts at most {maximum} upstream artifact(s)")

    digest_field = UPSTREAM_DIGEST_FIELDS.get(contract)
    if digest_field:
        value = str(payload.get(digest_field, ""))
        if not SHA256_RE.fullmatch(value):
            errors.append(f"{digest_field} must be a lowercase SHA-256 digest")
        if upstreams and all(path.is_file() for path in upstreams):
            expected = combined_digest(upstreams)
            if value != expected:
                errors.append(f"{digest_field} is stale or belongs to different upstream artifacts")
    if upstreams:
        if contract == "poem-title-plan/v1":
            if len(upstreams) != 1:
                errors.append("TitlePlan requires exactly one ContentPlan upstream")
            else:
                validate_expected_artifact(upstreams[0], "poem-content-plan/v1", "ContentPlan upstream", errors)
        elif contract == "poem-design-plan/v1":
            validate_expected_artifact(upstreams[0], "poem-content-plan/v1", "ContentPlan upstream", errors)
            if len(upstreams) > 1:
                validate_expected_artifact(upstreams[1], "poem-title-plan/v1", "TitlePlan upstream", errors)
            if len(upstreams) > 2:
                errors.append("DesignPlan accepts at most ContentPlan and TitlePlan upstreams")
        elif contract == "poem-artifact-manifest/v1":
            for index, upstream in enumerate(upstreams):
                validate_expected_artifact(upstream, "poem-card-spec/v1", f"CardSpec upstream {index}", errors)
            if artifact_path is not None and isinstance(payload.get("outputs"), list):
                output_specs = {
                    resolve_artifact_path(str(output.get("spec", "")), artifact_path).resolve()
                    for output in payload["outputs"]
                    if isinstance(output, dict) and str(output.get("spec", "")).strip()
                }
                upstream_specs = {path.resolve() for path in upstreams}
                if output_specs != upstream_specs:
                    errors.append("ArtifactManifest outputs must reference exactly the bound CardSpec upstreams")
        elif contract == "poem-review-report/v1":
            if len(upstreams) != 1:
                errors.append("ReviewReport requires exactly one ArtifactManifest upstream")
            else:
                manifest = validate_expected_artifact(
                    upstreams[0], "poem-artifact-manifest/v1", "ArtifactManifest upstream", errors,
                )
                if manifest is not None:
                    validate_manifest(manifest, errors, upstreams[0])
                    if payload.get("deliverable") is True or payload.get("approved") is True:
                        validate_release_evidence(manifest, upstreams[0], errors, payload)
    if contract == "poem-content-plan/v1":
        if source is None:
            errors.append("validated ContentPlan requires --source to bind the source digest")
        elif str(payload.get("source_digest", "")) != file_digest(source):
            errors.append("source_digest is stale or belongs to a different source file")
    if contract == "poem-design-plan/v1":
        for field in ("content_plan_digest", "title_plan_digest"):
            if field in payload and not SHA256_RE.fullmatch(str(payload.get(field, ""))):
                errors.append(f"{field} must be a lowercase SHA-256 digest")
        if upstreams:
            if upstreams[0].is_file() and str(payload.get("content_plan_digest", "")) != file_digest(upstreams[0]):
                errors.append("content_plan_digest is stale or belongs to a different ContentPlan")
            if len(upstreams) > 1 and upstreams[1].is_file() and str(payload.get("title_plan_digest", "")) != file_digest(upstreams[1]):
                errors.append("title_plan_digest is stale or belongs to a different TitlePlan")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?")
    parser.add_argument("--upstream", nargs="+", default=[])
    parser.add_argument("--source", type=Path)
    parser.add_argument("--digest", nargs="+")
    args = parser.parse_args()

    if args.digest:
        print(combined_digest([Path(value).resolve() for value in args.digest]))
        return 0
    if not args.artifact:
        parser.error("artifact is required unless --digest is used")

    artifact = Path(args.artifact).resolve()
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    source = args.source.expanduser().resolve() if args.source else None
    errors = validate(
        payload,
        [Path(value).resolve() for value in args.upstream],
        source,
        artifact,
    )
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
