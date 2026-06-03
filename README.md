# Article Review Skill

Article Review Skill is a Codex skill for auditing article drafts before publication. It helps review Markdown, HTML, and plain-text drafts for SEO, GEO/AI-search readiness, E-E-A-T, editorial quality, publishing details, useful next actions, and privacy-safe sharing.

The project is intentionally brand-neutral. It does not include private site data, proprietary strategy, customer information, or organization-specific SEO targets.

## What It Checks

- Direct answer and search intent match
- H1/H2/H3 structure and AI-search extractability
- FAQ/PAA coverage and question-led sections
- Tables for comparisons, specs, decisions, or steps
- Evidence, precise claims, E-E-A-T, and human review flags
- Link anchor quality and next-action clarity
- Meta, URL, image alt text, and publishing readiness
- Privacy, confidential wording, and internal-only risk

## Repository Layout

```text
article-review-skill/
  skill/article-review-skill/      # Installable Codex skill package
    SKILL.md
    agents/openai.yaml
    references/review-standards.md
    scripts/audit_article.py
  examples/
    sample-article.md
```

## Install

Copy the skill package into your Codex skills directory:

```bash
cp -R skill/article-review-skill ~/.codex/skills/article-review-skill
```

On Windows PowerShell:

```powershell
Copy-Item -Recurse -Force .\skill\article-review-skill "$env:USERPROFILE\.codex\skills\article-review-skill"
```

Then ask Codex:

```text
Use $article-review-skill to audit this article and tell me whether it needs edits.
```

## Run The Heuristic Scanner

The scanner uses only the Python standard library.

```bash
python skill/article-review-skill/scripts/audit_article.py examples/sample-article.md --format markdown
```

JSON output is also available:

```bash
python skill/article-review-skill/scripts/audit_article.py examples/sample-article.md --format json
```

The scanner is intentionally heuristic. It does not replace factual review, plagiarism checks, grammar tools, live SERP/PAA research, expert review, accessibility testing, or mobile preview.

## Privacy Posture

This project is designed to be safe for public reuse. Keep it that way:

- Do not add private customer data, credentials, internal strategy, exact confidential metrics, supplier terms, or unreleased roadmap details.
- Keep examples synthetic or clearly anonymized.
- Prefer generic business language over organization-specific instructions.
- Flag regulated or high-stakes claims for human review instead of treating the skill as final approval.

## License

MIT
