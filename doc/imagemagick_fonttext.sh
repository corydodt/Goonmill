#!/bin/bash
if [ "$#" -lt 4 ]; then
    echo 'Usage: '$0' <font> <fontsize> <color> "<message text>"' 1>&2
    exit 1
fi

font="$1"
fontsize="$2"
color="$3"
text="$4"

# FONT="../goonmill/static/3p/vinque.ttf"

filename=$(echo "$text" | tr ' /' '+')

convert -size 800x300 xc:none -font "$font" -fill "$color" -pointsize "$fontsize" \
    -annotate +100+100 "$text" -trim png:- # "$filename".png
