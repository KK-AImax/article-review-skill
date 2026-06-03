---
name: article-review-skill
description: Review article drafts for SEO, GEO/AI-search readiness, E-E-A-T, goal alignment, publishing quality, and privacy-safe sharing. Use when asked to audit, score, optimize, refresh, or decide whether to publish Markdown, HTML, text articles, blog posts, guides, FAQ pages, comparison pages, product-support content, documentation pages, or public-facing drafts.
---

# Article Review Skill

## Overview

Use this skill to decide whether an article draft is publish-ready, needs optimization, needs revision, or should be held for risk review. Base the review on search intent, AI-search extractability, editorial quality, evidence, goal alignment, publishing details, and privacy safety.

## Quick Workflow

1. Identify the draft type: informational guide, comparison, buying guide, how-to, FAQ, documentation page, product-support article, landing copy, or scenario recommendation.
2. Gather available context: target query or topic, audience, market, conversion or reader goal, publishing platform, links, meta title, meta description, URL handle, image alt text, and any privacy constraints.
3. If the input is a local Markdown, HTML, or text file, run the quick scanner:

   ```bash
   python <skill-dir>/scripts/audit_article.py <article-path> --format markdown
   ```

4. Review the article against the core checks below. Load `references/review-standards.md` when detailed criteria, examples, or scoring guidance are needed.
5. Return the verdict first, followed by the highest-impact fixes and concrete rewrite guidance.

## Default Assumptions

- Treat the draft as public-facing unless the user says it is internal.
- Infer the audience and goal from the article when they are not provided, but state the assumption.
- Do not claim to have run live SERP, plagiarism, grammar, AI-detection, accessibility, or mobile-preview tools unless those results are provided or actually run.
- Do not invent facts, citations, product specifications, prices, legal rules, medical claims, safety claims, or performance claims.
- Flag regulated, legal, medical, financial, safety, warranty, or compliance claims for human review.
- Respond in the user's language unless they request otherwise.

## Verdict Levels

- **Publish-ready**: No hard-stop issues; score is usually 85+; only minor polish remains.
- **Needs optimization**: Score is usually 65-84; the article is usable but misses important SEO, GEO, evidence, FAQ, linking, or publishing opportunities.
- **Needs revision before publishing**: Score is usually 45-64; the draft has weak intent match, structure, evidence, readability, conversion path, or privacy controls.
- **Hold**: Score is below 45 or the draft has serious factual, originality, privacy, legal, medical, safety, compliance, or unsupported-claim risk.

## Core Checks

| Area | What To Check |
|---|---|
| Intent and opening answer | The first 100 words directly answer the title, query, or reader task. Remove generic filler introductions. |
| SEO and GEO structure | Use real H2/H3 headings, question-led sections, extractable definitions, comparison/spec tables, step lists, and at least 3 FAQ/PAA-style questions when relevant. |
| Evidence and E-E-A-T | Include precise data, firsthand context, examples, credible sourcing, clear limitations, and human review flags for claims that require verification. |
| Goal alignment | Connect reader pain points to the next useful action: related article, product, documentation, support path, template, checklist, or decision aid. |
| Readability | Avoid long text walls, AI cliches, vague claims, repeated points, passive overuse, and mobile-hostile tables. |
| Publishing readiness | Check H1, URL handle, meta title, meta description, image alt text, link anchors, table responsiveness, and final preview risks. |
| Privacy and safety | Remove private customer data, unreleased strategy, confidential metrics, credentials, internal plans, sensitive personal data, or overly specific internal direction. |

## Scoring

When a score helps the user decide, score out of 100:

| Dimension | Weight |
|---|---:|
| Intent match and direct answer | 15 |
| SEO/GEO structure and AI readability | 20 |
| Evidence, E-E-A-T, and factual support | 20 |
| Goal alignment and useful next actions | 15 |
| Readability and editorial polish | 10 |
| Publishing details | 10 |
| Privacy, originality, and safety risk | 10 |

Use the scanner score as a heuristic signal only. Adjust the final score based on the full human-readable draft, provided business context, and claim risk.

## Output Format

For full audits, use this structure:

```markdown
**Verdict**
Decision: Publish-ready / Needs optimization / Needs revision before publishing / Hold
Score: xx/100
Needs edits: Yes/No
Top reason: one sentence

**Priority Fixes**
| Priority | Issue | Evidence | Why It Matters | Exact Fix |
|---|---|---|---|---|

**Optimization Plan**
1. ...
2. ...
3. ...

**Suggested Rewrites**
- H1:
- Opening answer:
- H2/H3 structure:
- Table to add:
- Links or next actions:
- FAQ/PAA:
- Meta title:
- Meta description:
- URL handle:
- Image alt examples:

**Final Checklist**
- ...
```

For short audits, collapse the template into a concise verdict plus 3-7 prioritized actions.

## Revision Guidance

Make fixes concrete. Prefer exact suggested headings, table columns, FAQ questions, link anchor examples, meta text, and opening paragraphs over generic advice. When article text is available, quote only short snippets and provide edited versions. When context is missing, state the assumption and give adaptable recommendations.
