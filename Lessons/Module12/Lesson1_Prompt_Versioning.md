# **Module 12, Lesson 1: Prompt Versioning**

Prompts are code. They should be versioned, tracked, and rolled back just like any other code asset. This lesson sets up a lightweight prompt registry and shows how to measure quality drift between versions.

---

## Learning Objectives

- **Store** prompt versions with metadata in a structured registry
- **Retrieve** any version by name and tag
- **Detect** quality regressions when a prompt is updated

---

## 1. Why Version Prompts?

| Without versioning | With versioning |
|---|---|
| Edit the prompt, test, forget what changed | Every change is tagged and retrievable |
| Hard to roll back when quality drops | `registry.get("summariser", tag="v1.2")` |
| No way to know which prompt is in production | `registry.get_production("summariser")` |
| Can't measure the effect of a change | Before/after eval on the same test cases |

---

## 2. A Minimal Prompt Registry

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class PromptVersion:
    name:       str
    version:    str
    system:     str
    notes:      str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    production: bool = False

class PromptRegistry:
    def __init__(self):
        self._store: dict[str, list[PromptVersion]] = {}

    def register(self, prompt: PromptVersion):
        self._store.setdefault(prompt.name, []).append(prompt)

    def get(self, name: str, version: str) -> Optional[PromptVersion]:
        for p in self._store.get(name, []):
            if p.version == version:
                return p
        return None

    def get_production(self, name: str) -> Optional[PromptVersion]:
        for p in reversed(self._store.get(name, [])):
            if p.production:
                return p
        return None

    def history(self, name: str) -> list[PromptVersion]:
        return self._store.get(name, [])
```

---

## 3. Quality Gates on Version Promotion

Before marking a new version `production=True`, run it against a test suite and compare:

```python
def promote_if_better(registry, name, candidate_version, threshold=0.05):
    """Only promote if the new version scores ≥ threshold better than current prod."""
    current = registry.get_production(name)
    candidate = registry.get(name, candidate_version)

    current_score   = eval_prompt(current.system,   test_cases)
    candidate_score = eval_prompt(candidate.system, test_cases)

    improvement = candidate_score - current_score
    if improvement >= threshold:
        candidate.production = True
        print(f"Promoted {candidate_version} (+{improvement:.3f})")
    else:
        print(f"Rejected {candidate_version} (delta={improvement:.3f} < {threshold})")
```

---

## 4. Detecting Quality Drift Over Time

Run the same test suite on every version in history to plot quality over time:

```python
scores = {}
for version in registry.history("summariser"):
    scores[version.version] = eval_prompt(version.system, test_cases)

# Plot: version → score reveals when quality degraded
```

---

## Key Takeaways

- A prompt registry is a dict of `name → [PromptVersion]` — simple to implement, invaluable in production
- Tag every version; mark only the production-ready one as `production=True`
- Run eval before every promotion — never push a new prompt without measuring the delta
- Plot version scores over time to catch quality drift early

---

*Next: [Lesson 2 — A/B Testing Prompts](Lesson2_AB_Testing.md)*
