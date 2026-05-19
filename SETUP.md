# Getting Started — Step-by-Step Setup Guide

This guide walks you through everything you need to run the course code from scratch. Follow every step in order.

---

## Step 1: Check Your Python Version

You need **Python 3.10 or higher**.

```bash
python3 --version
# Should show: Python 3.10.x, 3.11.x, 3.12.x, or 3.13.x
```

If you see Python 3.9 or lower, [download the latest Python](https://www.python.org/downloads/).

---

## Step 2: Clone the Repository

```bash
git clone https://github.com/anas4140/context-engineering.git
cd context-engineering
```

---

## Step 3: Create a Virtual Environment

A virtual environment keeps this project's packages separate from everything else on your computer.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it — pick the command for your OS:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows (Command Prompt)
venv/Scripts/Activate.ps1       # Windows (PowerShell)
```

You'll know it's active when your terminal prompt shows `(venv)` at the start.

> **Important**: You must activate the venv every time you open a new terminal window.

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs ~15 packages. The first time it may take 2–5 minutes.

> **Slow download?** `sentence-transformers` downloads a ~90 MB model file on first use — that's normal. It caches locally after the first download.

---

## Step 5: Get an Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for a free account
3. Click **API Keys** in the left sidebar
4. Click **Create Key** → give it a name → copy the key (starts with `sk-ant-`)

> **Free tier**: New accounts get $5 of free credits — enough to run every lesson in this course.

---

## Step 6: Add Your API Key

```bash
cp .env.example .env
```

Open the `.env` file in your editor and replace `your_api_key_here` with your key:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

> **Security**: The `.env` file is in `.gitignore` — it will never be committed to git. Never share your API key publicly.

---

## Step 7: Verify Your Setup

Run this one-liner to confirm everything works:

```bash
python3 -c "
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()
client = Anthropic()
r = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=32, messages=[{'role':'user','content':'Say: Setup complete!'}])
print(r.content[0].text)
"
```

Expected output:
```
Setup complete!
```

If you see that, you're ready. Start with Lesson 1:

```bash
python3 code/module1/lesson1_context_demo.py
```

---

## Something Wrong? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Quick Reference: Commands You'll Use Every Session

```bash
# Activate the virtual environment (do this first, every time)
source venv/bin/activate         # macOS/Linux
venv\Scripts\activate            # Windows

# Run a lesson
python3 code/module1/lesson1_context_demo.py

# Run the final project
python3 final_project/research_assistant.py

# Run the test suite
python3 -m pytest tests/

# Deactivate when done
deactivate
```

---

## Windows Users: Common Differences

| macOS/Linux | Windows |
|---|---|
| `python3` | `python` |
| `source venv/bin/activate` | `venv\Scripts\activate` |
| `/` in paths | `\` in paths |
| `touch .env` | `copy .env.example .env` |
