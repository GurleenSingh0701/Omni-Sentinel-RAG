Omni-Sentinel RAGAn Agentic, Zero-Cost Retrieval System for Structured & Unstructured DataOmni-Sentinel is a production-ready Agentic RAG (Retrieval-Augmented Generation) pipeline designed to bridge the gap between semantic text search and structured data analysis. Built on a Directed Acyclic Graph (DAG) architecture, it ensures that your AI always uses the right tool for the job.🏗️ System ArchitectureOmni-Sentinel uses an Agentic Router to classify user intent before initiating retrieval. This prevents "context clutter" and ensures high-fidelity responses for both descriptive and numerical queries.High-Level WorkflowCode snippetgraph TD
    User([User Query]) --> Router{Semantic Router}
    
    subgraph "Decision Logic"
    Router -- "Descriptive/General" --> VectorNode[Vector Search Node]
    Router -- "Numerical/Tabular" --> TableNode[Tabular Analysis Node]
    end
    
    VectorNode --> Generator[Final LLM Synthesis]
    TableNode --> Generator
    Generator --> Output([Refined Response])

    style Router fill:#f9f,stroke:#333,stroke-width:2px
    style VectorNode fill:#bbf,stroke:#333
    style TableNode fill:#bfb,stroke:#333
    style Generator fill:#fbb,stroke:#333
🌟 Key Technical FeaturesAgentic Orchestration: Powered by LangGraph, the system manages state transitions deterministically, moving beyond brittle linear chains.Local-First (Zero Cost): Leverages Ollama (Llama 3) and nomic-embed-text for 100% private, free inference—no OpenAI/Pinecone credits required.Hybrid Retrieval: Automatically switches between specialized nodes:Vector Node: Handles high-dimensional semantic search for general documentation.Table Node: Extracts and parses Markdown tables to prevent numerical hallucinations.High-Performance Infrastructure: Managed with uv, achieving 10x faster environment resolution and reproducible builds.🛠️ Tech StackComponentTechnologyLanguagePython 3.12OrchestrationLangGraphEnvironmentuvLocal LLMOllamaTracingConsole-based State Logging🚀 Getting Started1. PrerequisitesInstall Ollama and uv. Then pull the models:Bashollama pull llama3
ollama pull nomic-embed-text
2. Installation & ExecutionBash# Clone the repo
git clone https://github.com/yourusername/omni-sentinel-rag
cd omni-sentinel-rag

# Run the system (uv auto-installs deps)
uv run app.py
💼 Business Impact & Use CasesFinancial Analysis: Seamlessly switches to table-parsing mode for comparing quarterly revenue reports.Technical Support: Retrieves descriptive troubleshooting steps while maintaining accuracy for hardware specification tables.Data Privacy: 100% local execution makes it ideal for handling sensitive enterprise data without cloud exposure