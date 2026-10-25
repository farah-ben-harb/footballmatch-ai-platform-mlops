#!/usr/bin/env bash
set -euo pipefail

fail() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

for dependency in curl ffmpeg ffprobe; do
    command -v "$dependency" >/dev/null 2>&1 \
        || fail "Missing dependency: $dependency. Install curl and FFmpeg before running this script."
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
output_dir="$repo_root/data/raw"
output_file="$output_dir/match.mp4"
source_url='https://upload.wikimedia.org/wikipedia/commons/7/7d/Girls_football_training.webm'
source_page='https://commons.wikimedia.org/wiki/File:Girls_football_training.webm'
license_url='https://creativecommons.org/licenses/by-sa/3.0/'

[[ ! -e "$output_file" && ! -L "$output_file" ]] \
    || fail "$output_file already exists. Move it aside before downloading another sample."

mkdir -p -- "$output_dir"
work_dir="$(mktemp -d "$output_dir/.sample-video.XXXXXX")"
cleanup() {
    rm -f -- "$work_dir/source.webm" "$work_dir/match.mp4"
    rmdir -- "$work_dir"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

printf 'Downloading a 9.2-second football sample by Evworo (CC BY-SA 3.0).\n'
curl -fL --silent --show-error --retry 2 --connect-timeout 15 --max-time 120 \
    --max-filesize 10000000 --output "$work_dir/source.webm" "$source_url" \
    || fail "Download failed; no match.mp4 was created."

ffmpeg -nostdin -hide_banner -loglevel error -i "$work_dir/source.webm" \
    -map 0:v:0 -t 15 -an -r 25 -c:v libx264 -preset veryfast -crf 23 \
    -pix_fmt yuv420p -movflags +faststart \
    -metadata title='Girls football training - local test sample' \
    -metadata artist='Evworo' \
    -metadata comment="Source: $source_page; License: $license_url; Changes: H.264 MP4 conversion at 25 FPS, audio removed." \
    "$work_dir/match.mp4" \
    || fail "Video conversion failed; no match.mp4 was created."

codec="$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name \
    -of default=noprint_wrappers=1:nokey=1 "$work_dir/match.mp4")" \
    || fail "Unable to inspect the downloaded video."
duration="$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$work_dir/match.mp4")" \
    || fail "Unable to inspect the video duration."
[[ "$codec" == 'h264' ]] || fail "Expected an H.264 video, received: $codec"
awk -v duration="$duration" 'BEGIN { exit !(duration >= 5 && duration <= 15) }' \
    || fail "Expected a 5-15 second clip, received: $duration seconds."

mv -n -- "$work_dir/match.mp4" "$output_file"
[[ ! -e "$work_dir/match.mp4" ]] \
    || fail "Another file appeared at $output_file; it was not overwritten."

printf 'Saved: %s\nSize: %s bytes\nDuration: %s seconds\n' \
    "$output_file" "$(wc -c < "$output_file")" "$duration"
