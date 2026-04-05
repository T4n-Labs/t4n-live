#!/bin/bash
# Auto-detection for Polybar - Clean Version with Functions

POLYBAR_DIR="$HOME/.config/polybar"
SYSTEM_INI="$POLYBAR_DIR/system.ini"
LOG_FILE="$POLYBAR_DIR/auto-detect.log"
mkdir -p "$POLYBAR_DIR"

# Logging function
log() {
    echo "[$(date '+%H:%M:%S')] $*" >> "$LOG_FILE"
    [[ "$1" != "--quiet" ]] && echo "$*"
}

# Function: check and create system.ini if missing or empty
check_system_ini() {
    if [[ ! -f "$SYSTEM_INI" || ! -s "$SYSTEM_INI" ]]; then
        log "system.ini missing or empty. Running full detection."
        run_detection "--force"
        return 0
    fi
    return 1
}

# Function: run detection and write system.ini
run_detection() {
    local mode="${1:-normal}"
    log "=== Starting system detection ($mode) ==="

    # Detect adapter (AC)
    local adapter="AC"
    for path in /sys/class/power_supply/{AC,ADP,ac_adapter,ADP1,ACAD}; do
        if [[ -e "$path" ]]; then
            adapter=$(basename "$path")
            break
        fi
    done
    if [[ "$adapter" == "AC" ]] && command -v upower >/dev/null; then
        local upow=$(upower -e 2>/dev/null | grep -i 'ac\|adapter' | head -1)
        [[ -n "$upow" ]] && adapter=$(basename "$upow")
    fi
    log "Adapter: $adapter"

    # Detect battery
    local battery="BAT0"
    for path in /sys/class/power_supply/BAT*; do
        if [[ -e "$path" ]]; then
            battery=$(basename "$path")
            break
        fi
    done
    if [[ "$battery" == "BAT0" ]] && command -v upower >/dev/null; then
        local upow=$(upower -e 2>/dev/null | grep -i battery | head -1)
        [[ -n "$upow" ]] && battery=$(basename "$upow")
    fi
    log "Battery: $battery"

    # Detect backlight
    local backlight="intel_backlight"
    for path in /sys/class/backlight/*; do
        if [[ -e "$path" ]]; then
            backlight=$(basename "$path")
            break
        fi
    done
    log "Backlight: $backlight"

    # Detect wireless interface
    local wireless="wlp0s20f3"
    if command -v ip >/dev/null; then
        for iface in $(ip link show | awk -F': ' '/^[0-9]+:/ {print $2}'); do
            if [[ -d "/sys/class/net/$iface/wireless" ]]; then
                wireless="$iface"
                break
            fi
        done
    else
        for path in /sys/class/net/*/wireless; do
            if [[ -d "$path" ]]; then
                wireless=$(basename "$(dirname "$path")")
                break
            fi
        done
    fi
    log "Wireless: $wireless"

    # Detect wired interface
    local wired="eth0"
    if command -v ip >/dev/null; then
        for iface in $(ip link show | awk -F': ' '/^[0-9]+:/ {print $2}'); do
            if [[ "$iface" =~ ^(en|eth) ]] && [[ ! -d "/sys/class/net/$iface/wireless" ]]; then
                wired="$iface"
                break
            fi
        done
    else
        for path in /sys/class/net/en* /sys/class/net/eth*; do
            if [[ -e "$path" ]] && [[ ! -d "$path/wireless" ]]; then
                wired=$(basename "$path")
                break
            fi
        done
    fi
    log "Wired: $wired"

    # Backup existing system.ini if any
    [[ -f "$SYSTEM_INI" ]] && cp "$SYSTEM_INI" "$SYSTEM_INI.backup.$(date +%s)" 2>/dev/null

    # Write new system.ini
    cat > "$SYSTEM_INI" <<EOF
# Polybar System Configuration
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# Mode: $mode

[system]
adapter = $adapter
battery = $battery
backlight = $backlight
network_interface_wireless = $wireless
network_interface_wired = $wired
detection_date = $(date '+%Y-%m-%d %H:%M:%S')
detection_mode = $mode
EOF
    chmod 644 "$SYSTEM_INI"
    log "Configuration saved to $SYSTEM_INI"
}

# Main logic
main() {
    case "${1:-}" in
        --quick|-q)
            # Quick mode: only run if system.ini missing/empty or outdated
            if check_system_ini; then
                # Already handled by check_system_ini (ran full detection)
                :
            elif [[ -f "$SYSTEM_INI" ]]; then
                # Check if file is from today
                today=$(date '+%Y%m%d')
                file_date=$(stat -c %y "$SYSTEM_INI" 2>/dev/null | cut -d' ' -f1 | tr -d '-')
                if [[ "$file_date" != "$today" ]]; then
                    log "Quick check: system.ini outdated, updating."
                    run_detection "quick"
                else
                    log "Quick check: system.ini is up to date."
                fi
            fi
            ;;
        --force|-f)
            run_detection "force"
            ;;
        *)
            # Default: check and run if missing/empty
            check_system_ini || run_detection "normal"
            ;;
    esac
}

# Run main with all arguments
main "$@"