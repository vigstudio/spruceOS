# TrimUI Smart Pro S Runtime Notes

This note captures the observed runtime layout of a TrimUI Smart Pro S running spruceOS. Use it before changing PyUI, Fn/DIP switch behavior, CPU/fan settings, or device services.

Inventory source: SSH read-only audit against device IP `172.16.10.173`.

## System

- Kernel: Linux `5.15.147`, `aarch64`.
- Board boot string includes `sun55iw3p1`.
- User context over SSH is `root`.
- BusyBox: `1.36.1`.
- RAM: about `986 MB` total, no swap configured in the sampled state.
- Root filesystem: `/dev/mmcblk0p4` mounted at `/`, ext4, read-write.
- Internal UDISK: `/dev/mmcblk0p6` mounted at `/mnt/UDISK`, ext4, read-write.
- SD card: `/dev/mmcblk1p1` mounted at `/mnt/sdcard/mmcblk1p1`, vfat, read-write.
- `/mnt/SDCARD` is the practical SD-card root used by spruceOS scripts and apps.

## CPU

The device has two CPU clusters. Do not treat `policy0` as a single whole-device performance target.

Observed online cores:

```text
4-7
```

Little cluster, `cpu0`-`cpu3`:

```text
available: 408000 672000 792000 936000 1032000 1128000 1224000 1320000 1416000
governors: conservative ondemand userspace powersave performance schedutil
current sampled state: ondemand, 408000-1416000
```

Big cluster, `cpu4`-`cpu7`:

```text
available: 408000 672000 840000 1008000 1200000 1344000 1488000 1584000 1680000 1800000 1992000 2088000 2160000
governors: conservative ondemand userspace powersave performance schedutil
current sampled state: ondemand, 1008000-1992000
```

Important implications:

- Stock scripts that write `2000000` to `cpu0` or `policy0` can fail with `Invalid argument`.
- Big-cluster performance mode can safely target `cpu4`-`cpu7` at `1992000` in the current spruceOS config.
- `2160000` exists as an overclock maximum but should not be used casually.
- Spruce CPU helper scripts lock `scaling_governor`, `scaling_min_freq`, and `scaling_max_freq` with `chmod a-w`; scripts that write these files must unlock and re-lock deliberately.

Relevant repo/device config:

- `/mnt/SDCARD/spruce/scripts/platform/SmartProS.cfg`
- `/mnt/SDCARD/spruce/scripts/platform/device_functions/utils/cpu_control_functions.sh`

## Thermal And Fan

Thermal zones observed:

- `cpul_thermal_zone`
- `cpub_thermal_zone`
- `gpu_thermal_zone`
- `npu_thermal_zone`
- `ddr_thermal_zone`
- `axp2202-usb`
- `axp2202-battery`

Fan control:

```text
/sys/class/thermal/cooling_device0
type: pwm-fan
max_state: 31
```

Thermal watchdog process:

```text
/mnt/SDCARD/spruce/smartpros/bin/thermal-watchdog
```

Thermal profile files:

```text
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog/active_profile
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog/profiles/conservative.json
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog/profiles/off.json
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog/profiles/quiet.json
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog/profiles/smart.json
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog/profiles/sport.json
```

Observed active profile:

```text
smart
```

Design implication: CPU/Fn performance features should prefer existing thermal profiles and CPU helper functions over independent long-running raw sysfs loops.

## Power

Battery power supply:

```text
/sys/class/power_supply/axp2202-battery
```

Sampled state:

```text
status: Discharging
capacity: 98
voltage_now: 4062000
temp: 254
```

USB power supply:

```text
/sys/class/power_supply/axp2202-usb
```

Sampled state:

```text
online: 0
present: 0
```

## Display, Brightness, LED, Rumble

Display config from `SmartProS.cfg`:

```text
DISPLAY_WIDTH=1280
DISPLAY_HEIGHT=720
DISPLAY_ROTATION=0
DISPLAY_ASPECT_RATIO=16:9
```

Backlight path:

```text
/sys/class/backlight/backlight0/brightness
```

Sampled state:

```text
brightness=255
actual_brightness=255
max_brightness=255
bl_power=0
```

LED animation sysfs:

```text
/sys/class/led_anim
```

It exposes frame, effect, RGB, mask, and scale controls. Some files have unusual permissions, including `enable` with no visible permissions in the sampled listing.

Rumble GPIO from platform config:

```text
RUMBLE_GPIO=236
```

## Fn Slider And Input

Fn slider / DIP switch is GPIO, not a normal gamepad key event:

```text
/sys/class/gpio/gpio363/value
```

Sampled value:

```text
0
```

Input devices:

```text
/dev/input/event0  sunxi-keyboard       volume buttons
/dev/input/event1  pwm-vibrator
/dev/input/event2  axp2202-pek          power button
/dev/input/event3  audiocodec Headphones
/dev/input/event4  TRIMUI Player1       gamepad/controller
/dev/input/js0     joystick interface
```

