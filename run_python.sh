#!/bin/bash
ulimit -n 65536

BASENAME="$(basename "$1")"

LOGDIR="logs/${2:-${BASENAME%.*}}"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/$(date +"%Y-%m-%d_%H-%M-%S").log"

screen -dmS "$BASENAME" -L -Logfile "$LOGFILE" -- python "$1"
