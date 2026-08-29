from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

class Status(str, Enum):
    VERIFIED='VERIFIED'; PARTIALLY_VERIFIED='PARTIALLY_VERIFIED'; PROVISIONAL='PROVISIONAL'; BLOCKED='BLOCKED'

ORDER={Status.VERIFIED:0, Status.PARTIALLY_VERIFIED:1, Status.PROVISIONAL:2, Status.BLOCKED:3}
EXIT_CODES={Status.VERIFIED:0,Status.PARTIALLY_VERIFIED:1,Status.PROVISIONAL:2,Status.BLOCKED:3}

@dataclass
class Evidence:
    id: str; kind: str; subject: str; status: Status; source: str='rustless'; method: str=''; details: dict[str,Any]=field(default_factory=dict); limitations:list[str]=field(default_factory=list); timestamp:None=None
    def json(self):
        d=asdict(self); d['status']=self.status.value; return d

@dataclass
class Finding:
    id:str; kind:str; subject:str; status:Status; message:str; evidence:list[str]=field(default_factory=list); details:dict[str,Any]=field(default_factory=dict)
    def json(self):
        d=asdict(self); d['status']=self.status.value; return d

@dataclass
class Gate:
    id:str; name:str; required:bool; status:Status; evidence:list[str]=field(default_factory=list); reason:str=''; blocking_reasons:list[str]=field(default_factory=list); class_name:str='required'
    def json(self):
        d=asdict(self); d['status']=self.status.value; return d

def aggregate(statuses):
    vals=list(statuses)
    return max(vals,key=lambda s:ORDER[s]) if vals else Status.VERIFIED
