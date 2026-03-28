import argparse
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any


BASELINE_FILE = Path(__file__).with_name("baseline_prompts.json")


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, int(round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def run_once(query: str) -> None:
    from app import invoke_query

    try:
        result = invoke_query(query)
    except Exception as exc:  # pragma: no cover - runtime safety for local model issues
        print("\n" + "=" * 40)
        print(f"USER QUERY: {query}")
        print("ROUTE: unknown")
        print(f"AGENT ERROR: {type(exc).__name__}: {exc}")
        print("=" * 40)
        return

    print("\n" + "=" * 40)
    print(f"USER QUERY: {query}")
    print(f"ROUTE: {result.get('decision', 'unknown')}")
    print(f"AGENT RESPONSE:\n{result.get('response', '')}")
    print("=" * 40)


def smoke_test(
    route_only: bool,
    min_route_accuracy: float,
    min_success_rate: float,
    max_p95_ms: float,
    report_file: str,
) -> int:
    if route_only and os.getenv("ENABLE_EVAL_STUB_LLM") is None:
        os.environ["ENABLE_EVAL_STUB_LLM"] = "true"

    from app import invoke_query

    if not BASELINE_FILE.exists():
        print(f"Baseline file not found: {BASELINE_FILE}")
        return 1

    cases = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    latencies_ms: list[float] = []
    passed = 0
    route_pass = 0
    content_pass = 0
    runtime_errors = 0

    print(f"Running smoke test with {len(cases)} baseline prompts...")

    for idx, case in enumerate(cases, start=1):
        query = case["query"]
        expected_route = case.get("expected_route", "")
        expected_tokens = case.get("expected_any_contains", [])

        start = time.perf_counter()
        result: dict[str, Any] = {}
        error_text = ""
        try:
            result = invoke_query(query)
        except Exception as exc:  # pragma: no cover - runtime safety for local model issues
            runtime_errors += 1
            error_text = f"{type(exc).__name__}: {exc}"

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies_ms.append(elapsed_ms)

        actual_route = str(result.get("decision", "")).strip().lower()
        response_text = str(result.get("response", ""))
        response_lower = response_text.lower()

        is_route_ok = actual_route == str(expected_route).strip().lower()
        if route_only:
            is_content_ok = True
        else:
            is_content_ok = (not expected_tokens) or any(
                str(token).lower() in response_lower for token in expected_tokens
            )
        is_case_ok = is_route_ok and is_content_ok

        route_pass += 1 if is_route_ok else 0
        content_pass += 1 if is_content_ok else 0
        passed += 1 if is_case_ok else 0

        status = "PASS" if is_case_ok else "FAIL"
        print(
            f"[{idx:02d}/{len(cases)}] {status} | "
            f"route={actual_route} expected={expected_route} | "
            f"latency_ms={elapsed_ms:.1f}"
        )
        if error_text:
            print(f"    error={error_text}")

    total = max(1, len(cases))
    success_rate = (passed / total) * 100.0
    route_rate = (route_pass / total) * 100.0
    content_rate = (content_pass / total) * 100.0
    avg_latency = statistics.fmean(latencies_ms) if latencies_ms else 0.0
    p95_latency = _p95(latencies_ms)

    print("\n--- BASELINE METRICS ---")
    print(f"Total cases: {len(cases)}")
    print(f"Passed cases: {passed}")
    print(f"Runtime errors: {runtime_errors}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Route accuracy: {route_rate:.1f}%")
    print(f"Content check pass rate: {content_rate:.1f}%")
    print(f"Average latency: {avg_latency:.1f} ms")
    print(f"P95 latency: {p95_latency:.1f} ms")

    report = {
        "total_cases": len(cases),
        "passed_cases": passed,
        "runtime_errors": runtime_errors,
        "success_rate": round(success_rate, 2),
        "route_accuracy": round(route_rate, 2),
        "content_check_pass_rate": round(content_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "thresholds": {
            "min_route_accuracy": min_route_accuracy,
            "min_success_rate": min_success_rate,
            "max_p95_ms": max_p95_ms,
        },
    }
    Path(report_file).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report written: {report_file}")

    thresholds_ok = (
        route_rate >= min_route_accuracy
        and success_rate >= min_success_rate
        and p95_latency <= max_p95_ms
    )
    if not thresholds_ok:
        print("Threshold check: FAIL")
        return 3

    print("Threshold check: PASS")

    return 0 if passed == len(cases) else 2


def health_check() -> int:
    from app import check_model_health

    healthy, detail = check_model_health()
    status = "OK" if healthy else "ERROR"
    print(f"Health check: {status} - {detail}")
    return 0 if healthy else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Omni-Sentinel runner")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "smoke_test", "health_check"],
        help="run a single query or execute baseline smoke tests",
    )
    parser.add_argument(
        "--query",
        default="2024 future projections",
        help="query text for 'run' command",
    )
    parser.add_argument(
        "--route-only",
        action="store_true",
        help="evaluate route and latency only (skips content checks)",
    )
    parser.add_argument(
        "--min-route-accuracy",
        type=float,
        default=100.0,
        help="minimum required route accuracy percent",
    )
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=70.0,
        help="minimum required overall success rate percent",
    )
    parser.add_argument(
        "--max-p95-ms",
        type=float,
        default=6000.0,
        help="maximum allowed p95 latency in ms",
    )
    parser.add_argument(
        "--report-file",
        default="eval_report.json",
        help="path to write evaluation JSON report",
    )
    args = parser.parse_args()

    if args.command == "smoke_test":
        return smoke_test(
            route_only=args.route_only,
            min_route_accuracy=args.min_route_accuracy,
            min_success_rate=args.min_success_rate,
            max_p95_ms=args.max_p95_ms,
            report_file=args.report_file,
        )
    if args.command == "health_check":
        return health_check()

    run_once(args.query)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
