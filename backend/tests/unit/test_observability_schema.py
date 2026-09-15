from __future__ import annotations

from app.schemas.observability import RunMetricsResponse


def test_run_metrics_response_accepts_metrics() -> None:
    response = RunMetricsResponse(
        total_runs=10,
        queued_runs=2,
        running_runs=1,
        completed_runs=5,
        failed_runs=2,
        average_duration_ms=1532.41,
    )

    assert response.total_runs == 10
    assert response.completed_runs == 5
    assert response.average_duration_ms == 1532.41


def test_run_metrics_response_allows_missing_average_duration() -> None:
    response = RunMetricsResponse(
        total_runs=3,
        queued_runs=2,
        running_runs=1,
        completed_runs=0,
        failed_runs=0,
    )

    assert response.average_duration_ms is None