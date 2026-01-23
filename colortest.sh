#!/usr/bin/env bash
# Human++ Color Test
# Displays the current terminal palette and Human++ color values

# Force bash 4+ features
if [ -z "$BASH_VERSION" ] || [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "This script requires bash 4.0 or later"
    exit 1
fi

cat << 'HEADER'

  ╔═══════════════════════════════════════════════════════════════════╗
  ║                       Human++ Cool Balanced                       ║
  ║           Code is cheap. Intent is scarce.                        ║
  ╚═══════════════════════════════════════════════════════════════════╝

HEADER

# Display ANSI 0-15 (what your terminal actually shows)
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  TERMINAL ANSI COLORS (0-15)                                    │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "   Normal:  "
for i in 0 1 2 3 4 5 6 7; do
  printf "\033[48;5;${i}m   \033[0m"
done
echo ""
echo -n "   Bright:  "
for i in 8 9 10 11 12 13 14 15; do
  printf "\033[48;5;${i}m   \033[0m"
done
echo ""
echo ""

# Detailed view
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  ANSI TO BASE24 MAPPING                                         │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
printf "   %-5s %-12s %-8s %-10s %s\n" "ANSI" "Name" "Slot" "Hex" ""
printf "   %-5s %-12s %-8s %-10s %s\n" "────" "────" "────" "───" ""

# ANSI to base24 mapping (Human++ terminal style: LOUD normal, QUIET bright)
print_row() {
  local ansi=$1 name=$2 slot=$3 hex=$4
  printf "   %-5s %-12s %-8s %-10s \033[48;5;${ansi}m      \033[0m\n" "$ansi" "$name" "$slot" "$hex"
}

print_row 0  "Black"       "base00" "#1b1d20"
print_row 1  "Red"         "base08" "#d9048e"
print_row 2  "Green"       "base0B" "#04b372"
print_row 3  "Yellow"      "base0A" "#f2a633"
print_row 4  "Blue"        "base0D" "#317ad6"
print_row 5  "Magenta"     "base0E" "#8d57ff"
print_row 6  "Cyan"        "base0C" "#1ad0d6"
print_row 7  "White"       "base06" "#f2ebe4"
print_row 8  "Br.Black"    "base03" "#8a7b6b"
print_row 9  "Br.Red"      "base10" "#c8518f"
print_row 10 "Br.Green"    "base13" "#61b186"
print_row 11 "Br.Yellow"   "base12" "#dfb683"
print_row 12 "Br.Blue"     "base15" "#5283c5"
print_row 13 "Br.Magenta"  "base16" "#8f72e3"
print_row 14 "Br.Cyan"     "base14" "#72d1d5"
print_row 15 "Br.White"    "base07" "#faf5ef"
echo ""

# Extended colors 16-21
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  EXTENDED PALETTE (16-21)                                       │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
print_row 16 "Extra 1"     "base09" "#f26c33"
print_row 17 "Extra 2"     "base0F" "#bbff00"
print_row 18 "Extra 3"     "base01" "#24262a"
print_row 19 "Extra 4"     "base02" "#32343a"
print_row 20 "Extra 5"     "base04" "#8a8279"
print_row 21 "Extra 6"     "base05" "#e5ded6"
echo ""

# Full palette reference
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  HUMAN++ FULL PALETTE                                           │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo "   GRAYSCALE"
printf "   base00 #1b1d20 background    base04 #8a8279 UI secondary\n"
printf "   base01 #24262a elevation     base05 #e5ded6 main text\n"
printf "   base02 #32343a selection     base06 #f2ebe4 emphasis\n"
printf "   base03 #8a7b6b comments      base07 #faf5ef brightest\n"
echo ""
echo "   LOUD ACCENTS — Diagnostics & Signals"
printf "   base08 #d9048e errors        base0C #1ad0d6 info\n"
printf "   base09 #f26c33 warnings      base0D #317ad6 links\n"
printf "   base0A #f2a633 caution       base0E #8d57ff special\n"
printf "   base0B #04b372 success       base0F #bbff00 human !!\n"
echo ""
echo "   QUIET ACCENTS — Syntax & UI"
printf "   base10 #c8518f keywords      base14 #72d1d5 types\n"
printf "   base11 #d68c6f secondary     base15 #5283c5 hints\n"
printf "   base12 #dfb683 strings       base16 #8f72e3 constants\n"
printf "   base13 #61b186 functions     base17 #d2fc91 quiet lime\n"
echo ""

# Visual comparison
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  LOUD vs QUIET COMPARISON                                       │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "   Loud:   "
for i in 1 3 2 4 5 6; do
  printf "\033[48;5;${i}m    \033[0m"
done
echo "  ← base08-0E (LOUD)"

echo -n "   Quiet:  "
for i in 9 11 10 12 13 14; do
  printf "\033[48;5;${i}m    \033[0m"
done
echo "  ← base10-16 (quiet)"
echo ""

# Color blocks
echo "  ┌─────────────────────────────────────────────────────────────────┐"
echo "  │  ALL 16 COLORS                                                  │"
echo "  └─────────────────────────────────────────────────────────────────┘"
echo ""
for row in 0 1; do
  echo -n "   "
  for col in 0 1 2 3 4 5 6 7; do
    i=$((row * 8 + col))
    printf "\033[48;5;${i}m       \033[0m"
  done
  echo ""
  echo -n "   "
  for col in 0 1 2 3 4 5 6 7; do
    i=$((row * 8 + col))
    printf "\033[48;5;${i}m       \033[0m"
  done
  echo ""
  echo ""
done
