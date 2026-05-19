# **Module 7, Lesson 2: Multimodal Context**

Context windows can now contain images, documents, and audio alongside text. This lesson covers how multimodal inputs change context engineering decisions.

---

## Learning Objectives

- **Explain** how images and PDFs are represented in the context window
- **Apply** multimodal context design to document analysis tasks

---

## 1. Images in the Context Window

Images are passed as base64-encoded data in the messages array. They consume tokens based on their dimensions — a 1024×1024 image costs approximately 1,600 tokens.

**Context engineering considerations:**
- Large images are expensive — resize before sending if the full resolution isn't needed
- Multiple images multiply the token cost — be selective
- Describe what the model should focus on in the image to improve accuracy

```python
messages = [{
    "role": "user",
    "content": [
        {
            "type":   "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img_data}
        },
        {
            "type": "text",
            "text": "Focus on the data in the table in the bottom-right corner."
        }
    ]
}]
```

## 2. PDFs as Context

Claude can receive PDFs directly as document blocks. This is more efficient than extracting text yourself — the model can reference specific pages and understand the document structure.

**When to use PDF context vs RAG:**
- **PDF directly:** Short documents (< 50 pages), single document, one-off analysis
- **RAG pipeline:** Large document collections, repeated queries, need for citations

---

## Key Takeaways

- Images and PDFs are valid context window content — not just text
- Images cost tokens based on dimensions — optimise size before sending
- For large document collections, RAG is more efficient than sending documents directly
- Always tell the model what to focus on in an image for better results

---

*Next: [Lesson 3 — The Future of Context Engineering](Lesson3_Future.md)*

---

## Hands-On Task

```bash
python code/module7/lesson2_multimodal.py
```

1. **Token cost comparison**: Use `estimate_image_tokens()` to compare the cost of a 256×256 image vs a 1920×1080 image. How many times more expensive is the larger one?
2. **Describe + extract**: Send the same image with two different questions: (a) "Describe this image" and (b) "List any text visible in this image." Compare the responses — does Claude behave differently?
3. **Context window impact**: If you have a 200K token window and you want to include 10 images of 512×512 each, how much of the window do they consume? How many tokens are left for text?

---

*Next: [Lesson 3 — Future Patterns](Lesson3_Future.md)*
