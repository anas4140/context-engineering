# Contributing to Context Engineering for AI

Thank you for helping improve this course! Here's how to contribute.

---

## Types of Contributions Welcome

- **Bug fixes** — broken code, typos, incorrect explanations
- **New code examples** — additional demonstrations of lesson concepts
- **Solution notebooks** — Jupyter notebooks for hands-on tasks
- **Translations** — lessons in languages other than English
- **New lessons** — additional content that fits the course arc

---

## How to Contribute

1. **Fork** the repo and create a branch: `git checkout -b fix/module3-rag-chunking`
2. **Make your changes** following the style guide below
3. **Test your code**: every Python file must run without errors
4. **Open a PR** with a clear description of what changed and why

---

## Code Style Guide

- **Python 3.10+** only
- **Heavily commented** — this is a teaching repo, not a production codebase
- Every runnable file must have a `if __name__ == "__main__":` block
- Use `python-dotenv` for API keys — never hardcode them
- Keep each file focused on one concept (one file per lesson)

---

## Lesson File Format

Each lesson Markdown file should have:

1. Module + lesson title as `# **Module X, Lesson Y: Title**`
2. "Building on What We've Learned" intro paragraph
3. Learning Objectives (bulleted, using **Define / Explain / Apply / Build**)
4. Numbered concept sections with code examples
5. Key Takeaways (3–5 bullets)
6. Hands-On Task with a clear deliverable

---

## Issues

Use these labels when opening issues:
- `bug` — something broken
- `enhancement` — new feature or content
- `good first issue` — suitable for first-time contributors
- `help wanted` — needs a contributor

---

## Code of Conduct

Be kind, be constructive. This is a learning resource — all skill levels are welcome.
