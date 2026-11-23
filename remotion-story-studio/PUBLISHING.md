# Public distribution

This document is a procedure, not evidence of publication.

Create a dedicated public repository `remotion-story-studio` in the maintainer account. Do not change any existing private repository's visibility or publish user source folders. Include only this package's allowlisted files.

1. Run `python scripts/verify_package.py`, `python -m unittest discover -s tests -v`, clean example install, typecheck and two MP4 renders.
2. Run `python scripts/package.py --output ../dist` to make a versioned ZIP and SHA256.
3. Push this source to the dedicated repository. Create GitHub Release v0.1.0 containing ZIP and SHA256.
4. Download the public ZIP without authentication, verify its hash and rerun the example from the extracted package.
5. Record actual repo URL, commit, release URL, hash and test evidence in a release record. A local ZIP is not a public release.

With an authenticated GitHub CLI:
```sh
git init -b main
git add .
git commit -m "Release Remotion Story Studio 0.1.0"
gh repo create remotion-story-studio --public --source . --remote origin --push
gh release create v0.1.0 ../dist/remotion-story-studio-v0.1.0.zip ../dist/remotion-story-studio-v0.1.0.sha256 --title "Remotion Story Studio 0.1.0"
```
If the available connector cannot create repositories/releases and no CLI/API authentication exists, finish the package and accurately report that publishing is blocked. Do not substitute an unrelated existing repository.
