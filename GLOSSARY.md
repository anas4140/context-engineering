# Glossary

> Core terms used throughout the course. Lessons link here on first use of each term.

---

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

**Embedding**
A vector (list of numbers) that represents the semantic meaning of a piece of text. Similar texts have embeddings that are "close" to each other in vector space. Embeddings enable similarity search in RAG systems.

**Embedding Model**
A specialised model that converts text into embeddings. This course uses `sentence-transformers/all-MiniLM-L6-v2`, a small, fast English embedding model that runs locally.

## F

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
