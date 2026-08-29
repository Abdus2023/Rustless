import json
from pathlib import Path

def markdown(graph):
    s = graph.get("summary", {})
    sections = [("Executive Summary", f"FINAL STATUS: {s.get('status')}"), ("Repository Identity", graph.get("repository", {})), ("Environment", graph.get("environment", {})), ("Toolchains", graph.get("toolchains", {})), ("Inventory", graph.get("inventory", {})), ("Fixtures", graph.get("fixtures", [])), ("Integrity", graph.get("integrity", {})), ("Provenance", graph.get("provenance", {})), ("Claims", graph.get("claims", [])), ("Static Analysis", graph.get("static", {})), ("CI Reconciliation", graph.get("ci", {})), ("Gates", graph.get("gates", [])), ("Evidence", graph.get("evidence", [])), ("Limitations", graph.get("limitations", [])), ("Blockers", graph.get("blockers", [])), ("Final Status", f"FINAL STATUS: {s.get('status')}")]
    out = ["# Rustless Verification Report", ""]
    for title, value in sections:
        out.append(f"## {title}")
        out.append(value if isinstance(value, str) else "```json\n" + json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n```")
        out.append("")
    return "\n".join(out)

def write(graph, out):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    canonical = json.loads(out.read_text(encoding="utf-8"))
    out.with_suffix(".md").write_text(markdown(canonical), encoding="utf-8")
