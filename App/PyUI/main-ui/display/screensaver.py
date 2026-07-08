import time
import datetime
import sdl2

from devices.device import Device
from display.font_purpose import FontPurpose
from display.render_mode import RenderMode
from themes.theme import Theme
from utils.logger import PyUiLogger


class ScreenSaver:
    @classmethod
    def render(cls):
        try:
            renderer = Device.get_device()
            screen_w = renderer.screen_width()
            screen_h = renderer.screen_height()
            from display.display import Display

            bg_color = Theme.hex_to_color(Theme.get_screensaver_bg_color())
            sdl2.SDL_SetRenderDrawColor(Display.renderer.sdlrenderer, bg_color[0], bg_color[1], bg_color[2], 255)
            sdl2.SDL_RenderClear(Display.renderer.sdlrenderer)

            widgets = cls._get_enabled_widgets()
            for widget in widgets:
                cls._render_widget(widget, screen_w, screen_h, Display)

            Display.renderer.present()
            sdl2.SDL_SetRenderTarget(Display.renderer.renderer, Display.render_canvas)
        except Exception as e:
            PyUiLogger.get_logger().error(f"ScreenSaver render error: {e}")

    @classmethod
    def _get_enabled_widgets(cls):
        ss = Theme._data.get("screensaver", {})
        show_clock = ss.get("showClock", True)
        show_date = ss.get("showDate", True)
        show_battery = ss.get("showBattery", True)

        all_widgets = Theme.get_screensaver_widgets()
        enabled = []
        for w in all_widgets:
            wtype = w.get("type", "")
            if wtype == "clock" and not show_clock:
                continue
            if wtype == "date" and not show_date:
                continue
            if wtype == "battery" and not show_battery:
                continue
            enabled.append(w)
        return enabled

    @classmethod
    def _render_widget(cls, widget, screen_w, screen_h, Display):
        wtype = widget.get("type", "")
        x = int(widget.get("x", 0.5) * screen_w)
        y = int(widget.get("y", 0.5) * screen_h)
        font_size = int(widget.get("fontSize", 24))
        color = Theme.hex_to_color(widget.get("color", "#FFFFFF"))
        multiplier = Theme._default_multiplier
        scaled_size = max(12, int(font_size * multiplier))

        if wtype == "clock":
            now = datetime.datetime.now()
            text = now.strftime("%H:%M")
            cls._draw_text(text, x, y, color, scaled_size, Display, center=True)

        elif wtype == "date":
            now = datetime.datetime.now()
            text = now.strftime("%A, %B %d")
            cls._draw_text(text, x, y, color, scaled_size, Display, center=True)

        elif wtype == "battery":
            try:
                percent = Device.get_device().get_battery_percent()
                charging = Device.get_device().get_charge_status()
                from devices.charge.charge_status import ChargeStatus
                symbol = "+" if charging == ChargeStatus.CHARGING else ""
                text = f"{symbol}{percent}%"
                if percent <= 10:
                    color = (255, 80, 80)
                elif percent <= 30:
                    color = (255, 200, 80)
                cls._draw_text(text, x, y, color, scaled_size, Display, center=True)
            except Exception:
                pass

        elif wtype == "text":
            text = widget.get("value", "")
            if text:
                cls._draw_text(text, x, y, color, scaled_size, Display, center=True)

    @classmethod
    def _draw_text(cls, text, x, y, color, font_size, Display, center=True):
        from sdl2 import sdlttf
        font_obj = None
        for purpose in FontPurpose:
            try:
                font_obj = Display.fonts.get(purpose)
                if font_obj:
                    break
            except Exception:
                continue

        if font_obj is None:
            return

        font_path = Theme.get_font(FontPurpose.LIST)
        try:
            font = sdlttf.TTF_OpenFont(font_path.encode("utf-8"), font_size) if font_path else None
        except Exception:
            font = None

        if font is None:
            return

        try:
            sdl_color = sdl2.SDL_Color(color[0], color[1], color[2])
            surface = sdlttf.TTF_RenderUTF8_Blended(font, text.encode("utf-8"), sdl_color)
            if not surface:
                return

            texture = sdl2.SDL_CreateTextureFromSurface(Display.renderer.renderer, surface)
            if not texture:
                sdl2.SDL_FreeSurface(surface)
                return

            w = surface.contents.w
            h = surface.contents.h
            if center:
                draw_x = x - w // 2
            else:
                draw_x = x
            draw_y = y - h // 2

            dst = sdl2.SDL_Rect(draw_x, draw_y, w, h)
            sdl2.SDL_RenderCopy(Display.renderer.renderer, texture, None, dst)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(surface)
        except Exception as e:
            PyUiLogger.get_logger().error(f"ScreenSaver text render error: {e}")
        finally:
            sdlttf.TTF_CloseFont(font)
