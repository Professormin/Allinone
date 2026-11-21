"""Build a versioned skill ZIP using an explicit public-file allowlist."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'SKILL.md', 'README.md', 'LICENSE', 'VERSION', 'requirements.txt', 'PUBLISHING.md',
    'agents/openai.yaml', 'references/configuration.md', 'references/teaching-modes.md',
    'references/prep-schema.md', 'scripts/build_prep.py', 'scripts/demo.py',
    'scripts/install.py', 'scripts/package.py', 'tests/test_workflow.py',
]


def package(output):
    output = Path(output)
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not version or any(c not in '0123456789.' for c in version):
        raise ValueError('Invalid VERSION')
    for name in FILES:
        if not (ROOT / name).is_file():
            raise FileNotFoundError(name)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'beike-v{version}.zip'
    checksum = output / f'beike-v{version}.sha256'
    if archive.exists() or checksum.exists():
        raise FileExistsError('Release files already exist; choose a new directory/version')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as zipped:
        for name in FILES:
            zipped.write(ROOT / name, 'beike/' + name)
    checksum.write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n', encoding='utf-8')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(package(parser.parse_args().output))
