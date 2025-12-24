# Omni-Sentinel RAG: Agentic Multi-Modal Retrieval System

Omni-Sentinel is a high-performance, **zero-cost** Agentic RAG system built using **LangGraph** and **Ollama**. Unlike standard RAG pipelines that suffer from "Table Failure," Omni-Sentinel uses a **Semantic Router** to dynamically switch between unstructured vector search and structured tabular analysis.

### 🚀 Key Features
- **Agentic Orchestration:** Uses a State Machine (LangGraph) to handle complex query branching.
- **Local-First (Zero Cost):** Powered by Ollama (Llama3) and `uv` for lightning-fast, private inference.
- **Hybrid Retrieval:** Automatically detects if a query requires semantic context or structured numerical data (Tables).
- **High-Performance Tooling:** Managed with `uv` for 10x faster dependency resolution than pip.

### 🛠️ Tech Stack
- **Orchestration:** LangGraph
- **LLM / Embeddings:** Ollama (Llama3, Nomic-Embed)
- **Environment:** uv (Python 3.12)
- **Framework:** LangChain

### 🏁 Quick Start
1. **Pull Models:** `ollama pull llama3`
2. **Install Deps:** `uv run app.py`

### 🧠 System Architecture