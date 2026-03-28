import threading
import time
from collections import defaultdict, deque

from fastapi import FastAPI
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field

from app import check_model_health, invoke_query, settings


app = FastAPI(title="Omni-Sentinel API", version="0.1.0")


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            q = self._hits[key]
            cutoff = now - self.window_seconds
            while q and q[0] <= cutoff:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


_limiter = InMemoryRateLimiter(
    limit=settings.api_rate_limit_requests,
    window_seconds=settings.api_rate_limit_window_seconds,
)


def _client_key(request: Request) -> str:
    host = request.client.host if request.client else "unknown"
    return host or "unknown"


def _enforce_rate_limit(request: Request) -> None:
    if not settings.api_rate_limit_enabled:
        return
    key = _client_key(request)
    if not _limiter.allow(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)


class QueryResponse(BaseModel):
    request_id: str
    decision: str
    response: str
    status: str
    total_latency_ms: float
    verification_confidence: float = 0.0
    unsupported_claims: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    healthy, detail = check_model_health()
    return {
        "ok": healthy,
        "detail": detail,
    }


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, request: Request) -> QueryResponse:
    _enforce_rate_limit(request)
    result = invoke_query(payload.query)
    return QueryResponse(
        request_id=str(result.get("request_id", "")),
        decision=str(result.get("decision", "")),
        response=str(result.get("response", "")),
        status=str(result.get("status", "unknown")),
        total_latency_ms=float(result.get("total_latency_ms", 0.0)),
        verification_confidence=float(result.get("verification_confidence", 0.0)),
        unsupported_claims=[str(x) for x in result.get("unsupported_claims", [])],
    )
