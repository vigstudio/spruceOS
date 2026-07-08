import time
import datetime
import os
import sdl2
import sdl2.sdlimage

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

            cls._render_background(screen_w, screen_h, Display)

            widgets = cls._get_enabled_widgets()
            for widget in widgets:
                cls._render_widget(widget, screen_w, screen_h, Display)

            Display.renderer.present()
            sdl2.SDL_SetRenderTarget(Display.renderer.renderer, Display.render_canvas)
        except Exception as e:
            PyUiLogger.get_logger().error(f"ScreenSaver render error: {e}")

    @classmethod
    def _render_background(cls, screen_w, screen_h, Display):
        ss = Theme._data.get("screensaver", {})
        bg_image = ss.get("bgImage", "")
        overlay_opacity = ss.get("overlayOpacity", 0.0)
        overlay_color = Theme.hex_to_color(ss.get("overlayColor", "#000000"))
        blur = ss.get("blur", 0)
        bg_color = Theme.hex_to_color(ss.get("bgColor", "#000000"))

        if bg_image and os.path.exists(bg_image):
            surface = sdl2.sdlimage.IMG_Load(bg_image.encode("utf-8"))
            if surface:
                if blur > 0:
                    surface = cls._apply_blur(surface, blur)
                texture = sdl2.SDL_CreateTextureFromSurface(Display.renderer.renderer, surface)
                if texture:
                    sdl2.SDL_SetTextureBlendMode(texture, sdl2.SDL_BLENDMODE_BLEND)
                    src_w = surface.contents.w
                    src_h = surface.contents.h
                    src = sdl2.SDL_Rect(0, 0, src_w, src_h)
                    dst = sdl2.SDL_Rect(0, 0, screen_w, screen_h)
                    sdl2.SDL_RenderCopy(Display.renderer.renderer, texture, src, dst)
                    sdl2.SDL_DestroyTexture(texture)
                sdl2.SDL_FreeSurface(surface)
            else:
                sdl2.SDL_SetRenderDrawColor(Display.renderer.sdlrenderer,
                    bg_color[0], bg_color[1], bg_color[2], 255)
                sdl2.SDL_RenderClear(Display.renderer.sdlrenderer)
        else:
            sdl2.SDL_SetRenderDrawColor(Display.renderer.sdlrenderer,
                bg_color[0], bg_color[1], bg_color[2], 255)
            sdl2.SDL_RenderClear(Display.renderer.sdlrenderer)

        if 0 < overlay_opacity <= 1.0:
            alpha = int(overlay_opacity * 255)
            sdl2.SDL_SetRenderDrawBlendMode(Display.renderer.sdlrenderer, sdl2.SDL_BLENDMODE_BLEND)
            sdl2.SDL_SetRenderDrawColor(Display.renderer.sdlrenderer,
                overlay_color[0], overlay_color[1], overlay_color[2], alpha)
            rect = sdl2.SDL_Rect(0, 0, screen_w, screen_h)
            sdl2.SDL_RenderFillRect(Display.renderer.sdlrenderer, rect)

    @classmethod
    def _apply_blur(cls, surface, radius):
        w = surface.contents.w
        h = surface.contents.h
        fmt = surface.contents.format.contents
        src_pixels = sdl2.SDL_LockSurface(surface)
        if src_pixels == 0:
            return surface

        try:
            pixels = surface.contents.pixels
            pitch = surface.contents.pitch
            bpp = fmt.BytesPerPixel
            temp = sdl2.SDL_CreateRGBSurfaceWithFormat(0, w, h, 32, fmt.format)
            if not temp:
                return surface

            sdl2.SDL_LockSurface(temp)
            try:
                temp_pixels = temp.contents.pixels
                temp_pitch = temp.contents.pitch

                r = min(radius, min(w, h) // 2)
                if r < 1:
                    r = 1

                kernel_size = 2 * r + 1
                for y in range(h):
                    for x in range(w):
                        sum_r, sum_g, sum_b, count = 0, 0, 0, 0
                        for ky in range(-r, r + 1):
                            sy = y + ky
                            if sy < 0 or sy >= h:
                                continue
                            for kx in range(-r, r + 1):
                                sx = x + kx
                                if sx < 0 or sx >= w:
                                    continue
                                offset = sy * pitch + sx * bpp
                                if bpp == 4:
                                    b = pixels[offset]
                                    g = pixels[offset + 1]
                                    rd = pixels[offset + 2]
                                    a = pixels[offset + 3]
                                elif bpp == 3:
                                    b = pixels[offset]
                                    g = pixels[offset + 1]
                                    rd = pixels[offset + 2]
                                    a = 255
                                else:
                                    continue
                                sum_r += rd
                                sum_g += g
                                sum_b += b
                                count += 1
                        if count > 0:
                            avg_r = sum_r // count
                            avg_g = sum_g // count
                            avg_b = sum_b // count
                        else:
                            avg_r, avg_g, avg_b = 0, 0, 0
                        dst_offset = y * temp_pitch + x * bpp
                        if bpp == 4:
                            temp_pixels[dst_offset] = avg_b
                            temp_pixels[dst_offset + 1] = avg_g
                            temp_pixels[dst_offset + 2] = avg_r
                            temp_pixels[dst_offset + 3] = 255
                        elif bpp == 3:
                            temp_pixels[dst_offset] = avg_b
                            temp_pixels[dst_offset + 1] = avg_g
                            temp_pixels[dst_offset + 2] = avg_r
            finally:
                sdl2.SDL_UnlockSurface(temp)
        finally:
            sdl2.SDL_UnlockSurface(surface)

        sdl2.SDL_BlitSurface(temp, None, surface, None)
        sdl2.SDL_FreeSurface(temp)
        return surface

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
