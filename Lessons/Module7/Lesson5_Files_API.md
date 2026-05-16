# **Module 7, Lesson 5: Files API**

The Files API lets you upload a document once and reference it by ID in any number of subsequent requests — without resending the bytes each time. This is the production pattern for document-heavy RAG pipelines.

---

## Learning Objectives

- **Upload** a file via the Files API and store its ID
- **Reference** an uploaded file in a message
- **Manage** file lifecycle (list, delete) to control storage costs

---

## 1. The Problem with Inline Document Passing

In Module 3 you chunked documents and embedded them in ChromaDB. For PDFs and large text files, you can also pass the raw content inline:

```python
# Fragile — resends the full document on every API call
response = client.messages.create(
    model=MODEL, max_tokens=512,
    messages=[{"role": "user", "content": [
        {"type": "text", "text": document_bytes.decode()},
        {"type": "text", "text": "Summarise this."},
    ]}]
)
```

Problems: high latency, high cost (every call re-bills the document tokens), and file size limits.

---

## 2. Uploading a File

```python
# Upload once — store the ID
with open("research_paper.pdf", "rb") as f:
    file_obj = client.beta.files.upload(
        file=("research_paper.pdf", f, "application/pdf"),
    )

file_id = file_obj.id
print(file_id)   # file_abc123...
```

Supported types: `application/pdf`, `text/plain`, `text/html`, `text/markdown`.

---

## 3. Using the File in a Request

Reference the file by ID — no bytes resent:

```python
response = client.beta.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "file",
                    "file_id": file_id,
                },
                "title": "Research Paper",   # optional — improves citation quality
            },
            {"type": "text", "text": "What are the three main findings of this paper?"},
        ],
    }],
    betas=["files-api-2025-04-14"],
)
print(response.content[0].text)
```

The same `file_id` can be reused across thousands of requests — you only pay the document tokens once per upload.

---

## 4. Multi-Document Queries

Send multiple file IDs in a single request:

```python
response = client.beta.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {"type": "file", "file_id": file_id_1}, "title": "Paper A"},
            {"type": "document", "source": {"type": "file", "file_id": file_id_2}, "title": "Paper B"},
            {"type": "text", "text": "Compare the methodologies of Paper A and Paper B."},
        ],
    }],
    betas=["files-api-2025-04-14"],
)
```

---

## 5. File Management

```python
# List all uploaded files
files = client.beta.files.list()
for f in files.data:
    print(f.id, f.filename, f.size)

# Delete when no longer needed (frees storage quota)
client.beta.files.delete(file_id)
```

---

## 6. Files API vs. ChromaDB RAG

| | ChromaDB RAG | Files API |
|--|--|--|
| Document size | Large (chunked) | Up to API limit per file |
| Retrieval | Semantic search over chunks | Full document per request |
| Re-upload needed | No (persistent store) | No (file_id persists) |
| Token cost per query | Only retrieved chunks | Full document tokens |
| Best for | Large corpora, many docs | Small-medium docs, repeated queries |

Use ChromaDB when you have many large documents and need selective retrieval. Use the Files API when you frequently query the same small set of documents in full.

---

## Key Takeaways

- Upload once with `client.beta.files.upload()`; reference by `file_id` forever after
- Include `betas=["files-api-2025-04-14"]` in `client.beta.messages.create()`
- Multiple files can be included in a single request as `document` content blocks
- Delete files with `client.beta.files.delete()` when done to free storage quota

---

*Up next: Module 8 — Extended Thinking*
