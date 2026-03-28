import argparse
import json
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from app import invoke_query

DEFAULT_QUERY_FILE = Path("queries/all_queries.json")
RESULTS_DIR = Path("results")


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, int(round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def _safe_file_slug(text: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in text)
    slug = "_".join(part for part in slug.split("_") if part)
    return slug[:64] if slug else "query"


def load_queries(query_file: Path) -> list[dict[str, Any]]:
    if not query_file.exists():
        raise FileNotFoundError(f"Query file not found: {query_file}")
    payload = json.loads(query_file.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Query file must contain a JSON array.")
    return payload


def run_all(query_file: Path, output_root: Path) -> int:
    queries = load_queries(query_file)
    output_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    run_results: list[dict[str, Any]] = []
    latencies: list[float] = []
    route_pass = 0
    runtime_errors = 0

    print(f"Running {len(queries)} queries from {query_file}...")

    for idx, item in enumerate(queries, start=1):
        query = str(item.get("query", "")).strip()
        query_id = str(item.get("id", f"q_{idx:03d}"))
        category = str(item.get("category", "general"))
        expected_route = str(item.get("expected_route", "")).strip().lower()

        started = time.perf_counter()
        error = ""
        result: dict[str, Any] = {}
        try:
            result = invoke_query(query)
        except Exception as exc:  # pragma: no cover - runtime safeguard
            runtime_errors += 1
            error = f"{type(exc).__name__}: {exc}"

        elapsed_ms = round((time.perf_counter() - started) * 1000.0, 2)
        latencies.append(elapsed_ms)

        actual_route = str(result.get("decision", "")).strip().lower()
        route_ok = bool(expected_route) and actual_route == expected_route
        if route_ok:
            route_pass += 1

        record = {
            "index": idx,
            "id": query_id,
            "category": category,
            "query": query,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "route_ok": route_ok,
            "status": result.get("status", "error" if error else "unknown"),
            "request_id": result.get("request_id", ""),
            "latency_ms": elapsed_ms,
            "response": result.get("response", ""),
            "verification_confidence": result.get("verification_confidence", 0.0),
            "unsupported_claims": result.get("unsupported_claims", []),
            "error": error,
        }
        run_results.append(record)

        out_file = run_dir / f"{idx:03d}_{query_id}_{_safe_file_slug(query)}.json"
        out_file.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

        status = "PASS" if route_ok else "FAIL"
        print(
            f"[{idx:02d}/{len(queries)}] {status} | "
            f"id={query_id} | route={actual_route} expected={expected_route} | latency_ms={elapsed_ms:.2f}"
        )
        if error:
            print(f"    error={error}")

    total = len(queries)
    route_accuracy = (route_pass / total) * 100.0 if total else 0.0
    avg_latency = statistics.fmean(latencies) if latencies else 0.0
    p95_latency = _p95(latencies)

    summary = {
        "query_file": str(query_file),
        "run_dir": str(run_dir),
        "total_queries": total,
        "runtime_errors": runtime_errors,
        "route_accuracy_pct": round(route_accuracy, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "generated_at": datetime.now().isoformat(),
    }

    summary_json = run_dir / "evaluation_summary.json"
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    summary_md = run_dir / "evaluation_summary.md"
    summary_md.write_text(
        "\n".join(
            [
                "# Evaluation Summary",
                "",
                f"- Query file: {query_file}",
                f"- Total queries: {total}",
                f"- Runtime errors: {runtime_errors}",
                f"- Route accuracy: {route_accuracy:.2f}%",
                f"- Average latency: {avg_latency:.2f} ms",
                f"- P95 latency: {p95_latency:.2f} ms",
                f"- Output directory: {run_dir}",
            ]
        ),
        encoding="utf-8",
    )

    all_results_file = run_dir / "all_results.json"
    all_results_file.write_text(json.dumps(run_results, indent=2, ensure_ascii=False), encoding="utf-8")

    latest_link = output_root / "latest_run.txt"
    latest_link.write_text(str(run_dir), encoding="utf-8")

    print("\nRun complete.")
    print(f"Results folder: {run_dir}")
    print(f"Evaluation JSON: {summary_json}")
    print(f"Evaluation Markdown: {summary_md}")
    print(f"Combined results: {all_results_file}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all project queries and store results.")
    parser.add_argument(
        "--query-file",
        default=str(DEFAULT_QUERY_FILE),
        help="path to JSON file containing query definitions",
    )
    parser.add_argument(
        "--output-dir",
        default=str(RESULTS_DIR),
        help="directory where run outputs are stored",
    )
    args = parser.parse_args()

    return run_all(Path(args.query_file), Path(args.output_dir))


if __name__ == "__main__":
    raise SystemExit(main())
