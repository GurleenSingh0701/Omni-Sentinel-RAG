To make this look like a high-level engineering project, your README needs to focus on **System Design** rather than just "code." This is what captures the attention of MAANG recruiters.

Here is the finalized, professional `README.md` for **Omni-Sentinel RAG**.

---

# 📄 README.md

# 🛡️ Omni-Sentinel RAG: Agentic Multi-Modal Retrieval System

Omni-Sentinel is a production-grade **Agentic RAG** (Retrieval-Augmented Generation) pipeline designed to solve the "Table-Parsing" failure common in traditional AI architectures. Built with a **State-Driven Graph** approach, it provides a deterministic, reliable, and zero-cost solution for analyzing complex, mixed-format documents.

## 🎯 The Problem it Solves

Standard RAG systems follow a linear path: `Retrieve -> Augment -> Generate`. These systems often fail when:

1. **Context Clutter:** Irrelevant text chunks drown out useful data.
2. **Table Blindness:** Vector similarity search struggles to retrieve meaningful data from structured grids/tables.
3. **High Latency/Cost:** Constant reliance on external APIs like OpenAI.

**Omni-Sentinel** introduces an **Agentic Router** that analyzes user intent to dynamically switch between specialized retrieval paths.

---

## 🏗️ System Architecture

The project is architected as a **Directed Acyclic Graph (DAG)** using **LangGraph**. This allows the system to maintain "state" and make logical decisions before generating a response.

### The Workflow:

1. **Semantic Router:** Analyzes the query to determine if the user needs *qualitative* (textual) or *quantitative* (tabular) information.
2. **Specialized Nodes:**
* **Vector Path:** Conducts semantic similarity search for broad, descriptive answers.
* **Table Path:** Triggers structured data extraction to handle numerical queries and comparisons with high precision.


3. **Synthesis:** A final LLM node aggregates the context from the chosen path to generate a grounded, hallucination-free response.

---

## 🛠️ Tech Stack (The "Modern AI" Stack)

* **Orchestration:** [LangGraph](https://www.langchain.com/langgraph) (For stateful agent control)
* **Intelligence:** [Ollama](https://ollama.com/) (Running Llama 3 locally)
* **Package Management:** [uv](https://docs.astral.sh/uv/) (High-performance Python dependency resolution)
* **Embeddings:** `nomic-embed-text` (Local, high-dimensional vectorization)
* **Infrastructure:** 100% Local / Zero-Cost / Private

---

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have **Ollama** installed and running. Pull the required models:

```bash
ollama pull llama3
ollama pull nomic-embed-text

```

### 2. Installation

This project uses `uv` for lightning-fast setup.

```bash
# Clone the repository
git clone https://github.com/yourusername/omni-sentinel-rag
cd omni_sentinel_rag

# Run the project (uv will auto-install dependencies)
uv run app.py

```

---

## 📊 Performance & Testing

The system was validated against two distinct query types to prove the routing logic:

| Query Type | Input Example | Routed Path | Result |
| --- | --- | --- | --- |
| **Qualitative** | "What is Omni-Sentinel?" | `vector_path` | Semantic Description |
| **Quantitative** | "What was the Q4 revenue?" | `table_path` | Precise Tabular Data |

---

## 💼 Why this is "MAANG-Level"

* **Modular Design:** Separates retrieval logic from generation, allowing for easy scaling (e.g., adding a SQL or Web Search node).
* **Cost Optimization:** Demonstrates ability to architect enterprise solutions that bypass expensive token costs.
* **Deterministic Logic:** Uses a Graph-State approach, ensuring the agent doesn't "get lost" in a loop, a common failure in autonomous agents.
---