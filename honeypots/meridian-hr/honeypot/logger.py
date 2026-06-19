"""
Honeypot event logger — writes all events to JSONL for offline analysis.
"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("hplogger")


class HoneypotLogger:
    def __init__(self, log_path: Path = Path("/app/logs/events.jsonl")):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def log_event(self, event_type: str, data: dict):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            **data,
        }
        with self._lock:
            try:
                with open(self.log_path, "a") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                logger.error(f"Log write failed: {e}")
