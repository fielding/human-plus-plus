#!/usr/bin/env sh
# tinted-shell (https://github.com/tinted-theming/tinted-shell)
# Scheme name: Human++ Cool Balanced
# Scheme author: fielding
# Template author: Tinted Theming (https://github.com/tinted-theming)
export BASE24_THEME="human-plus-plus"

color00="1a/1c/22" # Base 00 - Black
color01="e7/34/9c" # Base 08 - Red
color02="04/b3/72" # Base 0B - Green
color03="f2/a6/33" # Base 0A - Yellow
color04="45/8a/e2" # Base 0D - Blue
color05="98/71/fe" # Base 0E - Magenta
color06="1a/d0/d6" # Base 0C - Cyan
color07="db/d6/cc" # Base 05 - White
color08="5a/5d/62" # Base 03 - Bright Black
color09="df/b6/83" # Base 12 - Bright Red
color10="91/cb/cd" # Base 14 - Bright Green
color11="61/b1/86" # Base 13 - Bright Yellow
color12="8f/72/e3" # Base 16 - Bright Blue
color13="d2/fc/91" # Base 17 - Bright Magenta
color14="5e/84/b6" # Base 15 - Bright Cyan
color15="f8/f6/f2" # Base 07 - Bright White
color16="f2/6c/33" # Base 09
color17="bb/ff/00" # Base 0F
color18="28/2b/31" # Base 01
color19="3a/3d/42" # Base 02
color20="82/80/79" # Base 04
color21="ee/ea/e2" # Base 06
color_foreground="db/d6/cc" # Base 05
color_background="1a/1c/22" # Base 00


if [ -z "$TTY" ] && ! TTY=$(tty) || [ ! -w "$TTY" ]; then
  put_template() { true; }
  put_template_var() { true; }
  put_template_custom() { true; }
elif [ -n "$TMUX" ] || [ "${TERM%%[-.]*}" = "tmux" ]; then
  # Tell tmux to pass the escape sequences through
  # (Source: http://permalink.gmane.org/gmane.comp.terminal-emulators.tmux.user/1324)
  put_template() { printf '\033Ptmux;\033\033]4;%d;rgb:%s\033\033\\\033\\' "$@" > "$TTY"; }
  put_template_var() { printf '\033Ptmux;\033\033]%d;rgb:%s\033\033\\\033\\' "$@" > "$TTY"; }
  put_template_custom() { printf '\033Ptmux;\033\033]%s%s\033\033\\\033\\' "$@" > "$TTY"; }
elif [ "${TERM%%[-.]*}" = "screen" ]; then
  # GNU screen (screen, screen-256color, screen-256color-bce)
  put_template() { printf '\033P\033]4;%d;rgb:%s\007\033\\' "$@" > "$TTY"; }
  put_template_var() { printf '\033P\033]%d;rgb:%s\007\033\\' "$@" > "$TTY"; }
  put_template_custom() { printf '\033P\033]%s%s\007\033\\' "$@" > "$TTY"; }
elif [ "${TERM%%-*}" = "linux" ]; then
  put_template() { [ "$1" -lt 16 ] && printf "\e]P%x%s" "$1" "$(echo "$2" | sed 's/\///g')" > "$TTY"; }
  put_template_var() { true; }
  put_template_custom() { true; }
else
  put_template() { printf '\033]4;%d;rgb:%s\033\\' "$@" > "$TTY"; }
  put_template_var() { printf '\033]%d;rgb:%s\033\\' "$@" > "$TTY"; }
  put_template_custom() { printf '\033]%s%s\033\\' "$@" > "$TTY"; }
fi

# 16 color space
put_template 0  "$color00"
put_template 1  "$color01"
put_template 2  "$color02"
put_template 3  "$color03"
put_template 4  "$color04"
put_template 5  "$color05"
put_template 6  "$color06"
put_template 7  "$color07"
put_template 8  "$color08"
put_template 9  "$color09"
put_template 10 "$color10"
put_template 11 "$color11"
put_template 12 "$color12"
put_template 13 "$color13"
put_template 14 "$color14"
put_template 15 "$color15"

# foreground / background / cursor color
if [ -n "$ITERM_SESSION_ID" ]; then
  # iTerm2 proprietary escape codes
  put_template_custom Pg dbd6cc # foreground
  put_template_custom Ph 1a1c22 # background
  put_template_custom Pi dbd6cc # bold color
  put_template_custom Pj 3a3d42 # selection color
  put_template_custom Pk dbd6cc # selected text color
  put_template_custom Pl dbd6cc # cursor
  put_template_custom Pm 1a1c22 # cursor text
else
  put_template_var 10 "$color_foreground"
  if [ "$BASE24_SHELL_SET_BACKGROUND" != false ]; then
    put_template_var 11 "$color_background"
    if [ "${TERM%%-*}" = "rxvt" ]; then
      put_template_var 708 "$color_background" # internal border (rxvt)
    fi
  fi
  put_template_custom 12 ";7" # cursor (reverse video)
fi

# clean up
unset put_template
unset put_template_var
unset put_template_custom
unset color00
unset color01
unset color02
unset color03
unset color04
unset color05
unset color06
unset color07
unset color08
unset color09
unset color10
unset color11
unset color12
unset color13
unset color14
unset color16
unset color17
unset color18
unset color19
unset color20
unset color21
unset color15
unset color_foreground
unset color_background

# Optionally export variables
if [ -n "$TINTED_SHELL_ENABLE_BASE24_VARS" ]; then
  export BASE24_COLOR_00_HEX="1a1c22"
  export BASE24_COLOR_01_HEX="282b31"
  export BASE24_COLOR_02_HEX="3a3d42"
  export BASE24_COLOR_03_HEX="5a5d62"
  export BASE24_COLOR_04_HEX="828079"
  export BASE24_COLOR_05_HEX="dbd6cc"
  export BASE24_COLOR_06_HEX="eeeae2"
  export BASE24_COLOR_07_HEX="f8f6f2"
  export BASE24_COLOR_08_HEX="e7349c"
  export BASE24_COLOR_09_HEX="f26c33"
  export BASE24_COLOR_0A_HEX="f2a633"
  export BASE24_COLOR_0B_HEX="04b372"
  export BASE24_COLOR_0C_HEX="1ad0d6"
  export BASE24_COLOR_0D_HEX="458ae2"
  export BASE24_COLOR_0E_HEX="9871fe"
  export BASE24_COLOR_0F_HEX="bbff00"
  export BASE24_COLOR_10_HEX="c8518f"
  export BASE24_COLOR_11_HEX="d68c6f"
  export BASE24_COLOR_12_HEX="dfb683"
  export BASE24_COLOR_13_HEX="61b186"
  export BASE24_COLOR_14_HEX="91cbcd"
  export BASE24_COLOR_15_HEX="5e84b6"
  export BASE24_COLOR_16_HEX="8f72e3"
  export BASE24_COLOR_17_HEX="d2fc91"
fi