Smart Pro S key mappings from `SmartProS.cfg`:

```text
EVENT_PATH_READ_INPUTS_SPRUCE=/dev/input/event4
EVENT_PATH_VOLUME=/dev/input/event0
EVENT_PATH_POWER=/dev/input/event2

B_A=1 305
B_B=1 304
B_X=1 308
B_Y=1 307
B_L1=1 310
B_R1=1 311
B_L2=3 2 255
B_R2=3 5 255
B_L3=1 317
B_R3=1 318
B_START=1 315
B_SELECT=1 314
B_MENU=1 316
B_HOME=1 172
B_VOLUP=1 115
B_VOLDOWN=1 114
```

Design implications:

- Fn slider logic belongs in a GPIO watcher or `trimui_scened`, not key event handling.
- L3/R3 are joystick click inputs and are separate from the physical Fn slider.

## Network And Remote Access

Sampled IP:

```text
172.16.10.173
```

Active services/processes observed:

- `wpa_supplicant`
- `dropbear` SSH
- `smbd`
- `darkhttpd /mnt/SDCARD/spruce/www`
- `adbd`

DNS sampled from `/etc/resolv.conf` and `/tmp/resolv.conf`:

```text
8.8.8.8
8.8.4.4
```

SSH credentials used during inventory:

```text
user: spruce
password: happygaming
```

## Runtime Processes

Important user-space processes observed:

```text
/usr/trimui/bin/runtrimui.sh
trimui_inputd
trimui_scened
trimui_btmanager
hardwareservice
musicserver
thermal-watchdog
homebutton_watchdog.sh
low_power_warning.sh
power_button_watchdog_v2.sh
buttons_watchdog.sh
principal.sh
PyUI launch.sh
MainUI ... mainui.py
```

`buttons_watchdog.sh` runs with child processes for background polling and `getevent`. Seeing multiple shell PIDs for it can be normal; verify actual behavior before killing anything.

PyUI runs through:

```text
/mnt/SDCARD/App/PyUI/launch.sh
/mnt/SDCARD/spruce/flip/bin/MainUI /mnt/SDCARD/App/PyUI/main-ui/mainui.py -device TRIMUI_SMART_PRO_S ...
```

Restart caution:

- Killing `MainUI` or `launch.sh` manually can lead to duplicate PyUI instances if another watchdog or parent script respawns it while a manual launch is also started.
- Prefer the existing UI reload path when available. If SSH restart is required, kill all matching PyUI launch/MainUI processes, wait, then start exactly one `launch.sh` and verify with `ps`.

## Stock TrimUI Layout

Stock base:

```text
/usr/trimui
```

Important stock binaries:

```text
/usr/trimui/bin/MainUI
/usr/trimui/bin/keymon
/usr/trimui/bin/mplayer
/usr/trimui/bin/shmvar
/usr/trimui/bin/systemval
/usr/trimui/bin/trimui_inputd
/usr/trimui/bin/trimui_scened
```

Stock apps:

```text
/usr/trimui/apps/bookreader
/usr/trimui/apps/fn_editor
/usr/trimui/apps/moonlight
/usr/trimui/apps/musicplayer
/usr/trimui/apps/photoviewer
/usr/trimui/apps/player
/usr/trimui/apps/usb_storage
/usr/trimui/apps/zformatter_fat32
```

Stock Fn editor:

```text
/usr/trimui/apps/fn_editor
```

Stock Fn/DIP action list:

```text
/usr/trimui/apps/fn_editor/scripts.json
```

Observed stock actions:

- `LED off`
- `Quiet Mode`
- `Silent Mode`
- `CPU Power Save`
- `CPU Performance Mode`
- `Turbo Button A`
- `Turbo Button B`
- `Turbo Button X`
- `Turbo Button Y`
- `Turbo Button L`
- `Turbo Button R`
- `Turbo Button L2`
- `Turbo Button R2`

Fn key config files:

```text
/usr/trimui/fnkeys/f1key.json
/usr/trimui/fnkeys/f2key.json
```

Sampled values:

```json
{
    "name": "LCD brigheness switcher",
    "launch": "com.trimui.switch.backlight.sh"
}
```

```json
{
    "name": "CPU clock swither",
    "launch": "com.trimui.switch.cpufreq.sh"
}
```

Runtime scene directory:

```text
/usr/trimui/scene
```

Observed active scene scripts:

```text
com.trimui.cpuperformance.sh
com.trimui.ledc.sh
```

## Spruce Layout

Spruce root:

```text
/mnt/SDCARD/spruce
```

Important paths:

```text
/mnt/SDCARD/spruce/scripts
/mnt/SDCARD/spruce/scripts/helperFunctions.sh
/mnt/SDCARD/spruce/scripts/buttons_watchdog.sh
/mnt/SDCARD/spruce/scripts/platform/SmartProS.cfg
/mnt/SDCARD/spruce/scripts/platform/device_functions/SmartProS.sh
/mnt/SDCARD/spruce/scripts/platform/device_functions/utils/cpu_control_functions.sh
/mnt/SDCARD/spruce/smartpros/bin/thermal-watchdog
/mnt/SDCARD/spruce/smartpros/etc/thermal-watchdog
```

