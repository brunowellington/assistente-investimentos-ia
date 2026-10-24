import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

def log_event(event: str, details: dict) -> str:
    event_id = str(uuid4())
    path = Path(os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "details": details,
    }
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return event_id
