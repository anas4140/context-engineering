# **Module 1, Lesson 1: What is Context and Why is it Critical?**

Welcome to Context Engineering for AI. This lesson establishes the single most important concept in the entire course: **context is everything**.

---

## Learning Objectives

- **Define** context in the context of Large Language Models
- **Explain** why context quality directly determines output quality
- **Apply** the GIGO principle to AI system design
- **Build** a working demo comparing poor vs rich context ([code/module1/lesson1_context_demo.py](../../code/module1/lesson1_context_demo.py))

---

## 1. What is Context?

When you send a message to an LLM, the model has no memory, no ability to look things up, and no awareness of who you are or what you need. All it has is the text you send it in that single request — that text is the **context window**.

Context engineering is the discipline of deciding **what to put in that window**.

Think of it like this: if you hired a brilliant consultant but only gave them one minute to read a brief before answering your question, the quality of that brief determines the quality of their answer. The consultant is Claude. The brief is your context.

---

## 2. The Four Types of Context

Every piece of information in a context window falls into one of four categories:

| Type | What it provides | Example |
|---|---|---|
| **Instructions** | Tells the model WHO it is and HOW to behave | System prompt, persona |
| **Memory** | Tells the model WHAT has already happened | Chat history, summaries |
| **Knowledge** | Tells the model WHAT is factually true | Retrieved docs, product manuals |
| **Tools** | Tells the model WHAT actions it can take | Function definitions |

The entire course teaches you to master each of these four types.

---

## 3. GIGO — Amplified

In traditional software, "Garbage In, Garbage Out" means bad input produces bad output. With LLMs, the effect is amplified: a model as capable as Claude will construct a **confidently wrong, well-written** answer from bad context. It doesn't tell you the context was inadequate — it just does its best with what it has.

**Poor context example:**

```
User: "It's not working, what do I do?"
Assistant: "I'm sorry to hear that. Could you tell me more about what isn't working?"
```

The model has no idea what product, what problem, or what the user has already tried. The response is technically correct but useless.

**Rich context example (same question):**

With a system prompt identifying the assistant as ACME support, conversation history establishing the user has a SmartFridge Series A, and a retrieved manual snippet about the Child Lock feature, Claude can respond:

```
It sounds like the Child Lock feature may be activated. 
Press and hold the 'Lock' button for 3 seconds — a green light 
will confirm it's deactivated. (Source: SmartFridge Series A Manual, p.12)
```

Same model. Same question. Completely different result.

---

## 4. Bias and the System Prompt as a Control Mechanism

The system prompt isn't just for persona — it's a **control mechanism** for model behaviour. This is demonstrated clearly in the bias mitigation demo in the code:

Without guidance, a model asked to write a job description may use exclusionary language ("rockstar developer", gendered pronouns). With an engineered system prompt that explicitly requires gender-neutral language and specific terminology rules, the same model produces an inclusive, professional result.

This isn't a trick — it's deliberate context design.

---

## Key Takeaways

- Context is the only information an LLM has when generating a response
- Context quality determines output quality — more reliably than model size
- The four context types are: Instructions, Memory, Knowledge, Tools
- The system prompt is a control mechanism, not just a greeting
- GIGO is amplified in LLMs — the model will be confidently wrong, not obviously confused

---

## Hands-On Task

Run the demo:

```bash
python code/module1/lesson1_context_demo.py
```

Then answer these questions:

1. In the "poor context" response, what specific information was missing that caused the vague answer?
2. Look at the `call_with_rich_context()` function. Which of the four context types (Instructions / Memory / Knowledge / Tools) does each parameter map to?
3. Modify the `inclusive_system_prompt` in `demo_bias_mitigation()` to add one more rule. What effect does it have?

---

*Next: [Lesson 2 — The Economics of Context: Tokens and Cost](Lesson2_Economics.md)*
