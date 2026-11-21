from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def verify():
    text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    if not text.startswith('---\n'): raise ValueError('Missing skill frontmatter')
    front=text.split('---',2)[1]
    name=re.search(r'^name: (.+)$',front,re.M)
    if not name or name.group(1)!=ROOT.name or not re.fullmatch('[a-z0-9-]{1,64}',name.group(1)): raise ValueError('Invalid skill name')
    if not re.search(r'^description: Use when',front,re.M): raise ValueError('Missing trigger description')
    for relative in re.findall(r'\]\((references/[^)]+)\)',text):
        if not (ROOT/relative).is_file(): raise ValueError('Missing reference: '+relative)
    count=0
    for p in ROOT.rglob('*'):
        if '.git' in p.parts or '__pycache__' in p.parts: continue
        if p.is_symlink(): raise ValueError('Symlink cannot enter public package: '+str(p))
        if not p.is_file(): continue
        if p.suffix.lower() in ['.png','.jpg','.jpeg','.ttf','.otf','.mp4','.env']: raise ValueError('Unexpected media/font/credential file: '+str(p))
        if p.suffix in ['.md','.py','.ts','.tsx','.json','.yaml']:
            content=p.read_text(encoding='utf-8')
            if re.search(r'[A-Za-z]:[\\/](?:Users|00_Professormin)',content): raise ValueError('Personal absolute path: '+str(p))
            if re.search(r'(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]{15,}',content): raise ValueError('Possible credential: '+str(p))
        count+=1
    print('Public package verified:',count,'files; no private media, fonts, personal paths or recognized tokens')
if __name__=='__main__': verify()
