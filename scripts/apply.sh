#!/bin/bash
# Human++ Cool Balanced - Apply theme to all apps
# GENERATED FROM palette.toml — paths reference dist/ outputs
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$ROOT_DIR/dist"
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run|-n]"
            exit 1
            ;;
    esac
done

log() {
    echo "  → $1"
}

run() {
    if $DRY_RUN; then
        echo "  [dry-run] $*"
    else
        "$@"
    fi
}

echo "Applying Human++ Cool Balanced theme..."
if $DRY_RUN; then
    echo "(dry-run mode - no changes will be made)"
fi
echo ""

# Sketchybar
if command -v sketchybar &> /dev/null; then
    log "Reloading sketchybar..."
    if ! $DRY_RUN; then
        # shellcheck source=/dev/null
        source "$DIST_DIR/sketchybar/colors.sh"
        sketchybar --reload
    fi
fi

# JankyBorders
if command -v borders &> /dev/null; then
    log "Applying borders..."
    if ! $DRY_RUN; then
        # shellcheck source=/dev/null
        source "$DIST_DIR/borders/bordersrc"
    fi
fi

# Ghostty
if [ -d "$HOME/.config/ghostty" ]; then
    log "Updating ghostty theme..."
    run mkdir -p "$HOME/.config/ghostty/themes"
    run cp "$DIST_DIR/ghostty/config" "$HOME/.config/ghostty/themes/human-plus-plus"
    echo "     (Restart ghostty or run: ghostty +reload-config)"
fi

# Vim/Neovim (via tinty)
TINTY_VIM="$HOME/.local/share/tinted-theming/tinty/repos/tinted-vim/colors/base24-human-plus-plus.vim"
if [ -f "$TINTY_VIM" ]; then
    if [ -d "$HOME/.vim/colors" ]; then
        log "Updating vim colorscheme..."
        run cp "$TINTY_VIM" "$HOME/.vim/colors/humanplusplus.vim"
    fi
    if [ -d "$HOME/.config/nvim" ]; then
        log "Updating neovim colorscheme..."
        run mkdir -p "$HOME/.config/nvim/colors"
        run cp "$TINTY_VIM" "$HOME/.config/nvim/colors/humanplusplus.vim"
    fi
else
    log "Vim theme not found (run 'make build' with tinty installed)"
fi

# Cursor - find latest tinted-themes extension version
if [ -d "$HOME/.cursor/extensions" ]; then
    # Find the latest matching extension directory
    CURSOR_EXT=$(find "$HOME/.cursor/extensions" -maxdepth 1 -type d -name "tintedtheming.base16-tinted-themes-*" 2>/dev/null | sort -V | tail -n1)

    if [ -n "$CURSOR_EXT" ] && [ -d "$CURSOR_EXT/themes/base16" ]; then
        log "Updating Cursor theme ($(basename "$CURSOR_EXT"))..."
        if [ -f "$DIST_DIR/vscode/humanpp-cool-balanced.json" ]; then
            run cp "$DIST_DIR/vscode/humanpp-cool-balanced.json" "$CURSOR_EXT/themes/base16/humanpp-cool-balanced.json"
        fi
    else
        log "Cursor tinted-themes extension not found, skipping..."
    fi
fi

# VS Code - same approach
if [ -d "$HOME/.vscode/extensions" ]; then
    VSCODE_EXT=$(find "$HOME/.vscode/extensions" -maxdepth 1 -type d -name "tintedtheming.base16-tinted-themes-*" 2>/dev/null | sort -V | tail -n1)

    if [ -n "$VSCODE_EXT" ] && [ -d "$VSCODE_EXT/themes/base16" ]; then
        log "Updating VS Code theme ($(basename "$VSCODE_EXT"))..."
        if [ -f "$DIST_DIR/vscode/humanpp-cool-balanced.json" ]; then
            run cp "$DIST_DIR/vscode/humanpp-cool-balanced.json" "$VSCODE_EXT/themes/base16/humanpp-cool-balanced.json"
        fi
    fi
fi

echo ""
echo "Done! Some apps may need restart to pick up changes."
