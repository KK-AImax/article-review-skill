# Contributing

Thanks for improving Article Review Skill.

## Useful Contributions

- Better review heuristics for Markdown, HTML, and plain text
- More precise publishing checks
- Safer privacy and confidential-content detection
- Example drafts and anonymized audit outputs
- Tests for edge cases and multilingual drafts

## Privacy Rules

- Do not commit private customer data, credentials, internal strategy, exact confidential metrics, supplier terms, or unreleased roadmap details.
- Keep examples synthetic or anonymized.
- Generalize organization-specific workflows before opening a pull request.

## Local Checks

Run the script on the sample draft:

```bash
python skill/article-review-skill/scripts/audit_article.py examples/sample-article.md --format markdown
```

Run tests:

```bash
python -m unittest discover -s tests
```
