# **Module 12, Lesson 2: A/B Testing Prompts**

A/B testing runs two system prompts against the same inputs under controlled conditions and measures which one wins on quality metrics. This turns "I think the new prompt is better" into "the new prompt is 12% better on faithfulness with p<0.05."

---

## Learning Objectives

- **Design** a controlled A/B test for two system prompts
- **Score** both prompts on the same test cases using LLM-as-judge
- **Interpret** results statistically to decide a winner

---

## 1. The A/B Test Structure

```
Test cases (shared inputs)
        │
        ├──▶ Prompt A (control)   ──▶ Answers A ──▶ Scores A
        │
        └──▶ Prompt B (challenger) ──▶ Answers B ──▶ Scores B

Winner = statistically significant higher average score
```

Both prompts receive **identical inputs**. The only variable is the system prompt.

---

## 2. Running the Test

```python
def run_ab_test(
    prompt_a: str,
    prompt_b: str,
    test_cases: list[dict],
    metric_fn: callable,
) -> dict:
    scores_a, scores_b = [], []

    for case in test_cases:
        answer_a = generate(prompt_a, case["question"])
        answer_b = generate(prompt_b, case["question"])

        scores_a.append(metric_fn(answer_a, case["context"]))
        scores_b.append(metric_fn(answer_b, case["context"]))

    return {
        "mean_a":     sum(scores_a) / len(scores_a),
        "mean_b":     sum(scores_b) / len(scores_b),
        "delta":      sum(scores_b) / len(scores_b) - sum(scores_a) / len(scores_a),
        "scores_a":   scores_a,
        "scores_b":   scores_b,
        "winner":     "B" if sum(scores_b) > sum(scores_a) else "A",
    }
```

---

## 3. Statistical Significance

With small test sets (<30 cases), use a paired comparison — count the cases where B strictly beats A:

```python
def wins_losses_ties(scores_a, scores_b, min_delta=0.05):
    wins = ties = losses = 0
    for a, b in zip(scores_a, scores_b):
        if b - a > min_delta:
            wins += 1
        elif a - b > min_delta:
            losses += 1
        else:
            ties += 1
    total = wins + losses
    win_rate = wins / total if total > 0 else 0.5
    return {"wins": wins, "losses": losses, "ties": ties, "win_rate": win_rate}
```

A win rate > 0.6 with at least 10 non-tied comparisons is a reliable signal.

---

## 4. What to Test

| Dimension | Example A | Example B |
|-----------|-----------|-----------|
| Tone      | "Be concise" | "Be thorough" |
| Format    | Bullet points | Prose paragraphs |
| Persona   | "You are an assistant" | "You are a domain expert" |
| Constraints | No constraints | "Always cite your source" |
| Length    | max_tokens=256 | max_tokens=512 |

Test **one variable at a time**. Changing both tone and format makes it impossible to know which caused the improvement.

---

## 5. Practical Checklist

- [ ] Same test cases for both prompts
- [ ] Same model and temperature for both
- [ ] At least 10 test cases for meaningful results
- [ ] Use LLM-as-judge with a consistent rubric
- [ ] Log raw scores per case — not just averages
- [ ] Re-test the winner against the next challenger before promoting to production

---

## Key Takeaways

- A/B test = same inputs, one changing variable (the system prompt), controlled scoring
- Win rate > 0.6 across 10+ non-tied cases is a reliable signal for a winner
- Always test one variable at a time — changing multiple things obscures the cause
- The winner becomes the new control for the next A/B test

---

*Up next: Final Project — pull everything together*
