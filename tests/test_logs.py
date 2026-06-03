from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.redaction import REDACTED, redact_lines


client = TestClient(app)


def test_redact_lines_masks_sensitive_values() -> None:
    lines = [
        "normal startup",
        "token=super-secret",
        "Authorization: Bearer abc.def.ghi",
        "password=hunter2",
        "api_key=not-for-ui",
    ]

    redacted = redact_lines(lines)

    assert redacted[0] == "normal startup"
    assert all(REDACTED in line for line in redacted[1:])


def test_api_logs_sources_returns_allowlisted_metadata_only(tmp_path: Path, monkeypatch) -> None:
    stdout = tmp_path / "gateway.log"
    stderr = tmp_path / "gateway.error.log"
    stdout.write_text("line\n", encoding="utf-8")
    stderr.write_text("err\n", encoding="utf-8")
    monkeypatch.setenv("HERMES_GATEWAY_STDOUT_LOG", str(stdout))
    monkeypatch.setenv("HERMES_GATEWAY_STDERR_LOG", str(stderr))

    response = client.get("/api/logs/sources")

    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    source_ids = {item["source_id"] for item in payload["sources"]}
    assert source_ids == {"gateway_stdout", "gateway_stderr"}
    for item in payload["sources"]:
        assert "absolute_path" not in item
        assert item["requires_redaction"] is True


def test_api_logs_unknown_source_returns_404() -> None:
    response = client.get("/api/logs/not-a-real-source")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["error"] == "unknown_log_source"


def test_api_logs_returns_redacted_tail(tmp_path: Path, monkeypatch) -> None:
    log_file = tmp_path / "gateway.log"
    log_file.write_text(
        "\n".join(
            [
                "service started",
                "token=hidden-value",
                "still running",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_GATEWAY_STDOUT_LOG", str(log_file))
    monkeypatch.setenv("HERMES_GATEWAY_STDERR_LOG", str(tmp_path / "missing.err"))

    response = client.get("/api/logs/gateway_stdout?lines=50")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["source_id"] == "gateway_stdout"
    assert payload["redacted"] is True
    assert payload["returned_lines"] == 3
    assert "hidden-value" not in "\n".join(payload["content"])
    assert REDACTED in payload["content"][1]


def test_api_logs_missing_file_returns_safe_payload(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HERMES_GATEWAY_STDOUT_LOG", str(tmp_path / "missing.log"))
    monkeypatch.setenv("HERMES_GATEWAY_STDERR_LOG", str(tmp_path / "missing.err"))

    response = client.get("/api/logs/gateway_stdout?lines=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"] == "log_file_unavailable"
    assert "traceback" not in response.text.lower()


def test_api_logs_rejects_too_many_lines() -> None:
    response = client.get("/api/logs/gateway_stdout?lines=501")

    assert response.status_code == 422
