import json

def dumps(value): return json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def stable_id(prefix,index): return f'{prefix}-{index:04d}'
