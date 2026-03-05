# Releasing Human++

## Prerequisites

- Write access to the repo
- `VSCE_PAT` and `OVSX_PAT` secrets configured in GitHub (for marketplace publishing)

## Release Steps

### 1. Update sources (not generated files)

All colors flow from `palette.toml` through the build system:

- **VS Code theme**: edit `templates/vscode/human-plus-plus.json.tmpl`
- **Neovim colorscheme**: edit `generate_neovim()` in `tools/build.py`
- **Landing page**: edit `templates/site/index.html.tmpl`
- **README**: edit `templates/README.md.tmpl`

Never edit files in `dist/`, `packages/*/themes/`, or `packages/*/colors/` directly — they are overwritten by `make build`.

### 2. Build and verify

```bash
make build
```

This regenerates all outputs from `palette.toml` and templates. Verify the changes look correct in your editor.

### 3. Update changelog

Edit `CHANGELOG.md` with the new version entry. Follow the existing format (Keep a Changelog style).

### 4. Bump version

Update the version in `pyproject.toml`:

```toml
version = "X.Y.Z"
```

The VS Code extension `package.json` version is updated automatically by the release workflow — do not update it manually.

### 5. Commit and tag

```bash
git add -A
git commit -m "Add feature X, bump to vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

### 6. Automated release (GitHub Actions)

Pushing the tag triggers `.github/workflows/release.yml` which:

1. Updates `packages/vscode-extension/package.json` version from the tag
2. Runs `make build` to regenerate all outputs
3. Syncs changelog to the site template
4. Builds and packages the VS Code extension (`.vsix`)
5. Creates dist archives (`.tar.gz`, `.zip`)
6. Publishes to VS Code Marketplace and Open VSX (Cursor)
7. Creates a GitHub Release with all artifacts
8. Auto-commits the synced package.json and site template back to main

## Version Locations

| File | Updated by |
|---|---|
| `pyproject.toml` | Manual (before tagging) |
| `packages/vscode-extension/package.json` | Automated (release workflow) |
| `site/data/meta.json` | Automated (`make build`) |

## Architecture

```
palette.toml (source of truth)
    |
    v
tools/build.py
    |
    +-> dist/vscode/human-plus-plus.json (from templates/vscode/*.tmpl)
    +-> packages/vscode-extension/themes/human-plus-plus.json (copy)
    +-> packages/neovim-plugin/colors/humanplusplus.lua (generated)
    +-> site/index.html (from templates/site/*.tmpl)
    +-> dist/* (ghostty, tmux, bat, delta, eza, fzf, etc.)
    +-> README.md (from templates/README.md.tmpl)
```
