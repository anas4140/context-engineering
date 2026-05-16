# **Module 4, Lesson 1: Context Window Anatomy**

Understanding exactly what occupies the context window — and in what order — is the foundation for optimising it.

---

## Learning Objectives

- **Define** each region of the context window and its purpose
- **Explain** the primacy and recency effects in LLM attention
- **Apply** placement strategy to maximise model attention on critical content

---

## 1. Regions of the Context Window

A fully populated context window looks like this (top to bottom):

```
┌─────────────────────────────────────────┐
│  SYSTEM PROMPT                          │  ← Instructions, rules, persona
│  (Layers 1, 2, 3, 5, 7, 10)            │
├─────────────────────────────────────────┤
│  CONVERSATION HISTORY                   │  ← Past turns (Layer 6)
├─────────────────────────────────────────┤
│  RETRIEVED CONTEXT (RAG)                │  ← Fetched chunks (Layer 8)
├─────────────────────────────────────────┤
│  CURRENT USER MESSAGE                   │  ← Latest query (Layer 11)
└─────────────────────────────────────────┘
```

## 2. Primacy and Recency Effects

LLMs pay the most attention to content at the **beginning** (primacy) and **end** (recency) of the context window. Content buried in the middle is most likely to be ignored — this is called the **lost-in-the-middle problem**.

**Practical implications:**
- Put non-negotiable rules and persona in the system prompt (beginning)
- Put the current query and most relevant retrieved chunk at the very bottom (end)
- Avoid burying critical facts in the middle of a long history

## 3. Placement Strategy by Layer

| Layer | Placement | Reason |
|---|---|---|
| 1-3, 5, 10 (Instructions) | `system` param | Permanent, high priority |
| 7 (Tool definitions) | `tools` param | API handles placement |
| 6 (History) | Early in `messages` | Less critical than current query |
| 8 (RAG results) | Bottom of final user turn | Recency effect |
| 11 (User query) | Very last line | Maximum attention |

---

## Key Takeaways

- The context window has a beginning (system), middle (history), and end (current turn)
- Models pay most attention to the beginning and end — use this deliberately
- RAG results and the user query belong at the bottom for maximum effect
- Long histories push important content into the middle — summarise regularly

---

*Next: [Lesson 2 — Compression Techniques](Lesson2_Compression.md)*
