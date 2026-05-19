# Glossary

> Core terms used throughout the course. Lessons link here on first use of each term.

---

## A

**A/B Testing (Prompts)**
A controlled experiment comparing two system prompts on identical inputs, using LLM-as-judge scoring to determine which wins. The only variable is the system prompt — model, temperature, and test cases are held constant. See: [Module 12](code/module12/lesson2_ab_testing.py).

**AsyncAnthropic**
The async version of the Anthropic Python client. Methods return coroutines (`await`-able) instead of blocking. Used with `asyncio.gather` to fire multiple API calls concurrently. See: [Module 11](code/module11/lesson1_async_basics.py).

## B

**Batch API**
An Anthropic API feature that processes requests asynchronously at 50% lower cost than synchronous calls. Submit a list of requests, poll for completion, then stream results. Ideal for eval runs and dataset annotation. See: [Module 9](code/module9/lesson1_batch_api.py).

**BM25**
A sparse retrieval algorithm that scores documents by term frequency and inverse document frequency. Excels at exact keyword matches that dense embeddings miss. Combined with vector search in hybrid retrieval. See: [Module 3](code/module3/lesson5_hybrid_search.py).

## C

**Chunking**
The process of splitting a large document into smaller pieces (chunks) before embedding them. Chunk size affects retrieval quality — too small loses context, too large wastes tokens. See: [Module 4](Lessons/Module4/).

