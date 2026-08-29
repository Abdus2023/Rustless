from .models import Evidence,Status
class EvidenceStore:
    def __init__(self): self.items=[]
    def add(self,kind,subject,status,method='',details=None,limitations=None):
        eid=f'EV-{len(self.items)+1:04d}'; e=Evidence(eid,kind,subject,Status(status),method=method,details=details or {},limitations=limitations or []); self.items.append(e); return eid
    def json(self): return [e.json() for e in self.items]
