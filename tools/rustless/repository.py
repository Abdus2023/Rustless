from pathlib import Path
import subprocess

def git(root,args):
    try: return subprocess.run(['git',*args],cwd=root,text=True,capture_output=True,timeout=10,check=False)
    except (OSError,subprocess.SubprocessError): return None

def identity(root):
    r=git(root,['rev-parse','HEAD']); b=git(root,['branch','--show-current']); s=git(root,['status','--porcelain','--untracked-files=all'])
    return {'root':str(root),'git_available':r is not None,'head':r.stdout.strip() if r and r.returncode==0 else None,'branch':b.stdout.strip() if b and b.returncode==0 else None,'working_tree_clean':bool(s and s.returncode==0 and not s.stdout),'git_status':'VERIFIED' if r and r.returncode==0 else 'BLOCKED'}
