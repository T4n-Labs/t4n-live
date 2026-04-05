#!/bin/bash
# ~/.config/picom/auto.sh

CONFIG="$HOME/.config/picom/picom.conf"

# Check if Picom is running
if pgrep -x "picom" >/dev/null; then
    echo "Picom is already running, stop..."
    pkill -x picom
    sleep 0.5
fi

# Make sure the device is completely shutdowm.
while pgrep -x picom >/dev/null; do 
    sleep 0.1
done

# Start picom with config if there is one, if not use default
if [[ -f "$CONFIG" ]]; then
    echo "Starting picom with config..."
    picom --config "$CONFIG" --daemon
else
    echo "Config not found, starting default picom..."
    picom --daemon
fi

exit 0