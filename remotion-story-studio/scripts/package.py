from pathlib import Path
import argparse, hashlib, zipfile
ROOT=Path(__file__).resolve().parents[1]
ALLOWED=['SKILL.md','README.md','LICENSE','VERSION','PUBLISHING.md','.gitignore','agents','references','scripts','assets','examples','tests']

def package(output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True)
    version=(ROOT/'VERSION').read_text().strip()
    archive=out/f'{ROOT.name}-v{version}.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ALLOWED:
            source=ROOT/name
            paths=source.rglob('*') if source.is_dir() else [source]
            for p in sorted(paths):
                if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc': continue
                z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.sha256').write_text(digest+'  '+archive.name+'\n',encoding='utf-8')
    return archive,digest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();archive,digest=package(a.output);print(str(archive));print(digest)
