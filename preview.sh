#!/usr/bin/env bash
# Human++ Palette Preview - Current vs Proposed
# Run this in your terminal to see the colors side-by-side

# True color support check
if [[ "$COLORTERM" != "truecolor" && "$COLORTERM" != "24bit" ]]; then
    echo "Note: Your terminal may not support true color (24-bit)"
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

echo ""
echo "  ╔═══════════════════════════════════════════════════════════════════════╗"
echo "  ║              Human++ Palette: Current vs Proposed                     ║"
echo "  ╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Current palette
C00="#1b1d20"; C01="#24262a"; C02="#32343a"; C03="#8a7b6b"
C04="#8a8279"; C05="#e5ded6"; C06="#f2ebe4"; C07="#faf5ef"
C08="#d9048e"; C09="#f26c33"; C0A="#f2a633"; C0B="#04b372"
C0C="#1ad0d6"; C0D="#317ad6"; C0E="#8d57ff"; C0F="#bbff00"
C10="#c8518f"; C11="#d68c6f"; C12="#dfb683"; C13="#61b186"
C14="#72d1d5"; C15="#5283c5"; C16="#8f72e3"; C17="#d2fc91"

# Proposed palette (REVISED - cool comments, warm text)
P00="#1a1c22"; P01="#282b31"; P02="#3a3d42"; P03="#5a5d62"
P04="#828079"; P05="#dbd6cc"; P06="#eeeae2"; P07="#f8f6f2"
P08="#e7349c"; P09="#f26c33"; P0A="#f2a633"; P0B="#04b372"
P0C="#1ad0d6"; P0D="#458ae2"; P0E="#9871fe"; P0F="#bbff00"
P10="#c8518f"; P11="#d68c6f"; P12="#dfb683"; P13="#61b186"
P14="#91cbcd"; P15="#5e84b6"; P16="#8f72e3"; P17="#d2fc91"

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  GRAYSCALE (base00-07)                                              │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "              base00    base01    base02    base03    base04    base05    base06    base07"
echo -n "  Current:  "
for hex in "$C00" "$C01" "$C02" "$C03" "$C04" "$C05" "$C06" "$C07"; do
    swatch "$hex"
    echo -n "  "
done
echo ""
echo -n "  Proposed: "
for hex in "$P00" "$P01" "$P02" "$P03" "$P04" "$P05" "$P06" "$P07"; do
    swatch "$hex"
    echo -n "  "
done
echo ""
echo ""

