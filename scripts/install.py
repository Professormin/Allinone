"""Copy the public skill files into an explicitly chosen, new directory."""
import argparse
from pathlib import Path
import shutil
from package import ROOT, FILES


def install(target):
    target = Path(target).expanduser().resolve()
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite existing installation: {target}')
    for name in FILES:
        if not (ROOT / name).is_file():
            raise FileNotFoundError(name)
    target.mkdir(parents=True, exist_ok=False)
    for name in FILES:
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True)
    print(install(parser.parse_args().target))
