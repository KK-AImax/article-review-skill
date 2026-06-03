#!/usr/bin/env python3
"""Quick heuristic audit for Markdown, HTML, and text article drafts."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


AI_CLICHES = [
    "in conclusion",
    "delve into",
    "a tapestry of",
    "game-changer",
    "unlock the",
    "in today's fast-paced",
    "it is important to note",
    "comprehensive guide",
    "in this article",
    "today we will",
    "we will discuss",
]

BAD_ANCHORS = {
    "click here",
    "here",
    "learn more",
    "read more",
    "this link",
}

PRIVACY_PATTERNS = [
    ("internal use only", r"\binternal use only\b"),
    ("confidential", r"\bconfidential\b"),
    ("do not share", r"\bdo not share\b"),
    ("NDA", r"\bnda\b"),
    ("unreleased", r"\bunreleased\b"),
    ("roadmap", r"\broadmap\b"),
    ("API key", r"\bapi[_-]?key\b"),
    ("access token", r"\baccess[_-]?token\b"),
    ("secret key", r"\bsecret[_-]?key\b"),
    ("margin", r"\bmargin\b"),
    ("wholesale cost", r"\bwholesale cost\b"),
]

QUESTION_PATTERNS = [
    r"\?",
    r"\b(what|how|which|why|when|where|can|is|are|do|does|should)\b",
]


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.S)


def strip_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def strip_html_tags(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?i)</h[1-6]\s*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(text)


def normalized_body(text: str) -> str:
    text = strip_frontmatter(text)
    text = strip_code_fences(text)
    if re.search(r"<(?:html|body|h[1-6]|p|a|table|img)\b", text, flags=re.I):
        text = strip_html_tags(text)
    return text


def wordish_count(text: str) -> int:
    english_words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", text)
    return len(english_words) + (len(cjk_chars) // 2)


def first_body_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if re.match(r"^\s*#\s+", line):
            continue
        if re.match(r"^\s*[-*_]{3,}\s*$", line):
            continue
        if line.strip():
            lines.append(line.strip())
        if wordish_count(" ".join(lines)) >= 120:
            break
    return " ".join(lines)


def collect_markdown_headings(text: str) -> list[dict[str, str | int]]:
    headings = []
    for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.M):
        headings.append({"level": len(match.group(1)), "text": match.group(2).strip()})
    return headings


def collect_html_headings(text: str) -> list[dict[str, str | int]]:
    headings = []
    for match in re.finditer(r"(?is)<h([1-6])[^>]*>(.*?)</h\1>", text):
        heading_text = re.sub(r"<[^>]+>", " ", match.group(2))
        heading_text = re.sub(r"\s+", " ", html.unescape(heading_text)).strip()
        headings.append({"level": int(match.group(1)), "text": heading_text})
    return headings


def collect_headings(original: str, clean: str) -> list[dict[str, str | int]]:
    return collect_markdown_headings(clean) + collect_html_headings(original)


def collect_links(text: str) -> list[dict[str, str]]:
    links = []
    for match in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", text):
        links.append({"anchor": match.group(1).strip(), "url": match.group(2).strip()})
    for match in re.finditer(r"(?is)<a\b[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", text):
        anchor = re.sub(r"<[^>]+>", " ", match.group(2))
        anchor = re.sub(r"\s+", " ", html.unescape(anchor)).strip()
        links.append({"anchor": anchor, "url": match.group(1).strip()})
    return links


def count_tables(text: str) -> int:
    markdown_tables = len(re.findall(r"(?m)^\s*\|.+\|\s*\n\s*\|[\s:-]+\|", text))
    html_tables = len(re.findall(r"(?is)<table\b", text))
    return markdown_tables + html_tables


def count_images_missing_alt(text: str) -> int:
    markdown_missing = len(re.findall(r"!\[\s*\]\([^)]+\)", text))
    html_images = re.findall(r"(?is)<img\b[^>]*>", text)
    html_missing = 0
    for tag in html_images:
        alt_match = re.search(r"(?i)\balt=['\"]([^'\"]*)['\"]", tag)
        if not alt_match or not alt_match.group(1).strip():
            html_missing += 1
    return markdown_missing + html_missing


def count_faq_questions(headings: list[dict[str, str | int]], text: str) -> int:
    faq_like = 0
    for heading in headings:
        heading_text = str(heading["text"])
        if int(heading["level"]) in (2, 3, 4) and any(
            re.search(pattern, heading_text, flags=re.I) for pattern in QUESTION_PATTERNS
        ):
            faq_like += 1
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^(Q:|Question:)\s+", stripped, flags=re.I):
            faq_like += 1
    return faq_like


def audit(text: str) -> dict:
    clean = normalized_body(text)
    headings = collect_headings(text, clean)
    links = collect_links(text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean) if p.strip()]
    wall_paragraphs = [
        {"index": idx + 1, "words": wordish_count(p), "preview": re.sub(r"\s+", " ", p)[:120]}
        for idx, p in enumerate(paragraphs)
        if wordish_count(p) >= 300
    ]

    first_text = first_body_text(clean)
    first_100 = " ".join(re.findall(r"\S+", first_text)[:100])
    cliches = sorted({phrase for phrase in AI_CLICHES if phrase.lower() in clean.lower()})
    bad_links = [link for link in links if link["anchor"].strip().lower() in BAD_ANCHORS]
    privacy_hits = sorted(
        {label for label, pattern in PRIVACY_PATTERNS if re.search(pattern, clean, flags=re.I)}
    )
    number_count = len(re.findall(r"(?<!\w)(?:\d+(?:\.\d+)?%?|\d{4})(?!\w)", clean))
    passive_count = len(re.findall(r"\b(?:is|are|was|were|be|been|being)\s+\w+(?:ed|en)\b", clean, flags=re.I))
    question_count = len(re.findall(r"\?", clean))
    h1_count = sum(1 for h in headings if int(h["level"]) == 1)
    h2_count = sum(1 for h in headings if int(h["level"]) == 2)
    h3_count = sum(1 for h in headings if int(h["level"]) == 3)
    table_count = count_tables(text)
    images_missing_alt = count_images_missing_alt(text)
    faq_count = count_faq_questions(headings, clean)

    issues: list[tuple[str, str]] = []
    score = 100

    if h1_count == 0:
        issues.append(("high", "No H1 heading detected. Add one clear page title."))
        score -= 8
    elif h1_count > 1:
        issues.append(("medium", "Multiple H1 headings detected. Keep one primary title."))
        score -= 4

    if h2_count < 3:
        issues.append(("high", "Fewer than 3 H2 sections; structure may be too thin for SEO/GEO extraction."))
        score -= 12

    if table_count == 0:
        issues.append(("medium", "No table detected. Add a comparison, spec, checklist, or decision table where relevant."))
        score -= 8

    if faq_count < 3:
        issues.append(("high", f"Only {faq_count} FAQ/PAA-style questions detected; target at least 3 when the topic supports FAQs."))
        score -= 12

    if wall_paragraphs:
        issues.append(("high", f"{len(wall_paragraphs)} paragraph(s) exceed about 300 words. Break them up for mobile readability."))
        score -= min(15, 6 * len(wall_paragraphs))

    if cliches:
        issues.append(("medium", "AI-cliche or filler phrases found: " + ", ".join(cliches[:6])))
        score -= min(10, 3 * len(cliches))

    if bad_links:
        anchors = ", ".join(sorted({link["anchor"] for link in bad_links}))
        issues.append(("medium", f"Vague link anchor text found: {anchors}. Use descriptive destination-specific anchors."))
        score -= min(8, 3 * len(bad_links))

    if images_missing_alt:
        issues.append(("medium", f"{images_missing_alt} image(s) have empty or missing alt text."))
        score -= min(8, 3 * images_missing_alt)

    if number_count < 3:
        issues.append(("medium", "Very few precise numbers detected. Add measurements, dates, ranges, benchmarks, or other evidence where useful."))
        score -= 8

    if passive_count > 12:
        issues.append(("low", f"Passive-voice pattern appears {passive_count} times. Convert key sentences to active voice."))
        score -= 4

    if re.search(r"\b(today we will|we will discuss|in this article)\b", first_100, flags=re.I):
        issues.append(("high", "Opening appears to start with filler instead of a direct answer."))
        score -= 12

    if question_count == 0:
        issues.append(("medium", "No explicit question phrasing detected. Add reader-intent or FAQ-style questions where natural."))
        score -= 6

    if privacy_hits:
        issues.append(("high", "Potential privacy or internal-only terms found: " + ", ".join(privacy_hits[:6])))
        score -= min(20, 8 * len(privacy_hits))

    score = max(0, min(100, score))
    if score >= 85 and not any(level == "high" for level, _ in issues):
        decision = "Publish-ready"
    elif score >= 65:
        decision = "Needs optimization"
    elif score >= 45:
        decision = "Needs revision before publishing"
    else:
        decision = "Hold"

    return {
        "score": score,
        "decision": decision,
        "metrics": {
            "wordish_count": wordish_count(clean),
            "h1": h1_count,
            "h2": h2_count,
            "h3": h3_count,
            "tables": table_count,
            "faq_questions": faq_count,
            "links": len(links),
            "bad_anchor_links": len(bad_links),
            "images_missing_alt": images_missing_alt,
            "numbers": number_count,
            "passive_patterns": passive_count,
            "wall_paragraphs": len(wall_paragraphs),
            "ai_cliches": len(cliches),
            "privacy_flags": len(privacy_hits),
        },
        "issues": [{"severity": level, "message": message} for level, message in issues],
        "wall_paragraphs": wall_paragraphs[:5],
    }


def to_markdown(result: dict, path: Path) -> str:
    lines = [
        f"# Quick Article Audit: {path.name}",
        "",
        f"- Decision: **{result['decision']}**",
        f"- Score: **{result['score']}/100**",
        "",
        "## Metrics",
    ]
    for key, value in result["metrics"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Issues"])
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"- **{issue['severity']}**: {issue['message']}")
    else:
        lines.append("- No major heuristic issues detected.")
    if result["wall_paragraphs"]:
        lines.extend(["", "## Long Paragraph Previews"])
        for item in result["wall_paragraphs"]:
            lines.append(f"- Paragraph {item['index']} ({item['words']} words): {item['preview']}")
    lines.append("")
    lines.append("> Heuristic scan only. It does not replace factual review, plagiarism checks, grammar tools, SERP/PAA research, expert review, or mobile preview.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Quick heuristic audit for article drafts.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="json")
    args = parser.parse_args()

    text = read_text(args.path)
    result = audit(text)
    if args.format == "markdown":
        print(to_markdown(result, args.path))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
