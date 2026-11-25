#!/usr/bin/env bash
set -euo pipefail
export BLOOMLOGIC_PROFILE_DIR="$(mktemp -d)"
python greenhouse.py --input-test > "$BLOOMLOGIC_PROFILE_DIR/input.log" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; cat "$BLOOMLOGIC_PROFILE_DIR/input.log"' EXIT
for i in $(seq 1 80); do
  if grep -q 'home ready' "$BLOOMLOGIC_PROFILE_DIR/input.log"; then break; fi
  sleep .25
done
wid=$(xdotool search --onlyvisible --name '^BloomLogic$' | head -1)
xdotool windowfocus --sync "$wid"
xdotool mousemove --window "$wid" 1120 211 click 1
for i in $(seq 1 100); do
  if grep -q 'scene ready' "$BLOOMLOGIC_PROFILE_DIR/input.log"; then break; fi
  sleep .25
done
sleep 1
xdotool mousemove --window "$wid" 1000 92 click 1
sleep .5
xdotool mousemove --window "$wid" 950 226 click 1 key ctrl+shift+BackSpace
xdotool type --clearmodifiers 'if moisture < 50:'
xdotool key Return
xdotool type 'irrigate(True)'
xdotool key Return BackSpace BackSpace BackSpace BackSpace
xdotool type 'else:'
xdotool key Return
xdotool type 'irrigate(False)'
xdotool mousemove --window "$wid" 875 504 click 1
wait "$pid"
grep -q 'OS input test passed' "$BLOOMLOGIC_PROFILE_DIR/input.log"
