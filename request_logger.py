import json
import os
from datetime import datetime, timezone

LOG_FILE = "logs/requests.jsonl"


def log_request(question: str, answer: str, tool_calls: list, latency_seconds: float, error: str = None):
    """Append one request's details as a JSON line to the log file."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "answer": answer,
        "tool_calls": tool_calls,
        "num_tool_calls": len(tool_calls),
        "latency_seconds": latency_seconds,
        "error": error
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, default=str) + "\n")