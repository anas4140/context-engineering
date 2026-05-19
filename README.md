# Context Engineering for AI — Complete Course

> A free, open-source course on building robust, reliable, and efficient context-aware AI applications.  
> Every lesson includes **runnable Python code**, solution notebooks, and hands-on tasks with answer keys.

---

## What You Will Build

By the end of this course you will have built:

- A **RAG pipeline** that answers questions from your own documents
- A **function-calling agent** that uses real tools (web search, calculators)
- A **security-hardened prompt** resilient to injection attacks
- A complete **AI Research Assistant** (final project) with citations, evaluation, and structured output

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | `python --version` to check |
| Anthropic API key | [Get one free at console.anthropic.com](https://console.anthropic.com) |
| ~500 MB disk space | For ChromaDB and model weights |

No prior AI or ML experience required. Code examples are heavily commented for beginners.

---

## Quick Start

> **First time?** Follow the detailed [SETUP.md](SETUP.md) guide — it covers Python version, virtual environments, and getting your API key step by step.  
> **Hitting errors?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the 10 most common problems and fixes.

```bash
# 1. Clone the repo
git clone https://github.com/anas4140/context-engineering.git
cd context-engineering

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Open .env and paste your ANTHROPIC_API_KEY

# 5. Run your first example
python code/module1/lesson1_context_demo.py
```

---

## Course Structure

| Module | Topic | Lessons | Code |
|---|---|---|---|
| [Module 1](Lessons/Module1/) | Foundations of Context Engineering | 3 | [code/module1/](code/module1/) |
| [Module 2](Lessons/Module2/) | Advanced Prompting Techniques | 3 | [code/module2/](code/module2/) |
| [Module 3](Lessons/Module3/) | Retrieval-Augmented Generation (RAG) + Hybrid Search | 5 | [code/module3/](code/module3/) |
| [Module 4](Lessons/Module4/) | Optimising the Context Window | 3 | [code/module4/](code/module4/) |
| [Module 5](Lessons/Module5/) | From RAG to Agents + Structured Outputs | 4 | [code/module5/](code/module5/) |
| [Module 6](Lessons/Module6/) | Evaluation, Testing & Security | 3 | [code/module6/](code/module6/) |
| [Module 7](Lessons/Module7/) | The Future of Context (CWA) + Files API | 5 | [code/module7/](code/module7/) |
| [Module 8](Lessons/Module8/) | Extended Thinking | 2 | [code/module8/](code/module8/) |
| [Module 9](Lessons/Module9/) | Production at Scale (Batch API, Streaming, Rate Limits) | 3 | [code/module9/](code/module9/) |
| [Module 10](Lessons/Module10/) | Model Context Protocol (MCP) | 2 | [code/module10/](code/module10/) |
| [Module 11](Lessons/Module11/) | Async & Concurrent Patterns | 2 | [code/module11/](code/module11/) |
| [Module 12](Lessons/Module12/) | Prompt Versioning & A/B Testing | 2 | [code/module12/](code/module12/) |

**Final Project:** [FINAL_PROJECT.md](FINAL_PROJECT.md) — Build a complete AI Research Assistant  
**Glossary:** [GLOSSARY.md](GLOSSARY.md)  
**Solutions:** [solutions/](solutions/) — Answer keys for every hands-on task

---

## Estimated Time

| Level | Time |
|---|---|
| Skim (read lessons only) | ~8 hours |
| Standard (lessons + run code) | ~24 hours |
| Deep (lessons + code + tasks) | ~45 hours |

---

## Repo Layout

```
context-engineering/
├── Lessons/              # Markdown lesson files (theory + explanations)
│   ├── Module1/ … Module10/
├── code/                 # Runnable Python examples (one file per lesson)
│   ├── module1/ … module10/
├── solutions/            # Answer keys for every hands-on task
│   ├── module1/ … module10/
├── final_project/        # Capstone — full AI Research Assistant
│   └── research_assistant.py
├── notebooks/            # Jupyter notebooks (optional, mirrors code/)
├── config.py             # Shared model names and constants
├── requirements.txt
├── .env.example
├── FINAL_PROJECT.md
├── GLOSSARY.md
└── CONTRIBUTING.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs are welcome — especially new code examples, additional language translations, and solution notebooks.

---

## License

MIT — free to use, share, and build on.
