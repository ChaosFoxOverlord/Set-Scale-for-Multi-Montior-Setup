#!/usr/bin/python3

# Based on https://askubuntu.com/questions/1035718/how-change-display-scale-from-the-command-line-in-ubuntu-18-04-xorg
# and https://gist.github.com/strycore/ca11203fd63cafcac76d4b04235d8759
# For data structure definitions, see
# https://gitlab.gnome.org/GNOME/mutter/blob/master/src/org.gnome.Mutter.DisplayConfig.xml

# Note: use system python3, not /usr/bin/env, because whichever python3 is on
# $PATH may not have dbus, but the system python3 does.
import dbus
import sys

# --- CONFIGURATION ---
# Here you can specify your monitors and the desired factors.
# You can find out the names (e.g., ‘eDP-1’) by running the script once
# or typing ‘xrandr’ in the terminal.
SCALE_MAP = {
    #"eDP-1": 2.0,  # Internal laptop display
    #"HDMI-1-0": 2.0 # External monitor
}
try:
    DEFAULT_SCALE = float(sys.argv[1])
except IndexError:
    DEFAULT_SCALE = 1.0
# ---------------------

namespace = "org.gnome.Mutter.DisplayConfig"
dbus_path = "/org/gnome/Mutter/DisplayConfig"

try:
    session_bus = dbus.SessionBus()
    obj = session_bus.get_object(namespace, dbus_path)
    interface = dbus.Interface(obj, dbus_interface=namespace)
except dbus.DBusException as e:
    print(f"Error: Could not connect to DBus interface: {e}")
    sys.exit(1)

# Get current state from Mutter
serial, connected_monitors, logical_monitors, properties = interface.GetCurrentState()

# --- AUTO-DISCOVERY BLOCK ---
# Print available monitor connectors to make configuration easier
print("Detected monitors:")
for monitor in connected_monitors:
    # monitor[0][0] is the connector name (e.g., 'eDP-1')
    connector = monitor[0][0]
    # Check if it's currently used in logical_monitors
    is_active = any(connector in str(l_mon[5]) for l_mon in logical_monitors)
    status = "Active" if is_active else "Inactive"
    print(f"  - {connector} ({status})")
print("-" * 20)
# ----------------------------

def get_current_mode_id(connector_name):
    """Finds the active mode ID for a given connector name."""
    for monitor in connected_monitors:
        if monitor[0][0] == connector_name:
            for mode in monitor[1]:
                if mode[6].get("is-current", False):
                    return mode[0]
    return None

new_logical_monitors = []

# Reconstruct the configuration for each logical monitor
for l_mon in logical_monitors:
    x, y, scale, transform, primary, monitors_info, props = l_mon
    
    updated_connectors = []
    target_scale = None

    for m_info in monitors_info:
        connector_name = m_info[0]
        mode_id = get_current_mode_id(connector_name)
        
        if mode_id:
            updated_connectors.append([connector_name, mode_id, {}])
            
            # Match scaling factor from SCALE_MAP
            if target_scale is None:
                target_scale = SCALE_MAP.get(connector_name, DEFAULT_SCALE)

    # Apply specific scale or keep current
    final_scale = float(target_scale if target_scale is not None else scale)
    new_logical_monitors.append([x, y, final_scale, transform, primary, updated_connectors])

try:
    # Apply settings immediately (method=1)
    # If this fails with InvalidArgs, the OS/Window Manager does not support mixed scaling.
    interface.ApplyMonitorsConfig(serial, 1, new_logical_monitors, {})
    print("Scaling configuration applied successfully.")
except dbus.DBusException as e:
    print(f"Error applying config: {e}")
    print("\nTip: If you see 'InvalidArgs', your system might not support different scales per monitor.")
    print("Try enabling 'scale-monitor-framebuffer' in gsettings if using Wayland.")
