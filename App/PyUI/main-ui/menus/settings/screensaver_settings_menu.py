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

    def _set_screensaver_prop(self, key, value):
        ss = Theme._data.get("screensaver", {})
        ss[key] = value
        Theme._data["screensaver"] = ss
        Theme.save_changes()

    def _get_screensaver_prop(self, key, default=True):
        return Theme._data.get("screensaver", {}).get(key, default)

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

        return option_list
