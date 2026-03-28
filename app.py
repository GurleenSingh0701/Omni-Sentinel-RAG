import os
import csv
import json
import re
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Load local environment variables from .env if present.
load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    lmstudio_model: str
    lmstudio_api_key: str
    lmstudio_base_url: str
    lm_temperature: float
    llm_timeout_seconds: int
    llm_max_retries: int
    tabular_keywords: tuple[str, ...]
    tabular_metric_keywords: tuple[str, ...]
    startup_healthcheck: bool
    fallback_response: str
    vector_context_file: str
    tabular_data_file: str
    tabular_data_files: tuple[str, ...]
    enable_eval_stub_llm: bool
    max_query_chars: int
    enable_input_sanitization: bool
    enable_log_redaction: bool
    api_rate_limit_enabled: bool
    api_rate_limit_requests: int
    api_rate_limit_window_seconds: int
    enable_guardrails: bool
    enable_verify: bool
    enable_tracing: bool

    @staticmethod
    def from_env() -> "AppConfig":
        raw_keywords = os.getenv(
            "TABULAR_KEYWORDS",
            "revenue,table,data,numbers,quarter,quarters,q1,q2,q3,q4,year,years",
        )
        parsed_keywords = tuple(k.strip().lower() for k in raw_keywords.split(",") if k.strip())
        raw_metric_keywords = os.getenv(
            "TABULAR_METRIC_KEYWORDS",
            "revenue,growth,customer,customers,renewal,margin,sla,incident,incidents,mttr,mtta,false_positive,nps,churn,segment,expansion_mrr,rate,pct,percent,kpi,trend,compare",
        )
        parsed_metric_keywords = tuple(
            k.strip().lower() for k in raw_metric_keywords.split(",") if k.strip()
        )
        default_tabular_catalog = (
            "data/revenue.csv",
            "data/incidents.csv",
            "data/customers.csv",
        )
        raw_tabular_files = os.getenv("TABULAR_DATA_FILES", "")
        parsed_tabular_files = tuple(
            item.strip() for item in raw_tabular_files.split(",") if item.strip()
        )
        default_tabular_file = os.getenv("TABULAR_DATA_FILE", "data/revenue.csv")
        final_tabular_files = parsed_tabular_files or default_tabular_catalog

        return AppConfig(
            lmstudio_model=os.getenv("LMSTUDIO_MODEL", "local-model"),
            lmstudio_api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
            lm_temperature=_env_float("LM_TEMPERATURE", 0.0),
            llm_timeout_seconds=_env_int("LLM_TIMEOUT_SECONDS", 60),
            llm_max_retries=_env_int("LLM_MAX_RETRIES", 2),
            tabular_keywords=parsed_keywords or ("revenue", "table", "data", "numbers"),
            tabular_metric_keywords=parsed_metric_keywords
            or (
                "revenue",
                "growth",
                "customer",
                "customers",
                "renewal",
                "margin",
                "sla",
                "incident",
                "incidents",
                "mttr",
                "mtta",
                "false_positive",
                "nps",
                "churn",
                "segment",
                "expansion_mrr",
                "rate",
                "pct",
                "percent",
                "kpi",
                "trend",
                "compare",
            ),
            startup_healthcheck=_env_bool("STARTUP_HEALTHCHECK", False),
            fallback_response=os.getenv(
                "FALLBACK_RESPONSE",
                "I could not reach the local model server. Please verify LM Studio is running and try again.",
            ),
            vector_context_file=os.getenv("VECTOR_CONTEXT_FILE", "docs/company_overview.txt"),
            tabular_data_file=default_tabular_file,
            tabular_data_files=final_tabular_files,
            enable_eval_stub_llm=_env_bool("ENABLE_EVAL_STUB_LLM", False),
            max_query_chars=max(256, _env_int("MAX_QUERY_CHARS", 5000)),
            enable_input_sanitization=_env_bool("ENABLE_INPUT_SANITIZATION", True),
            enable_log_redaction=_env_bool("ENABLE_LOG_REDACTION", True),
            api_rate_limit_enabled=_env_bool("API_RATE_LIMIT_ENABLED", True),
            api_rate_limit_requests=max(1, _env_int("API_RATE_LIMIT_REQUESTS", 60)),
            api_rate_limit_window_seconds=max(1, _env_int("API_RATE_LIMIT_WINDOW_SECONDS", 60)),
            enable_guardrails=_env_bool("ENABLE_GUARDRAILS", False),
            enable_verify=_env_bool("ENABLE_VERIFY", False),
            enable_tracing=_env_bool("ENABLE_TRACING", False),
        )


settings = AppConfig.from_env()

_REDACTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)bearer\s+[a-z0-9._\-]+"), "[REDACTED_TOKEN]"),
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)([^\s]+)"), r"\1[REDACTED_KEY]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{12,19}\b"), "[REDACTED_NUMBER]"),
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_query_text(query: str) -> str:
    """Normalize and bound user input to reduce injection/noise risks."""
    cleaned = query
    if settings.enable_input_sanitization:
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) > settings.max_query_chars:
        cleaned = cleaned[: settings.max_query_chars]
    return cleaned


def _redact_text(value: str) -> str:
    text = value
    for pattern, repl in _REDACTION_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def _redact_obj(value: object) -> object:
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, dict):
        return {str(k): _redact_obj(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_obj(v) for v in value]
    return value


def _read_text_file(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _csv_to_markdown_table(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return ""

    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
    except Exception:
        return ""

    if not rows or not rows[0]:
        return ""

    headers = [cell.strip() for cell in rows[0]]
    data_rows = [[cell.strip() for cell in row] for row in rows[1:] if row]

    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "|" + "|".join(["---"] * len(headers)) + "|"
    body_lines = ["| " + " | ".join(row) + " |" for row in data_rows]

    return "\n".join([header_line, divider_line, *body_lines])


def _format_table_section(path_str: str) -> str:
    table = _csv_to_markdown_table(path_str)
    if not table:
        return ""
    title = Path(path_str).stem.replace("_", " ").title()
    return f"### {title}\n{table}"


def log_event(event: str, request_id: str | None = None, **fields: object) -> None:
    payload = {
        "ts": _utc_now_iso(),
        "event": event,
    }
    if request_id:
        payload["request_id"] = request_id
    payload.update(fields)
    if settings.enable_log_redaction:
        payload = _redact_obj(payload)
    print(json.dumps(payload, ensure_ascii=True, default=str))


def setup_tracing() -> None:
    if not settings.enable_tracing:
        return

    try:
        from openinference.instrumentation.langchain import LangChainInstrumentor

        LangChainInstrumentor().instrument()
        log_event("tracing.enabled")
    except Exception as exc:
        log_event("tracing.failed", error=f"{type(exc).__name__}: {exc}")


setup_tracing()

# --- 1. LOCAL MODEL SETUP ---
# LM Studio exposes an OpenAI-compatible API at http://127.0.0.1:1234/v1 by default.
# Set LMSTUDIO_MODEL to the exact loaded model identifier shown in LM Studio.
llm = ChatOpenAI(
    model=settings.lmstudio_model,
    temperature=settings.lm_temperature,
    api_key=settings.lmstudio_api_key,
    base_url=settings.lmstudio_base_url,
    timeout=settings.llm_timeout_seconds,
    max_retries=settings.llm_max_retries,
)

# --- 2. THE STATE MACHINE DEFINITION ---
class AgentState(TypedDict):
    query: str
    decision: str
    context: str
    response: str
    request_id: str
    status: str
    latency_ms: float
    verification_confidence: float
    unsupported_claims: list[str]

# --- 3. THE "BRAIN" NODES ---

def semantic_router(state: AgentState):
    """Analyses the query to decide the retrieval path."""
    request_id = state.get("request_id", "")
    log_event("router.start", request_id=request_id)
    q = state["query"].lower()

    has_tabular_keyword = any(word in q for word in settings.tabular_keywords)
    has_metric_keyword = any(word in q for word in settings.tabular_metric_keywords)
    has_quarter_hint = re.search(r"\bq[1-4]\b", q) is not None
    has_year_hint = re.search(r"\b20\d{2}\b", q) is not None

    # Route to tabular if explicit keyword is present or if query references
    # time-sliced metrics (e.g., quarter/year + business metric language).
    if has_tabular_keyword or (has_metric_keyword and (has_quarter_hint or has_year_hint)):
        log_event("router.decision", request_id=request_id, decision="tabular")
        return {"decision": "tabular"}
    
    log_event("router.decision", request_id=request_id, decision="vector")
    return {"decision": "vector"}

def vector_fetcher(state: AgentState):
    """Fetches semantic context from a text file with safe fallback."""
    log_event("vector_fetcher.start", request_id=state.get("request_id", ""))
    context = _read_text_file(settings.vector_context_file)
    if not context:
        context = "User manual states that Omni-Sentinel is a localized RAG agent."
    return {"context": context}

def table_fetcher(state: AgentState):
    """Fetches structured context from one or more CSV files and formats markdown tables."""
    log_event("table_fetcher.start", request_id=state.get("request_id", ""))
    sections = [
        _format_table_section(path_str)
        for path_str in settings.tabular_data_files
    ]
    sections = [section for section in sections if section]

    if not sections:
        fallback_table = "| Quarter | Revenue |\n|---|---|\n| Q3 | $4.2M |\n| Q4 | $5.1M |"
        return {"context": fallback_table}

    return {"context": "\n\n".join(sections)}


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def verify_response(context: str, query: str, answer: str) -> tuple[float, list[str]]:
    """Optional verifier pass that scores context support for the generated answer."""
    if settings.enable_eval_stub_llm:
        return 1.0, []

    prompt = (
        "You are a strict factual verifier.\n"
        "Given context, query, and answer, return valid JSON only with keys:\n"
        "confidence (number 0 to 1), unsupported_claims (array of strings).\n"
        "Do not include markdown or extra text.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUERY:\n{query}\n\n"
        f"ANSWER:\n{answer}\n"
    )

    try:
        res = llm.invoke(prompt)
        payload = json.loads(str(res.content).strip())
        confidence = _safe_float(payload.get("confidence"), default=0.0)
        confidence = max(0.0, min(1.0, confidence))
        unsupported = payload.get("unsupported_claims", [])
        if not isinstance(unsupported, list):
            unsupported = []
        unsupported = [str(x) for x in unsupported]
        return confidence, unsupported
    except Exception:
        # Verification errors should never break the main response path.
        return 0.0, ["verification_unavailable"]

def responder(state: AgentState):
    """Final LLM synthesis."""
    request_id = state.get("request_id", "")
    log_event("generator.start", request_id=request_id)
    started = time.perf_counter()

    prompt = f"Using this context: {state['context']}\nAnswer the question: {state['query']}"
    if settings.enable_guardrails and state.get("decision") == "tabular":
        prompt = (
            "Use only numbers that appear in the provided context. "
            "If a requested number is missing, say it is not available in context.\n\n"
            + prompt
        )

    status = "ok"
    confidence = 0.0
    unsupported_claims: list[str] = []

    try:
        if settings.enable_eval_stub_llm:
            response_text = f"Stubbed response from context: {state['context'][:180]}"
            status = "stubbed"
        else:
            res = llm.invoke(prompt)
            response_text = str(res.content)
    except Exception as exc:
        status = "fallback"
        log_event(
            "generator.model_call_failed",
            request_id=request_id,
            error=f"{type(exc).__name__}: {exc}",
        )
        response_text = settings.fallback_response

    if settings.enable_verify:
        confidence, unsupported_claims = verify_response(
            context=state["context"],
            query=state["query"],
            answer=response_text,
        )

    latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
    log_event(
        "generator.end",
        request_id=request_id,
        status=status,
        latency_ms=latency_ms,
        verification_enabled=settings.enable_verify,
    )

    return {
        "response": response_text,
        "status": status,
        "latency_ms": latency_ms,
        "verification_confidence": confidence,
        "unsupported_claims": unsupported_claims,
    }

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


def invoke_query(query: str, request_id: str | None = None) -> dict:
    """Run a single query through the graph and return the final state."""
    rid = request_id or str(uuid4())
    safe_query = sanitize_query_text(query)
    started = time.perf_counter()
    log_event("request.start", request_id=rid, query=safe_query, raw_query_len=len(query))

    result = app.invoke(
        {
            "query": safe_query,
            "decision": "",
            "context": "",
            "response": "",
            "request_id": rid,
            "status": "started",
            "latency_ms": 0.0,
            "verification_confidence": 0.0,
            "unsupported_claims": [],
        }
    )

    total_latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
    result["request_id"] = rid
    result["total_latency_ms"] = total_latency_ms
    log_event(
        "request.end",
        request_id=rid,
        status=result.get("status", "unknown"),
        decision=result.get("decision", ""),
        total_latency_ms=total_latency_ms,
    )
    return result


def check_model_health() -> tuple[bool, str]:
    """Basic local model server check for startup and operations."""
    try:
        llm.invoke("Reply with exactly: ok")
        return True, "model reachable"
    except Exception as exc:
        return False, f"model unreachable: {type(exc).__name__}: {exc}"

# --- 5. EXECUTION ---
if __name__ == "__main__":
    print("--- OMNI-SENTINEL AGENT STARTING ---")
    print(
        "[CONFIG] "
        f"model={settings.lmstudio_model}, "
        f"guardrails={settings.enable_guardrails}, "
        f"verify={settings.enable_verify}, "
        f"tracing={settings.enable_tracing}, "
        f"eval_stub={settings.enable_eval_stub_llm}"
    )
    if settings.startup_healthcheck:
        healthy, detail = check_model_health()
        status = "OK" if healthy else "ERROR"
        print(f"[HEALTHCHECK] {status}: {detail}")

    user_input = "2024 future projections"
    result = invoke_query(user_input)
    
    print("\n" + "="*40)
    print(f"USER QUERY: {user_input}")
    print(f"AGENT RESPONSE:\n{result['response']}")
    print("="*40)