**ChromaDB**
An open-source, local vector database used in this course to store and search document embeddings. No server or account required. [chromadb.com](https://www.trychroma.com/)

**Context Window**
The total amount of text (measured in tokens) an LLM can "see" at once — including the system prompt, conversation history, retrieved chunks, and tool results. Different models have different context window sizes.

**Context Window Architecture (CWA)**
A framework for organising the 11 types of information that can populate an LLM's context window. Defined in full in [Module 7, Lesson 4](code/module7/lesson4_cwa.py).

**Contextual Compression**
A technique where retrieved document chunks are summarised by the LLM before being placed in the context window, reducing token usage while preserving relevant information. See: [Module 4](code/module4/lesson2_compression.py).

## E

**Extended Thinking**
A Claude feature that allocates a hidden "scratchpad" of reasoning tokens before generating the visible answer. Controlled by `thinking={'type': 'enabled', 'budget_tokens': N}`. Improves accuracy on multi-step problems; response content includes both `thinking` and `text` blocks. See: [Module 8](code/module8/lesson1_extended_thinking.py).

**Embedding**
A vector (list of numbers) that represents the semantic meaning of a piece of text. Similar texts have embeddings that are "close" to each other in vector space. Embeddings enable similarity search in RAG systems.

**Embedding Model**
A specialised model that converts text into embeddings. This course uses `sentence-transformers/all-MiniLM-L6-v2`, a small, fast English embedding model that runs locally.

## F

**Files API**
An Anthropic beta API that lets you upload documents once and reference them by `file_id` in subsequent requests — without resending the bytes. Supports PDF, plain text, HTML, and Markdown. See: [Module 7](code/module7/lesson5_files_api.py).

**Faithfulness**
A RAG evaluation metric. Measures whether every claim in the generated answer is supported by the retrieved context. Score: 0.0 (hallucinated) → 1.0 (fully grounded). See: [Module 6](code/module6/lesson1_evaluation.py).

**Few-shot Prompting**
A prompting technique where you provide 2-5 example input/output pairs before the actual task. Teaches the model the desired output format without fine-tuning. See: [Module 2](code/module2/lesson2_prompting_techniques.py).

**Function Calling**
The ability of an LLM to request the execution of a Python function during a conversation. The model returns a structured JSON argument block; your code executes the function and returns the result. Also called "tool use". See: [Module 5](code/module5/lesson_agent_loop.py).

## G

**Generator**
In a RAG system, the LLM component that reads the retrieved chunks and generates a final answer. Contrast with the Retriever.

**Grounding**
The practice of providing an LLM with factual source documents to base its answers on, reducing hallucination.

## H

**Hybrid Search**
A retrieval strategy that combines dense vector search (semantic similarity) with sparse BM25 keyword search, fusing their ranked lists using Reciprocal Rank Fusion (RRF). Outperforms either method alone on mixed query types. See: [Module 3](code/module3/lesson5_hybrid_search.py).

**Hallucination**
When an LLM generates plausible-sounding but factually incorrect information. The primary motivation for RAG — grounding responses in retrieved facts reduces hallucination.

## J

**JSON Schema**
A standard format for describing the structure of a JSON object. Used to define tool parameters so the LLM knows exactly what arguments a function expects. See: [Module 5](code/module5/lesson_agent_loop.py).

## L

**LLM-as-Judge**
An evaluation technique where a separate LLM call scores the quality of a primary LLM's output. Used in [Module 6](code/module6/lesson1_evaluation.py) to evaluate faithfulness and relevance.

**Long-term Memory**
Persisted facts about a user or domain, learned from past conversations and injected into future context windows. Corresponds to CWA Layer 5.

## P

**Prompt Injection**
An attack where malicious instructions are embedded in user-provided content (e.g. emails, documents) and trick the LLM into following them instead of the developer's intended instructions. Defended against using XML delimiters and hardened system prompts. See: [Module 6](code/module6/lesson1_evaluation.py).

## R

**RAG (Retrieval-Augmented Generation)**
An architecture that enhances LLM responses by first retrieving relevant document chunks from a knowledge base, then using those chunks as context for generation. See: [Module 3](code/module3/lesson1_rag_pipeline.py).

**ReAct (Reason + Act)**
An agentic prompting pattern where the model alternates between reasoning about the next step and taking an action (tool call), then observes the result, until the task is complete. See: [Module 5](code/module5/lesson_agent_loop.py).

**Re-ranking**
A post-retrieval step where retrieved chunks are scored for relevance and reordered so the most relevant chunks appear first. See: [Module 4](code/module4/lesson2_compression.py).

**Retriever**
In a RAG system, the component that searches the vector store and returns relevant chunks. Contrast with the Generator.

## S

**Short-term Memory**
A running summary of the current conversation, injected into the context window to avoid repeating information and manage token limits. Corresponds to CWA Layer 6.

**System Prompt**
Instructions sent to the LLM before any user message. Defines persona, rules, and behaviour. Corresponds to CWA Layers 1-3, 5, 7, and 10.

## T

**Token**
The basic unit of text an LLM processes. Roughly: 1 token ≈ 4 characters ≈ 0.75 words. Context windows, pricing, and rate limits are all measured in tokens.

**Tool**
A Python function that an LLM agent can request to be called. Described to the model using JSON Schema. See: [Module 5](code/module5/lesson_agent_loop.py).

## V

**Vector Store**
A database optimised for storing and searching embeddings using similarity search (e.g. nearest-neighbour search). This course uses ChromaDB. Alternatives: FAISS, Pinecone, Weaviate.

**Vector Search**
Finding the embeddings in a vector store that are most similar to a query embedding. This is how RAG retrieves relevant chunks.

## Z

**Zero-shot Prompting**
Sending a task to the LLM with no examples. The model relies entirely on its training. Contrast with few-shot prompting. See: [Module 2](code/module2/lesson2_prompting_techniques.py).

## M

**MCP (Model Context Protocol)**
An open standard for connecting AI models to external tools and data sources via a client-server architecture. MCP servers expose tools via `list_tools()` and `call_tool()`; clients discover and use tools dynamically. See: [Module 10](code/module10/lesson1_mcp_client.py).

## N

## P

**Prompt Caching**
An Anthropic API feature that stores processed prompt prefixes server-side. Subsequent requests reusing the same prefix pay ~10% of the normal input token price. Enabled by adding `cache_control: {type: ephemeral}` to content blocks. See: [Module 7](Lessons/Module7/Lesson1_Emerging_Patterns.md).

**Prompt Registry**
A versioned store of system prompts with metadata (version tag, notes, production flag). Enables rollback, quality tracking, and gated promotion. See: [Module 12](code/module12/lesson1_prompt_versioning.py).

## R

**RRF (Reciprocal Rank Fusion)**
A score-fusion algorithm for hybrid search. Combines ranked lists from multiple retrievers without normalising their scores: `score = Σ 1/(k + rank)`. Simple, parameter-free, and consistently effective. See: [Module 3](code/module3/lesson5_hybrid_search.py).

## S

**Streaming**
Receiving LLM output token-by-token as it is generated, instead of waiting for the full response. Improves perceived latency. Use `client.messages.stream()` in Python. See: [Module 9](code/module9/lesson2_streaming.py).

**Structured Outputs**
Using `tool_choice: {type: tool, name: "..."}` to force Claude to return a specific JSON schema — always as a `tool_use` block, never raw text. Eliminates fragile string parsing. See: [Module 5](code/module5/lesson4_structured_outputs.py).

## T

**Thinking Budget**
The maximum number of tokens Claude may use for its hidden reasoning scratchpad when extended thinking is enabled. Set via `budget_tokens` in `thinking={...}`. Must be ≥ 1024. See: [Module 8](code/module8/lesson2_thinking_budgets.py).

**TPM (Tokens Per Minute)**
An API rate limit measured in tokens consumed per minute. Relevant when making many large requests. Use `asyncio.Semaphore` or `TokenPacer` to stay within limits. See: [Module 9](code/module9/lesson3_rate_limits.py).
