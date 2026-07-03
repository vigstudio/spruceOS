# Session Summary: SpruceOS PyUI Patches & Android Streaming Plan

## System Status & Git
- **Device IP**: `172.16.10.173` (SSH: `spruce` / `happygaming`).
- **PR Branch**: `feature/trimui-stock-settings` (PR #1565 to `upstream/Development`).
- **Merged Test Branch**: `vigstudio/development-vietnamese-trimui` (deployed and compiled on device).

## Progress Implemented

### 1. Fn Settings & CPU
- **CPU scripts patched**: `com.trimui.cpuperformance.sh` and `com.trimui.cpusave.sh` in `App/fn_editor` made one-shot (no infinite loops).
- **Thermal profile aware**:
  - Fn Performance Mode ON sets active thermal profile to `sport` and overrides `cpu4` to `performance 1992000-1992000`.
  - Fn Performance Mode OFF sets active thermal profile to `smart` and overrides `cpu4` to `ondemand 1008000-1992000`.
  - CPU Power Save ON sets active thermal profile to `conservative` and overrides `cpu4` to `ondemand 1008000-1200000`.
- **Fn Diagnostics**: Option added to PyUI Fn Settings menu showing:
  - DIP Switch GPIO363 state.
  - Active thermal profile.
  - Fan state (`cooling_device0`).
  - `cpu4` governor/frequencies.
  - Enabled scene scripts count.

### 2. Video Player
- **Search cache**: Search now queries `/mnt/SDCARD/Saves/spruce/video-index.json` instead of executing slow recursive directory walks.
- **Cache Refresh**: Added "Refresh video index" option in menu and mapped to `X` button in file browser.

### 3. Vietnamese i18n
- Merged full Vietnamese translation files and custom `BeVietnamPro` fonts.

### 4. Docker & Wolf Testing
- Attempted Wolf Docker setup on Windows host.
- **Fail reason**: WSL2 does not expose `/dev/dri` (only `/dev/dxg` via WSLg) and has no `/dev/uinput` or `/dev/uhid` for gamepad. GPU encoding failed; only slow CPU software encoders (x264/x265) were available.
- **Cleanup**: Purged Wolf/Nvidia/Hello-World images and volumes. Reclaimed 7.75GB build cache. Running user containers (`tolereveo_*`) left untouched.

---

## Future Android Streaming Plan

### Host (Windows PC)
- **Software**: Sunshine server.
- **Android Emulator**: BlueStacks, LDPlayer, or Google Play Games Beta.
- **Virtual Display**: Use Virtual Display Driver to create a dummy `1280x720` monitor.
- **Sunshine Config**: Bind Sunshine to stream only the virtual monitor. Add shortcut launch commands for the emulator.

### Client (TrimUI Smart Pro S)
- Use the built-in Moonlight app to pair with PC.
- Stream directly from the virtual display.