PyUI root:

```text
/mnt/SDCARD/App/PyUI
```

PyUI config:

```text
/mnt/SDCARD/App/PyUI/py-ui-config.json
```

Sampled language setting:

```json
"language": "Vietnamese"
```

Video app root:

```text
/mnt/SDCARD/App/VideoPlayer
```

Fn editor SD-card app root:

```text
/mnt/SDCARD/App/fn_editor
```

Media folder:

```text
/mnt/SDCARD/Roms/MEDIA
```

Sampled contents include one `.mp4` and `miyoogamelist.xml`.

## Config Ownership

Stock/firmware config:

```text
/mnt/UDISK/system.json
```

Sampled notable values:

```json
{
    "language": "vn.lang",
    "theme": "/mnt/SDCARD/Themes/OTB",
    "wifi": 1,
    "cpufreq": 0,
    "ledswitch": 1,
    "ledvalue": 4,
    "fanlevel": -1,
    "usejoystick": 1,
    "brightness": 10,
    "vol": 0
}
```

Spruce config:

```text
/mnt/SDCARD/Saves/spruce/spruce-config.json
```

PyUI config:

```text
/mnt/SDCARD/App/PyUI/py-ui-config.json
```

Design implications:

- Use `/mnt/UDISK/system.json` for stock TrimUI settings that stock services read.
- Use `/mnt/SDCARD/Saves/spruce/spruce-config.json` for spruceOS user settings.
- Use `/mnt/SDCARD/App/PyUI/py-ui-config.json` for PyUI-specific settings.
- Avoid inventing new config files unless there is a clear owner and migration path.

## Available Tools

Tools found in PATH:

```text
sh=/bin/sh
python=/usr/bin/python
python3=/usr/bin/python3
jq=/mnt/SDCARD/spruce/bin64/jq
gptokeyb=/mnt/SDCARD/spruce/bin64/gptokeyb
getevent=/mnt/SDCARD/spruce/bin64/getevent
systemval=/usr/trimui/bin/systemval
shmvar=/usr/trimui/bin/shmvar
tinymix=/usr/bin/tinymix
```

Not found in global PATH during inventory:

```text
ffplay
```

Design implication: video playback should go through the existing MEDIA launcher or set app-specific PATH/LD_LIBRARY_PATH before assuming `ffplay` is globally available.

## Safe Extension Points

Prefer these for app and UX work:

- `/mnt/SDCARD/App/PyUI/main-ui/...`
- `/mnt/SDCARD/App/PyUI/lang/*.json`
- `/mnt/SDCARD/App/PyUI/fonts`
- `/mnt/SDCARD/App/VideoPlayer`
- `/mnt/SDCARD/App/fn_editor`
- `/mnt/SDCARD/spruce/scripts` when changing spruceOS-owned runtime scripts
- `/mnt/SDCARD/Saves/spruce/spruce-config.json` for spruce-owned settings

Use caution with these:

- `/usr/trimui/scene`: runtime scene activation area; can be written, but scripts can loop and must be process-managed.
- `/usr/trimui/fnkeys`: stock Fn key assignment area.
- `/mnt/UDISK/system.json`: stock settings file; use only for settings stock services expect.

Avoid unless deliberately doing firmware-level work:

- replacing stock binaries in `/usr/trimui/bin`
- changing rootfs boot files
- blindly killing `trimui_inputd`, `trimui_scened`, or `MainUI` without restart plan
- writing CPU sysfs without checking cluster, frequency table, and file permissions

## Recommended Development Rules

1. Inventory first when touching hardware, sysfs, services, or stock TrimUI behavior.
2. Treat Fn slider as GPIO363.
3. Treat L3/R3 as controller keys, not the Fn slider.
4. Treat CPU as two clusters.
5. Respect `thermal-watchdog` and existing CPU helper functions.
6. Prefer SD-card app/script overrides over modifying stock `/usr/trimui/apps` sources.
7. If a scene script loops, kill previous instances before starting a new one.
8. Verify with device state, not only repo tests:
   - `ps`
   - `/tmp/*watchdog*.log`
   - `/sys/class/gpio/gpio363/value`
   - CPU `scaling_*` files
   - PyUI process count

## Open Questions

- Whether `trimui_scened` should remain the only owner of `/usr/trimui/scene`, or whether spruceOS should fully own GPIO363 scene dispatch.
- Whether Fn CPU performance should switch thermal profiles (`sport`/`smart`) instead of directly writing CPU sysfs.
- Whether PyUI should expose diagnostics for GPIO363, active scene scripts, CPU cluster state, thermal profile, fan state, and service health.
- Whether the video player should depend only on MEDIA launcher or include a fallback ffplay path discovery routine.
