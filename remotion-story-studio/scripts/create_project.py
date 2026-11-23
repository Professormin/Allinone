"""Create a clean Remotion project without overwriting user files."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, urllib.request
FONT_SOURCES = [
 ('greatvibes','GreatVibes-Regular.ttf'),
 ('dmserifdisplay','DMSerifDisplay-Regular.ttf'),
 ('bebasneue','BebasNeue-Regular.ttf'),
 ('spacemono','SpaceMono-Regular.ttf'),
]
ROOT=Path(__file__).resolve().parents[1]

def fetch_fonts(output):
    dest=output/'public'/'fonts';dest.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for family,filename in FONT_SOURCES:
        for source,local in [(filename,filename),('OFL.txt',family+'-OFL.txt')]:
            url=f'https://raw.githubusercontent.com/google/fonts/main/ofl/{family}/{source}'
            with urllib.request.urlopen(url,timeout=45) as response: data=response.read()
            if source.endswith('.ttf') and (len(data)<1024 or data[:4] not in [b'\x00\x01\x00\x00',b'OTTO']):
                raise ValueError('Invalid font download: '+filename)
            (dest/local).write_bytes(data)
            manifest.append({'file':local,'url':url,'sha256':hashlib.sha256(data).hexdigest()})
    (dest/'sources.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

def create(output,skip_fonts=False,refresh_fonts=False):
    output=Path(output).resolve()
    if refresh_fonts:
        if not (output/'package.json').is_file(): raise ValueError('Not an existing generated project')
    else:
        if output.exists() and any(output.iterdir()): raise ValueError('Output directory must be empty; existing projects are not overwritten')
        output.mkdir(parents=True,exist_ok=True)
        shutil.copytree(ROOT/'assets'/'project',output,dirs_exist_ok=True)
    if not skip_fonts: fetch_fonts(output)
    return output

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--install',action='store_true');parser.add_argument('--skip-fonts',action='store_true');parser.add_argument('--refresh-fonts',action='store_true')
    args=parser.parse_args();output=create(args.output,args.skip_fonts,args.refresh_fonts)
    if args.install:
        npm=shutil.which('npm')
        if not npm: raise RuntimeError('npm not found; install Node.js first')
        subprocess.run([npm,'install','--no-fund'],cwd=output,check=True,shell=False)
    print('Project ready: '+str(output))
if __name__=='__main__': main()
