from typing import TypedDict, Literal
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

# --- 1. LOCAL MODEL SETUP ---
# Ensure you've run: ollama pull llama3
llm = ChatOllama(model="llama3.2", temperature=0)

# --- 2. THE STATE MACHINE DEFINITION ---
class AgentState(TypedDict):
    query: str
    decision: str
    context: str
    response: str

# --- 3. THE "BRAIN" NODES ---

def semantic_router(state: AgentState):
    """Analyses the query to decide the retrieval path."""
    print("\n🔍 [ROUTER]: Analyzing query intent...")
    q = state["query"].lower()
    
    # Intelligent routing logic
    if any(word in q for word in ["revenue", "table", "data", "numbers"]):
        print("➡️ [DECISION]: Routing to TABULAR ANALYSIS")
        return {"decision": "tabular"}
    
    print("➡️ [DECISION]: Routing to VECTOR SEARCH")
    return {"decision": "vector"}

def vector_fetcher(state: AgentState):
    """Simulates high-density vector retrieval."""
    print("📂 [VECTOR NODE]: Searching local document embeddings...")
    return {"context": "User manual states that Omni-Sentinel is a localized RAG agent."}

def table_fetcher(state: AgentState):
    """Simulates structured data extraction."""
    print("📊 [TABLE NODE]: Extracting markdown table data...")
    return {"context": "| Quarter | Revenue |\n|---|---|\n| Q3 | $4.2M |\n| Q4 | $5.1M |"}

def responder(state: AgentState):
    """Final LLM synthesis."""
    print("✍️  [GENERATOR]: Synthesizing final answer...")
    prompt = f"Using this context: {state['context']}\nAnswer the question: {state['query']}"
    res = llm.invoke(prompt)
    return {"response": res.content}

# --- 4. GRAPH CONSTRUCTION ---


workflow = StateGraph(AgentState)

workflow.add_node("router", semantic_router)
workflow.add_node("vector_path", vector_fetcher)
workflow.add_node("table_path", table_fetcher)
workflow.add_node("generator", responder)

workflow.set_entry_point("router")

# Map decisions to nodes
workflow.add_conditional_edges(
    "router",
    lambda x: x["decision"],
    {
        "vector": "vector_path",
        "tabular": "table_path"
    }
)

workflow.add_edge("vector_path", "generator")
workflow.add_edge("table_path", "generator")
workflow.add_edge("generator", END)

app = workflow.compile()

# --- 5. EXECUTION ---
if __name__ == "__main__":
    print("--- OMNI-SENTINEL AGENT STARTING ---")
    user_input = "2024 future projections  "
    result = app.invoke({
        "query": user_input,
        "decision": "",
        "context": "",
        "response": ""
    })
    
    print("\n" + "="*40)
    print(f"USER QUERY: {user_input}")
    print(f"AGENT RESPONSE:\n{result['response']}")
    print("="*40)