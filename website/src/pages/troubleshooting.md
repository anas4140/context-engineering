---
title: Troubleshooting
description: Solutions to the most common errors when running the course code.
---

# Troubleshooting Guide

Solutions to the most common errors. Find your error message below.

---

## `ModuleNotFoundError: No module named 'anthropic'`

**Cause:** The virtual environment is not activated, or dependencies haven't been installed.

```bash
# Step 1: Activate your virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Step 2: Install all dependencies
pip install -r requirements.txt

# Step 3: Try again
python3 code/module1/lesson1_context_demo.py
```

---

## `AuthenticationError: invalid x-api-key`

**Cause:** Your API key is missing, wrong, or the `.env` file isn't set up.

```bash
# Check that .env exists
ls -la .env           # macOS/Linux
dir .env              # Windows

# If it doesn't exist, create it from the template
cp .env.example .env
# Then open .env and add your real key
```

Make sure there are **no spaces** around the `=` sign, and your key starts with `sk-ant-`.

---

## `RateLimitError: 429 Too Many Requests`

**Cause:** You've sent too many requests too quickly, or hit the free tier limit.

```bash
# Wait 60 seconds and try again — rate limits reset per minute
# If it keeps happening, add $5 credit at: https://console.anthropic.com/billing
```

For lessons that make many calls (Module 6 eval, Module 9 batch), wait a minute between runs.

---

## `ConnectionError` or `APIConnectionError`

**Cause:** No internet connection, or Anthropic's API is temporarily down.

```bash
# Check your internet works
curl https://api.anthropic.com/v1/messages -I
# Should return HTTP 200 or 401, not "connection refused"

# Check Anthropic's status page
# https://status.anthropic.com
```

---

## `ModuleNotFoundError: No module named 'chromadb'`

**Cause:** ChromaDB wasn't installed, or the venv isn't active.

```bash
pip install chromadb
# First run downloads a ~90 MB model file — takes 1-3 min, then caches
```

---

## First run is very slow (model downloading)

**Normal behaviour.** The first time you run any RAG lesson, `sentence-transformers` downloads the embedding model (`all-MiniLM-L6-v2`, ~90 MB). This happens once and is cached.

```
Downloading: 100%|████████| 90.9M/90.9M [01:23<00:00]
```

Just wait — subsequent runs start instantly.

---

## `FileNotFoundError: [Errno 2] No such file or directory: '.env'`

```bash
cp .env.example .env
# Then open .env and add your API key
```

---

## Code runs but output looks wrong / empty

1. **API key is a placeholder** — open `.env` and check the key starts with `sk-ant-`
2. **Wrong Python version** — run `python3 --version`, must be 3.10+
3. **Wrong directory** — run commands from the repo root:
   ```bash
   ls    # should show: code/ Lessons/ solutions/ requirements.txt
   ```

---

## `KeyError: 'ANTHROPIC_API_KEY'`

**Cause:** `load_dotenv()` didn't find your `.env` file. Run from the repo root:

```bash
cd path/to/context-engineering   # go to the root
python3 code/module1/lesson1_context_demo.py
```

---

## `pip install -r requirements.txt` fails

```bash
# Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Windows: `'python3' is not recognized`

Replace every `python3` with `python`:

```bash
python -m venv venv
python code/module1/lesson1_context_demo.py
python -m pytest tests/
```

---

## Still stuck?

1. Check the [GitHub Issues](https://github.com/anas4140/context-engineering/issues) — your error may already be reported
2. Open a new issue with: the exact error, which lesson, your OS, and Python version

---

*Back to [Setup Guide](/context-engineering/setup)*
