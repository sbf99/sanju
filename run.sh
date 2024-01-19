#!/bin/bash
video_path="`find /media/sbf/ -name 'all_videos.*'`"
##video_path="`find /media/sbf/ -name 'AllVideosTest.*'`"

[[ -z "$video_path" ]] && { echo "No video found. Exiting."; exit 1; }

python ~/SanjuTree/playVideo.py -fs --video=$video_path
