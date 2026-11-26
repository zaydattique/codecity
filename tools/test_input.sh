#!/usr/bin/env bash
set -euo pipefail
export BLOOMLOGIC_PROFILE_DIR="$(mktemp -d)"
python greenhouse.py --input-test > "$BLOOMLOGIC_PROFILE_DIR/input.log" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; cat "$BLOOMLOGIC_PROFILE_DIR/input.log"' EXIT
wait_marker() {
  for i in $(seq 1 100); do
    grep -q "$1" "$BLOOMLOGIC_PROFILE_DIR/input.log" && return
    kill -0 "$pid" 2>/dev/null || return 1
    sleep .25
  done
  echo "Missing input milestone: $1" >&2; return 1
}
wait_marker 'home ready'
wid=$(xdotool search --onlyvisible --name '^BloomLogic$' | head -1)
xdotool windowfocus --sync "$wid"
click() { xdotool mousemove --window "$wid" "$1" "$2" click 1; sleep .5; }
click 1120 211
wait_marker 'lesson stage ready 0'
click 1000 92
wait_marker 'lesson stage ready 2'
click 1080 186
wait_marker 'editor cleared'
xdotool type --delay 60 'if moisture < 50:'
xdotool key Return
sleep .3
xdotool type --delay 60 'irrigate(True)'
xdotool key Return
sleep .3
xdotool key --delay 120 BackSpace BackSpace BackSpace BackSpace
xdotool type --delay 60 'else:'
xdotool key Return
sleep .3
xdotool type --delay 60 'irrigate(False)'
sleep .5
click 875 504
wait_marker 'Run clicked'
wait "$pid"
grep -q 'OS input test passed' "$BLOOMLOGIC_PROFILE_DIR/input.log"
