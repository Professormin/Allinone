import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from demo import create_demo
from build_prep import build
from install import install
from package import package, FILES


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.path = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_demo_and_template(self):
        demo = create_demo(self.path / 'demo')
        document = Document(demo / 'teacher.docx')
        self.assertEqual(len(document.inline_shapes), 3)
        self.assertIn('一次函数', document.paragraphs[0].text)
        with self.assertRaises(FileExistsError):
            build(demo / 'prep.json', None, demo / 'teacher.docx')
        template = self.path / 'reference.docx'
        source = Document()
        source.add_paragraph('OLD LESSON')
        source.sections[0].first_page_header.paragraphs[0].text = 'OLD HEADER'
        source.save(template)
        digest = hashlib.sha256(template.read_bytes()).hexdigest()
        build(demo / 'prep.json', template, self.path / 'inherited.docx')
        inherited = Document(self.path / 'inherited.docx')
        self.assertNotIn('OLD LESSON', '\n'.join(p.text for p in inherited.paragraphs))
        self.assertEqual(inherited.sections[0].first_page_header.paragraphs[0].text, '')
        self.assertEqual(hashlib.sha256(template.read_bytes()).hexdigest(), digest)

    def test_sources(self):
        demo = create_demo(self.path / 'demo')
        manifest = demo / 'prep.json'
        data = json.loads(manifest.read_text(encoding='utf-8'))
        data['slides'][0]['sources'] = [{'label': 'Original page 1', 'image': 'slide-1.png'}]
        manifest.write_text(json.dumps(data), encoding='utf-8')
        build(manifest, None, self.path / 'paired.docx')
        self.assertEqual(len(Document(self.path / 'paired.docx').inline_shapes), 4)
        data['slides'][0]['sources'][0]['image'] = 'missing.png'
        manifest.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(FileNotFoundError):
            build(manifest, None, self.path / 'invalid.docx')
        self.assertFalse((self.path / 'invalid.docx').exists())

    def test_install_and_public_package(self):
        target = install(self.path / 'installed')
        self.assertTrue((target / 'SKILL.md').is_file())
        with self.assertRaises(FileExistsError):
            install(target)
        archive = package(self.path / 'dist')
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(set(z.namelist()), {'beike/' + name for name in FILES})
            for name in z.namelist():
                content = z.read(name).decode('utf-8')
                self.assertNotRegex(content, r'[A-Z]:[/\\]Users[/\\][a-zA-Z]+')
                self.assertNotRegex(content, r'[A-Z]:[/\\]00_[A-Za-z]+')
        expected = archive.with_suffix('.sha256').read_text().split()[0]
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    unittest.main()
