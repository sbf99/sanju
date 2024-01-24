#!/bin/bash
video_path="`find /media/sbf/ -iname 'sanju*mp4'`"

[[ -z "$video_path" ]] && { echo "No video found. Exiting."; exit 1; }

python ~/SanjuTree/playVideo.py -fs --video="$video_path"