# Show the hex values
echo "  Current hex:"
echo "    $C00  $C01  $C02  $C03  $C04  $C05  $C06  $C07"
echo "  Proposed hex:"
echo "    $P00  $P01  $P02  $P03  $P04  $P05  $P06  $P07"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  base03 (Comments) - Close Up                                       │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "  Current:  "
labeled "$C03"
echo "  ← warm brown (doesn't flow from cool bg)"
echo -n "  Proposed: "
labeled "$P03"
echo "  ← cool gray (AI voice fades into bg)"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  base04 (UI Secondary) - Close Up                                   │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo -n "  Current:  "
labeled "$C04"
echo "  ← L=0.61, warm (too close to base03)"
echo -n "  Proposed: "
labeled "$P04"
echo "  ← L=0.60, neutral (bridges cool→warm)"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  Comments on Background - Readability Test                          │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
# Current
r=$((16#${C00:1:2})); g=$((16#${C00:3:2})); b=$((16#${C00:5:2}))
cr=$((16#${C03:1:2})); cg=$((16#${C03:3:2})); cb=$((16#${C03:5:2}))
printf "  Current:  \033[48;2;%d;%d;%dm  \033[38;2;%d;%d;%dm// This is a comment on the background  \033[0m\n" "$r" "$g" "$b" "$cr" "$cg" "$cb"
# Proposed
r=$((16#${P00:1:2})); g=$((16#${P00:3:2})); b=$((16#${P00:5:2}))
cr=$((16#${P03:1:2})); cg=$((16#${P03:3:2})); cb=$((16#${P03:5:2}))
printf "  Proposed: \033[48;2;%d;%d;%dm  \033[38;2;%d;%d;%dm// This is a comment on the background  \033[0m\n" "$r" "$g" "$b" "$cr" "$cg" "$cb"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  LOUD ACCENTS (base08-0F)                                           │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "              base08    base09    base0A    base0B    base0C    base0D    base0E    base0F"
echo -n "  Current:  "
for hex in "$C08" "$C09" "$C0A" "$C0B" "$C0C" "$C0D" "$C0E" "$C0F"; do
    swatch "$hex"
    echo -n "  "
done
echo ""
echo -n "  Proposed: "
for hex in "$P08" "$P09" "$P0A" "$P0B" "$P0C" "$P0D" "$P0E" "$P0F"; do
    swatch "$hex"
    echo -n "  "
done
echo ""
echo ""
echo "  Changes: base08 (pink), base0D (blue), base0E (purple) lightened for contrast"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  QUIET ACCENTS (base10-17)                                          │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "              base10    base11    base12    base13    base14    base15    base16    base17"
echo -n "  Current:  "
for hex in "$C10" "$C11" "$C12" "$C13" "$C14" "$C15" "$C16" "$C17"; do
    swatch "$hex"
    echo -n "  "
done
echo ""
echo -n "  Proposed: "
for hex in "$P10" "$P11" "$P12" "$P13" "$P14" "$P15" "$P16" "$P17"; do
    swatch "$hex"
    echo -n "  "
done
echo ""
echo ""
echo "  Changes: base14 (cyan), base15 (blue) more desaturated for better loud/quiet distinction"
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  LOUD vs QUIET Side-by-Side                                         │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  Current:"
echo -n "    Loud:  "
for hex in "$C08" "$C09" "$C0A" "$C0B" "$C0C" "$C0D" "$C0E"; do swatch "$hex"; done
echo ""
echo -n "    Quiet: "
for hex in "$C10" "$C11" "$C12" "$C13" "$C14" "$C15" "$C16"; do swatch "$hex"; done
echo ""
echo ""
echo "  Proposed:"
echo -n "    Loud:  "
for hex in "$P08" "$P09" "$P0A" "$P0B" "$P0C" "$P0D" "$P0E"; do swatch "$hex"; done
echo ""
echo -n "    Quiet: "
for hex in "$P10" "$P11" "$P12" "$P13" "$P14" "$P15" "$P16"; do swatch "$hex"; done
echo ""
echo ""

echo "  ┌─────────────────────────────────────────────────────────────────────┐"
echo "  │  MOCK CODE PREVIEW                                                  │"
echo "  └─────────────────────────────────────────────────────────────────────┘"
echo ""

# Mock code with proposed colors
bg=$P00; comment=$P03; keyword=$P10; string=$P12; func=$P13; type=$P14; text=$P05

r=$((16#${bg:1:2})); g=$((16#${bg:3:2})); b=$((16#${bg:5:2}))
BG="\033[48;2;${r};${g};${b}m"

colorize() {
    local hex=$1
    local r=$((16#${hex:1:2})); local g=$((16#${hex:3:2})); local b=$((16#${hex:5:2}))
    printf "\033[38;2;%d;%d;%dm" "$r" "$g" "$b"
}

echo "  Proposed palette mock-up:"
echo ""
printf "${BG}                                                                    \033[0m\n"
printf "${BG}  $(colorize $comment)// !! Critical: rate limiting depends on this cache format     \033[0m\n"
printf "${BG}  $(colorize $keyword)async function $(colorize $func)getUser$(colorize $text)(id: $(colorize $type)string$(colorize $text)): $(colorize $type)Promise$(colorize $text)<$(colorize $type)User$(colorize $text)> {   \033[0m\n"
printf "${BG}    $(colorize $keyword)const $(colorize $text)cached = $(colorize $keyword)await $(colorize $text)redis.get($(colorize $string)\`user:\${id}\`$(colorize $text));            \033[0m\n"
printf "${BG}    $(colorize $comment)// ?? Should we add retry logic here?                         \033[0m\n"
printf "${BG}    $(colorize $keyword)return $(colorize $text)user;                                                    \033[0m\n"
printf "${BG}  }                                                                  \033[0m\n"
printf "${BG}                                                                    \033[0m\n"
echo ""
