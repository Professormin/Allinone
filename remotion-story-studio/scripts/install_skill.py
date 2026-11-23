from pathlib import Path
import argparse, os, shutil

def install(destination):
    source=Path(__file__).resolve().parents[1]
    target=Path(destination).expanduser().resolve()/source.name
    if target.exists(): raise FileExistsError('Skill already exists; inspect before replacing: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','dist','node_modules','out','private'))
    return target
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',default=str(Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'skills'));a=p.parse_args();print(install(a.destination))
