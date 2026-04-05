#!/bin/bash
# Polybar launcher with multi-monitor auto-detection

CONFIG_DIR="$HOME/.config/polybar"
CONFIG="$CONFIG_DIR/config.ini"
SYSTEM_INI="$CONFIG_DIR/system.ini"
DETECT_SCRIPT="$CONFIG_DIR/detection.sh"

# Kill existing polybar instances
killall -q polybar
while pgrep -u "$UID" -x polybar >/dev/null; do sleep 0.5; done

# Ensure detection script exists and is executable
if [[ ! -x "$DETECT_SCRIPT" ]]; then
    echo "Making detection script executable..."
    chmod +x "$DETECT_SCRIPT" 2>/dev/null || { echo "Detection script missing"; exit 1; }
fi

# Run detection: force if system.ini missing, otherwise quick
if [[ ! -f "$SYSTEM_INI" ]]; then
    echo "No system.ini found, running full detection..."
    "$DETECT_SCRIPT" --force || exit 1
else
    echo "Running quick system check..."
    "$DETECT_SCRIPT" --quick
fi

# Verify system.ini exists
[[ -f "$SYSTEM_INI" ]] || { echo "system.ini still missing"; exit 1; }

# Detect monitors with xrandr
if command -v xrandr &>/dev/null; then
    primary=$(xrandr --query | awk '/ connected.*primary/ {print $1}')
    connected=$(xrandr --query | awk '/ connected/ {print $1}')
else
    echo "xrandr not found, launching on default monitor"
    polybar -c "$CONFIG" --reload main &
    exit 0
fi

# Launch polybar on each monitor
if [[ -n "$primary" ]]; then
    echo "Primary: $primary"
    MONITOR=$primary polybar -c "$CONFIG" --reload main &
    sleep 0.3
    # Launch secondary on other monitors
    for mon in $connected; do
        [[ "$mon" == "$primary" ]] && continue
        echo "Secondary: $mon"
        MONITOR=$mon polybar -c "$CONFIG" --reload secondary &
        sleep 0.3
    done
else
    # No primary, treat first as main, rest as secondary
    set -- $connected
    main=$1; shift
    echo "Main: $main"
    MONITOR=$main polybar -c "$CONFIG" --reload main &
    sleep 0.3
    for mon; do
        echo "Secondary: $mon"
        MONITOR=$mon polybar -c "$CONFIG" --reload secondary &
        sleep 0.3
    done
fi

# Verify launch
sleep 1
count=$(pgrep -u "$UID" -c polybar)
if (( count > 0 )); then
    echo "Polybar launched ($count instances)"
else
    echo "Failed to launch polybar"
    exit 1
fi