from pathlib import Path
import importlib.util, json, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
create=module('create_project');story=module('validate_story')
class WorkflowTests(unittest.TestCase):
 def test_clean_project_and_existing_files(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'video';create.create(p,skip_fonts=True)
   self.assertTrue((p/'src'/'Root.tsx').is_file())
   with self.assertRaises(ValueError):create.create(p,skip_fonts=True)
   props=json.loads((p/'story.example.json').read_text())
   self.assertEqual(story.validate(p,props)['duration_seconds'],6)
 def test_missing_assets_and_traversal(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'public').mkdir();(p/'secret.png').write_bytes(b'x')
   for image in ['../secret.png','https://example.com/x.png','missing.png','/absolute.png']:
    with self.subTest(image=image), self.assertRaises(ValueError):story.validate(p,{'title':'x','scenes':[{'image':image,'caption':'x','seconds':2}]})
 def test_invalid_duration(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'public').mkdir();(p/'public'/'ok.svg').write_text('<svg/>')
   for seconds in [True,float('nan'),0,31,'2']:
    with self.subTest(seconds=seconds),self.assertRaises(ValueError):story.validate(p,{'title':'x','scenes':[{'image':'ok.svg','caption':'x','seconds':seconds}]})
if __name__=='__main__':unittest.main()
