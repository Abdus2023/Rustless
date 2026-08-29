import hashlib
import json
from .models import Evidence, Status

class EvidenceStore:
    def __init__(self): self.items = []
    def add(self, kind, subject, status, method="", details=None, limitations=None):
        payload = {"kind": kind, "subject": subject, "status": Status(status).value, "source": "rustless", "method": method, "details": details or {}, "limitations": limitations or []}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]
        eid = f"EV-{digest}"
        self.items.append(Evidence(eid, kind, subject, Status(status), method=method, details=details or {}, limitations=limitations or []))
        return eid
    def json(self): return sorted((e.json() for e in self.items), key=lambda x: x["id"])
