# **Module 2, Lesson 1: A Taxonomy of Prompting Techniques**

Building on Module 1's four principles, this lesson maps out the landscape of prompting techniques — giving you a vocabulary and decision framework for choosing the right technique for any task.

---

## Learning Objectives

- **Define** zero-shot, few-shot, chain-of-thought, and role prompting
- **Explain** when each technique is appropriate
- **Apply** the technique selection framework to new tasks

---

## 1. The Technique Landscape

| Technique | When to use | Complexity | Token cost |
|---|---|---|---|
| Zero-shot | Simple, common tasks | Low | Low |
| Few-shot | Tasks requiring specific format | Medium | Medium |
| Chain-of-Thought | Reasoning, maths, multi-step logic | Medium | High |
| Role prompting | Domain expert knowledge needed | Low | Low |
| XML-structured | Mixed content types, injection risk | Medium | Low |
| ReAct | Tasks requiring external tools | High | High |

---

## 2. The Selection Framework

Ask these questions in order:

1. **Is the task simple and common?** → Zero-shot first. If output quality is sufficient, stop.
2. **Does the output need a specific format?** → Add few-shot examples.
3. **Does the task involve reasoning or maths?** → Add "think step by step".
4. **Does the task require domain expertise?** → Add a role via the system prompt.
5. **Is user content mixed with instructions?** → Use XML tags regardless of other choices.
6. **Does the task require external information or actions?** → ReAct with tools (Module 5).

---

## Key Takeaways

- Start with zero-shot and add complexity only when needed
- Few-shot examples teach format; CoT teaches reasoning
- Role prompting improves domain-specific quality
- XML tags belong in any prompt that processes user-provided content

---

*Next: [Lesson 2 — Prompting Techniques in Practice](Lesson2_Prompting_Techniques.md)*
