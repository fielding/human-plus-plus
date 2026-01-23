#!/bin/bash
# Human++ Cool Balanced - Apply theme to all apps

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Applying Human++ Cool Balanced theme..."

# Source sketchybar colors and reload
if command -v sketchybar &> /dev/null; then
    echo "  → Reloading sketchybar..."
    source "$SCRIPT_DIR/sketchybar/colors.sh"
    sketchybar --reload
fi

# Source borders config
if command -v borders &> /dev/null; then
    echo "  → Applying borders..."
    source "$SCRIPT_DIR/borders/bordersrc"
fi

# Copy ghostty config to ghostty config dir
if [ -d "$HOME/.config/ghostty" ]; then
    echo "  → Updating ghostty theme..."
    cp "$SCRIPT_DIR/ghostty/config" "$HOME/.config/ghostty/themes/human-plus-plus"
    echo "     (Restart ghostty or run: ghostty +reload-config)"
fi

# Copy vim colorscheme
if [ -d "$HOME/.vim/colors" ]; then
    echo "  → Updating vim colorscheme..."
    cp "$SCRIPT_DIR/vim/colors/humanplusplus.vim" "$HOME/.vim/colors/"
fi

# Neovim
if [ -d "$HOME/.config/nvim/colors" ]; then
    echo "  → Updating neovim colorscheme..."
    cp "$SCRIPT_DIR/vim/colors/humanplusplus.vim" "$HOME/.config/nvim/colors/"
fi

# Copy VS Code theme to Cursor
CURSOR_THEME_DIR="$HOME/.cursor/extensions/tintedtheming.base16-tinted-themes-0.34.0-universal/themes/base16"
if [ -d "$CURSOR_THEME_DIR" ]; then
    echo "  → Updating Cursor theme..."
    # Look for the latest base-cool-balanced JSON
    if [ -f "$SCRIPT_DIR/base-cool-balanced-v2.json" ]; then
        cp "$SCRIPT_DIR/base-cool-balanced-v2.json" "$CURSOR_THEME_DIR/human-plus-plus-cool-balanced-v2.json"
    fi
fi

echo "Done! Some apps may need restart to pick up changes."
