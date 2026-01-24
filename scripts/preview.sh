#!/usr/bin/env bash
# Human++ Palette Preview
# Displays the current palette from palette.toml with detailed visualization
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PALETTE_FILE="${1:-$ROOT_DIR/palette.toml}"

if [ ! -f "$PALETTE_FILE" ]; then
    echo "Error: Palette file not found: $PALETTE_FILE"
    echo "Usage: $0 [palette.toml]"
    exit 1
fi

# True color support check
if [[ "$COLORTERM" != "truecolor" && "$COLORTERM" != "24bit" ]]; then
    echo "Note: Your terminal may not support true color (24-bit)"
fi

# Parse palette.toml - extract baseXX = "#xxxxxx" lines
declare -A PALETTE
while IFS= read -r line; do
    # Match lines like: base00 = "#1a1c22"
    if [[ $line =~ ^[[:space:]]*(base[0-9A-Fa-f]+)[[:space:]]*=[[:space:]]*\"(#[0-9A-Fa-f]{6})\" ]]; then
        PALETTE["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
    fi
done < "$PALETTE_FILE"

# Verify we got the palette
if [ ${#PALETTE[@]} -lt 24 ]; then
    echo "Warning: Only found ${#PALETTE[@]} colors in palette (expected 24)"
fi

# Helper to print a colored block
swatch() {
    local hex="$1"
    local r=$((16#${hex:1:2}))
    local g=$((16#${hex:3:2}))
    local b=$((16#${hex:5:2}))
    printf "\033[48;2;%d;%d;%dm      \033[0m" "$r" "$g" "$b"
}

# Helper to print hex inside colored block
labeled() {
    local hex="$1"
    local r=$((16#${hex:1:2}))
    local g=$((16#${hex:3:2}))
    local b=$((16#${hex:5:2}))
    # Use black or white text based on luminance
    local lum=$(( (r*299 + g*587 + b*114) / 1000 ))
    if [ $lum -gt 128 ]; then
        printf "\033[48;2;%d;%d;%dm\033[30m%s\033[0m" "$r" "$g" "$b" "$hex"
    else
        printf "\033[48;2;%d;%d;%dm\033[97m%s\033[0m" "$r" "$g" "$b" "$hex"
    fi
}

# Helper to apply foreground color
fg() {
    local hex="$1"
    local r=$((16#${hex:1:2}))
    local g=$((16#${hex:3:2}))
    local b=$((16#${hex:5:2}))
    printf "\033[38;2;%d;%d;%dm" "$r" "$g" "$b"
}

# Helper to apply background color
bg() {
    local hex="$1"
    local r=$((16#${hex:1:2}))
    local g=$((16#${hex:3:2}))
    local b=$((16#${hex:5:2}))
    printf "\033[48;2;%d;%d;%dm" "$r" "$g" "$b"
}

reset="\033[0m"

echo ""
echo "  ╔═══════════════════════════════════════════════════════════════════════╗"
echo "  ║                          Human++ Palette                              ║"
echo "  ║                  Code is cheap. Intent is scarce.                     ║"
echo "  ╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Reading from: $PALETTE_FILE"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  GRAYSCALE (base00-07)                                              │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "              base00    base01    base02    base03    base04    base05    base06    base07"
echo -n "  Colors:   "
for i in 0 1 2 3 4 5 6 7; do
    slot="base0$i"
    swatch "${PALETTE[$slot]}"
    echo -n "  "
done
echo ""
echo ""

# Show hex values
echo -n "  Hex:      "
for i in 0 1 2 3 4 5 6 7; do
    slot="base0$i"
    printf "%-10s" "${PALETTE[$slot]}"
done
echo ""
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  base03 (Comments) - AI Voice                                       │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "  "
labeled "${PALETTE[base03]}"
echo "  ← cool gray (fades into background)"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  Comments on Background - Readability Test                          │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
printf "  $(bg "${PALETTE[base00]}")  $(fg "${PALETTE[base03]}")// This is a comment on the background  $reset\n"
printf "  $(bg "${PALETTE[base00]}")  $(fg "${PALETTE[base05]}")// This is main text (base05)           $reset\n"
printf "  $(bg "${PALETTE[base00]}")  $(fg "${PALETTE[base04]}")// This is UI secondary (base04)        $reset\n"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  LOUD ACCENTS (base08-0F) — Diagnostics & Signals                   │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "              base08    base09    base0A    base0B    base0C    base0D    base0E    base0F"
echo -n "  Colors:   "
for slot in base08 base09 base0A base0B base0C base0D base0E base0F; do
    swatch "${PALETTE[$slot]}"
    echo -n "  "
done
echo ""
echo -n "  Hex:      "
for slot in base08 base09 base0A base0B base0C base0D base0E base0F; do
    printf "%-10s" "${PALETTE[$slot]}"
done
echo ""
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  QUIET ACCENTS (base10-17) — Syntax & UI                            │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "              base10    base11    base12    base13    base14    base15    base16    base17"
echo -n "  Colors:   "
for slot in base10 base11 base12 base13 base14 base15 base16 base17; do
    swatch "${PALETTE[$slot]}"
    echo -n "  "
done
echo ""
echo -n "  Hex:      "
for slot in base10 base11 base12 base13 base14 base15 base16 base17; do
    printf "%-10s" "${PALETTE[$slot]}"
done
echo ""
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  LOUD vs QUIET Side-by-Side                                         │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "  Loud:   "
for slot in base08 base09 base0A base0B base0C base0D base0E; do
    swatch "${PALETTE[$slot]}"
done
echo ""
echo -n "  Quiet:  "
for slot in base10 base11 base12 base13 base14 base15 base16; do
    swatch "${PALETTE[$slot]}"
done
echo ""
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  MOCK CODE PREVIEW                                                  │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""

# Colors for mock code
bg_color="${PALETTE[base00]}"
comment="${PALETTE[base03]}"
keyword="${PALETTE[base10]}"
string="${PALETTE[base12]}"
func="${PALETTE[base13]}"
type="${PALETTE[base14]}"
text="${PALETTE[base05]}"

printf "$(bg "$bg_color")                                                                    $reset\n"
printf "$(bg "$bg_color")  $(fg "$comment")// !! Critical: rate limiting depends on this cache format     $reset\n"
printf "$(bg "$bg_color")  $(fg "$keyword")async function $(fg "$func")getUser$(fg "$text")(id: $(fg "$type")string$(fg "$text")): $(fg "$type")Promise$(fg "$text")<$(fg "$type")User$(fg "$text")> {   $reset\n"
printf "$(bg "$bg_color")    $(fg "$keyword")const $(fg "$text")cached = $(fg "$keyword")await $(fg "$text")redis.get($(fg "$string")\\\`user:\\\${id}\\\`$(fg "$text"));            $reset\n"
printf "$(bg "$bg_color")    $(fg "$comment")// ?? Should we add retry logic here?                         $reset\n"
printf "$(bg "$bg_color")    $(fg "$keyword")return $(fg "$text")user;                                                    $reset\n"
printf "$(bg "$bg_color")  }                                                                  $reset\n"
printf "$(bg "$bg_color")                                                                    $reset\n"
echo ""
