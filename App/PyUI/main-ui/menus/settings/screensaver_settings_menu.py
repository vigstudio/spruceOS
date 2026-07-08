import os

from controller.controller_inputs import ControllerInput
from menus.language.language import Language
from menus.settings import settings_menu
from themes.theme import Theme
from utils.py_ui_config import PyUiConfig
from views.grid_or_list_entry import GridOrListEntry


class ScreenSaverSettingsMenu(settings_menu.SettingsMenu):
    def __init__(self):
        super().__init__()

    def launch_screen_saver(self, input):
        pass

    def toggle_show_clock(self, input):
        if ControllerInput.A == input:
            current = Theme._data.get("screensaver", {}).get("showClock", True)
            self._set_screensaver_prop("showClock", not current)

    def toggle_show_date(self, input):
        if ControllerInput.A == input:
            current = Theme._data.get("screensaver", {}).get("showDate", True)
            self._set_screensaver_prop("showDate", not current)

    def toggle_show_battery(self, input):
        if ControllerInput.A == input:
            current = Theme._data.get("screensaver", {}).get("showBattery", True)
            self._set_screensaver_prop("showBattery", not current)

    def change_timeout(self, input):
        current = PyUiConfig.get_screensaver_timeout_sec()
        if ControllerInput.DPAD_RIGHT == input or ControllerInput.R1 == input:
            new_val = min(300, current + 30)
        elif ControllerInput.DPAD_LEFT == input or ControllerInput.L1 == input:
            new_val = max(0, current - 30)
        elif ControllerInput.A == input:
            new_val = 0 if current > 0 else 120
        else:
            return
        PyUiConfig.set("screensaverTimeoutSec", new_val)
        PyUiConfig.save()

    def change_overlay_opacity(self, input):
        current = Theme._data.get("screensaver", {}).get("overlayOpacity", 0.0)
        if ControllerInput.DPAD_RIGHT == input or ControllerInput.R1 == input:
            new_val = min(1.0, round(current + 0.1, 1))
        elif ControllerInput.DPAD_LEFT == input or ControllerInput.L1 == input:
            new_val = max(0.0, round(current - 0.1, 1))
        elif ControllerInput.A == input:
            new_val = 0.0 if current > 0 else 0.5
        else:
            return
        self._set_screensaver_prop("overlayOpacity", new_val)

    def change_blur(self, input):
        current = Theme._data.get("screensaver", {}).get("blur", 0)
        if ControllerInput.DPAD_RIGHT == input or ControllerInput.R1 == input:
            new_val = min(30, current + 2)
        elif ControllerInput.DPAD_LEFT == input or ControllerInput.L1 == input:
            new_val = max(0, current - 2)
        elif ControllerInput.A == input:
            new_val = 0 if current > 0 else 10
        else:
            return
        self._set_screensaver_prop("blur", new_val)

    def cycle_bg_image(self, input):
        ss = Theme._data.get("screensaver", {})
        current = ss.get("bgImage", "")
        images = self._find_bg_images()
        if not images:
            self._set_screensaver_prop("bgImage", "")
            return

        if ControllerInput.DPAD_RIGHT == input or ControllerInput.R1 == input:
            if current in images:
                idx = (images.index(current) + 1) % len(images)
            else:
                idx = 0
            self._set_screensaver_prop("bgImage", images[idx])
        elif ControllerInput.DPAD_LEFT == input or ControllerInput.L1 == input:
            if current in images:
                idx = (images.index(current) - 1) % len(images)
            else:
                idx = len(images) - 1
            self._set_screensaver_prop("bgImage", images[idx])
        elif ControllerInput.A == input:
            self._set_screensaver_prop("bgImage", "")

    def _find_bg_images(self):
        from devices.device import Device
        paths = [
            os.path.join(Device.get_device().get_sd_card_path(), "skins"),
            os.path.join(Device.get_device().get_sd_card_path(), "App", "PyUI"),
        ]
        images = []
        exts = (".png", ".jpg", ".jpeg", ".bmp")
        for base in paths:
            if not os.path.exists(base):
                continue
            for root, dirs, files in os.walk(base):
                for f in files:
                    if f.lower().endswith(exts) and "screensaver" in f.lower():
                        images.append(os.path.join(root, f))
        images.sort()
        return images

    def _set_screensaver_prop(self, key, value):
        ss = Theme._data.get("screensaver", {})
        ss[key] = value
        Theme._data["screensaver"] = ss
        Theme.save_changes()

    def _get_screensaver_prop(self, key, default=True):
        return Theme._data.get("screensaver", {}).get(key, default)

    def _format_image_label(self, path):
        if not path:
            return Language.get("screensaverBgNone", "None (solid color)")
        return os.path.basename(path)

    def build_options_list(self):
        option_list = []

        timeout = PyUiConfig.get_screensaver_timeout_sec()
        timeout_text = f"{timeout // 60}m {timeout % 60}s" if timeout > 0 else Language.get("off", "Off")
        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverTimeout", "Timeout"),
                value_text="<    " + timeout_text + "    >",
                image_path=None,
                image_path_selected=None,
                description=Language.get("screensaverTimeoutDesc", "Minutes before screensaver activates (0=off)"),
                icon=None,
                value=self.change_timeout
            )
        )

        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverShowClock", "Show clock"),
                value_text="<    " + Language.boolean_label(self._get_screensaver_prop("showClock", True)) + "    >",
                image_path=None,
                image_path_selected=None,
                description=None,
                icon=None,
                value=self.toggle_show_clock
            )
        )

        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverShowDate", "Show date"),
                value_text="<    " + Language.boolean_label(self._get_screensaver_prop("showDate", True)) + "    >",
                image_path=None,
                image_path_selected=None,
                description=None,
                icon=None,
                value=self.toggle_show_date
            )
        )

        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverShowBattery", "Show battery"),
                value_text="<    " + Language.boolean_label(self._get_screensaver_prop("showBattery", True)) + "    >",
                image_path=None,
                image_path_selected=None,
                description=None,
                icon=None,
                value=self.toggle_show_battery
            )
        )

        current_image = self._get_screensaver_prop("bgImage", "")
        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverBgImage", "Background image"),
                value_text="<    " + self._format_image_label(current_image) + "    >",
                image_path=None,
                image_path_selected=None,
                description=Language.get("screensaverBgImageDesc", "Auto-detects images with 'screensaver' in name"),
                icon=None,
                value=self.cycle_bg_image
            )
        )

        overlay_opacity = self._get_screensaver_prop("overlayOpacity", 0.0)
        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverOverlayOpacity", "Overlay opacity"),
                value_text="<    " + f"{int(overlay_opacity * 100)}%" + "    >",
                image_path=None,
                image_path_selected=None,
                description=Language.get("screensaverOverlayOpacityDesc", "Dark overlay over background (0=off, 100=full black)"),
                icon=None,
                value=self.change_overlay_opacity
            )
        )

        blur = self._get_screensaver_prop("blur", 0)
        blur_text = str(blur) if blur > 0 else Language.get("off", "Off")
        option_list.append(
            GridOrListEntry(
                primary_text=Language.get("screensaverBlur", "Background blur"),
                value_text="<    " + blur_text + "    >",
                image_path=None,
                image_path_selected=None,
                description=Language.get("screensaverBlurDesc", "Blur effect on background image (0=off)"),
                icon=None,
                value=self.change_blur
            )
        )

        return option_list
