from pathlib import Path
import argparse, json, math

def validate(project,props):
    public=(Path(project)/'public').resolve()
    if not isinstance(props,dict) or not isinstance(props.get('title'),str): raise ValueError('title must be a string')
    scenes=props.get('scenes')
    if not isinstance(scenes,list) or not 1<=len(scenes)<=20: raise ValueError('scenes must contain 1 to 20 scenes')
    total=0
    for scene in scenes:
        if not isinstance(scene,dict): raise ValueError('Each scene must be an object')
        image=scene.get('image')
        if not isinstance(image,str) or not image or '\\' in image or ':' in image: raise ValueError('Use a relative image path under public/')
        relative=Path(image)
        target=(public/relative).resolve()
        if relative.is_absolute() or not target.is_relative_to(public): raise ValueError('Image escapes public directory')
        if not target.is_file(): raise ValueError('Missing image: '+image)
        seconds=scene.get('seconds')
        if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or not math.isfinite(seconds) or not 1<=seconds<=30: raise ValueError('seconds must be a finite number from 1 to 30')
        if not isinstance(scene.get('caption'),str): raise ValueError('caption must be a string')
        total+=seconds
    return {'scenes':len(scenes),'duration_seconds':total}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--props',required=True);a=p.parse_args();print(json.dumps(validate(a.project,json.loads(Path(a.props).read_text(encoding='utf-8-sig')))))
