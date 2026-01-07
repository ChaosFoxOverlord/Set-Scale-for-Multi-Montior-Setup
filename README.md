# Set-Scale-for-Multi-Monitor-Setup

A Python utility to programmatically set individual display scaling factors for multi-monitor setups in GNOME (via D-Bus). 

This script is particularly useful for users who need to toggle scaling frequently or want to automate their display configuration without using the GNOME Settings GUI.

## Features
- **Per-monitor scaling:** Assign specific scaling factors (e.g., 1.0, 1.25, 2.0) to different displays.
- **D-Bus Integration:** Directly communicates with `org.gnome.Mutter.DisplayConfig`.
- **Safe Execution:** Uses the system's Python 3 to ensure `dbus` library availability.

## Prerequisites
- **GNOME Desktop Environment** (Mutter window manager).
- **Python 3** with `python3-dbus` installed (usually pre-installed on Ubuntu/Fedora).

## Configuration

Before running the script, you need to identify your monitor connector names and define your desired scaling in the `SCALE_MAP` dictionary within `set_scale_multi.py`.

### 1. Identify your Monitor Names
Run the following command in your terminal:
```bash
xrandr --query | grep " connected"
```
Common names are `eDP-1` (internal laptop display), `HDMI-1`, or `DP-1`.

### 2. Edit the script
Update the `SCALE_MAP` in the script:
```python
SCALE_MAP = {
    "eDP-1": 1.0,   # Example: Internal Display
    "HDMI-1-0": 2.0 # Example: External 4K Monitor
}
```

## Usage
Make the script executable and run it:
```bash
chmod +x set_scale_multi.py
./set_scale_multi.py
```

## Troubleshooting

### "InvalidArgs: Logical monitor scales must be identical"
If you encounter this error, your system (likely under **X11**) does not support different scaling factors per monitor nativelly. 

**Solution for Wayland users:**
Enable the experimental fractional scaling feature:
```bash
gsettings set org.gnome.mutter experimental-features "['scale-monitor-framebuffer']"
```
*Note: A logout/login or restart might be required.*

## Credits
Based on discussions and snippets from [AskUbuntu](https://askubuntu.com/questions/1035718/) and [strycore's gist](https://gist.github.com/strycore/ca1120357182d4ba48358759).
