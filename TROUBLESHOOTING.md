# Troubleshooting Guide

Solutions to the most common errors when running this course's code.

---

## Error: `ModuleNotFoundError: No module named 'anthropic'`

**Cause:** The virtual environment is not activated, or you haven't installed dependencies.

**Fix:**
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

## Error: `AuthenticationError: invalid x-api-key`

**Cause:** Your API key is missing, wrong, or the `.env` file isn't set up.

**Fix:**
```bash
# Check that .env exists
ls -la .env           # macOS/Linux
dir .env              # Windows

# If it doesn't exist, create it from the template
cp .env.example .env

# Open .env and make sure it looks like:
# ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY
```

Make sure there are **no spaces** around the `=` sign, and your key starts with `sk-ant-`.

---

## Error: `RateLimitError: 429 Too Many Requests`

**Cause:** You've sent too many requests too quickly, or your account has hit the free tier limit.

**Fix:**
```bash
# Wait 60 seconds and try again — rate limits reset per minute
# If it keeps happening, you've hit your monthly free limit
# Add $5 credit at: https://console.anthropic.com/billing
```

For the lessons that make many calls (Module 6 evaluation, Module 9 batch), wait a minute between runs.

---

## Error: `ConnectionError` or `APIConnectionError`

**Cause:** No internet connection, or Anthropic's API is temporarily down.

**Fix:**
```bash
# Check your internet works
curl https://api.anthropic.com/v1/messages -I
# Should return HTTP 200 or 401, not "connection refused"

# Check Anthropic's status page
# https://status.anthropic.com
```

---

## Error: `ModuleNotFoundError: No module named 'chromadb'`

**Cause:** ChromaDB wasn't installed, or the venv isn't active.

**Fix:**
```bash
pip install chromadb
# Then run again — first run downloads a ~90 MB model file, takes 1-3 min
```

---

## First run takes forever (downloading a model)

**Normal behaviour.** The first time you run any RAG lesson, `sentence-transformers` downloads the embedding model (`all-MiniLM-L6-v2`, ~90 MB). This happens once and is cached.

```
# You'll see something like:
Downloading: 100%|████████| 90.9M/90.9M [01:23<00:00]
```

Just wait — subsequent runs start instantly.

---

## Error: `FileNotFoundError: [Errno 2] No such file or directory: '.env'`

**Cause:** You forgot to copy `.env.example` to `.env`.

**Fix:**
```bash
cp .env.example .env
# Then open .env and add your API key
```

---

## Code runs but output looks wrong / empty

**Common causes:**

1. **API key is a placeholder** — open `.env` and check the key starts with `sk-ant-`
2. **Wrong Python version** — run `python3 --version`, must be 3.10+
3. **Wrong directory** — make sure you're running from the repo root:
   ```bash
   ls           # should show: code/ Lessons/ solutions/ requirements.txt etc.
   ```

---

## Error: `KeyError: 'ANTHROPIC_API_KEY'` or `None`

**Cause:** `load_dotenv()` didn't find your `.env` file, usually because you're running from the wrong directory.

**Fix:**
```bash
# Always run code from the repo root, not from inside a subdirectory
cd path/to/context-engineering   # go to the root
python3 code/module1/lesson1_context_demo.py
```

---

## `pip install -r requirements.txt` fails

**Fix - try upgrading pip first:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Fix - if a specific package fails:**
```bash
# Install just the core packages needed for Module 1
pip install anthropic python-dotenv rich
```

---

## Windows: `'python3' is not recognized`

Windows uses `python` not `python3`. Replace every `python3` with `python`:

```bash
python -m venv venv
python code/module1/lesson1_context_demo.py
python -m pytest tests/
```

---

## Still stuck?

1. Check the [GitHub Issues](https://github.com/anas4140/context-engineering/issues) — your error may already be reported
2. Open a new issue with: the exact error message, which lesson you're running, your OS, and your Python version
