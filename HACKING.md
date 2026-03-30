# Hacking on HackerTray

## Development Setup

```bash
git clone --recurse-submodules https://github.com/captn3m0/hackertray.git
cd hackertray
uv run --with pytest python -m pytest
```

## Flatpak

### Build

```bash
flatpak install flathub org.gnome.Platform//49 org.gnome.Sdk//49
flatpak-builder --install-deps-from=flathub --force-clean build-dir in.captnemo.hackertray.yml
```

### Install locally

```bash
flatpak-builder --user --install --force-clean build-dir in.captnemo.hackertray.yml
flatpak run in.captnemo.hackertray
```

### Install from remote flatpakref (once published)

A single-file flatpakref is hosted on GitHub Pages:

```bash
flatpak install https://captnemo.in/hackertray/hackertray.flatpakref
```

### Publish

**WIP**: Not published anywhere yet.

The Flatpak is built as a single-file bundle and attached to GitHub Releases. To generate a bundle locally:

```bash
flatpak-builder --repo=repo --force-clean build-dir in.captnemo.hackertray.yml
flatpak build-bundle repo hackertray.flatpak in.captnemo.hackertray
```

Install from the bundle:

```bash
flatpak install hackertray.flatpak
```

## Release

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit and tag: `git tag x.y.z && git push --tags`
4. PyPI publish happens automatically via GitHub Actions (trusted publishing)
5. Build and attach Flatpak bundle to the GitHub Release
