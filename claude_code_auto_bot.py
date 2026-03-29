#!/usr/bin/env python3
"""
Claude Code Auto-Bot v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━
Monitors a screen region for Claude Code permission prompts and
auto-approves by clicking + pressing a configurable key.

Install:  pip install -r requirements.txt
Usage:    python claude_code_auto_bot.py
"""

import tkinter as tk
import threading
import time
import subprocess
import platform
import asyncio
import colorsys
import sys
import os
from datetime import datetime
from pathlib import Path

try:
    from PIL import ImageGrab, Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import winocr
    HAS_WINOCR = True
except ImportError:
    HAS_WINOCR = False

try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

HAS_OCR = HAS_WINOCR or HAS_PYTESSERACT


def play_alert_sound():
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        print("\a", end="", flush=True)


def send_notification(title, message):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["osascript", "-e",
                              f'display notification "{message}" with title "{title}" sound name "Glass"'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            subprocess.Popen(["notify-send", title, message],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            try:
                from plyer import notification
                notification.notify(title=title, message=message, timeout=5)
            except ImportError:
                pass
    except Exception:
        pass


# ─── Color Palette Generation ─────────────────────────────────────────────────

def _hsv_hex(h, s, v):
    """Convert HSV (h: 0-360, s: 0-1, v: 0-1) to hex color string."""
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def generate_palette(hue):
    """Generate a full color palette from a single hue (0-360)."""
    return {
        "bg":         _hsv_hex(hue, 0.70, 0.04),
        "panel":      _hsv_hex(hue, 0.65, 0.07),
        "panel2":     _hsv_hex(hue, 0.55, 0.10),
        "logbg":      _hsv_hex(hue, 0.70, 0.055),
        "border":     _hsv_hex(hue, 0.85, 1.0),
        "border_dim": _hsv_hex(hue, 0.75, 0.53),
        "accent":     _hsv_hex(hue, 0.85, 1.0),
        "accent_hi":  _hsv_hex(hue, 0.60, 1.0),
        "accent_dim": _hsv_hex(hue, 0.75, 0.53),
        "accent_dk":  _hsv_hex(hue, 0.80, 0.27),
        "green":      "#00ff88",
        "green_dim":  "#004422",
        "red":        "#ff2244",
        "red_dim":    "#440011",
        "yellow":     "#ffcc00",
        "text":       _hsv_hex(hue, 0.18, 1.0),
        "dim":        _hsv_hex(hue, 0.60, 0.67),
        "muted":      _hsv_hex(hue, 0.50, 0.40),
        "white":      "#ffffff",
        "log_text":   _hsv_hex(hue, 0.40, 1.0),
    }


THEMES = {
    "CRIMSON":  350,
    "EMBER":     20,
    "SOLAR":     45,
    "TOXIC":    120,
    "ARCTIC":   190,
    "COBALT":   220,
    "VIOLET":   270,
    "MAGENTA":  310,
}

PALETTES = {name: generate_palette(hue) for name, hue in THEMES.items()}

# Achromatic themes (hand-crafted since generate_palette needs a hue)
PALETTES["OBSIDIAN"] = {
    "bg":         "#050505",
    "panel":      "#0e0e0e",
    "panel2":     "#161616",
    "logbg":      "#0a0a0a",
    "border":     "#888888",
    "border_dim": "#444444",
    "accent":     "#888888",
    "accent_hi":  "#bbbbbb",
    "accent_dim": "#444444",
    "accent_dk":  "#222222",
    "green":      "#00ff88",
    "green_dim":  "#004422",
    "red":        "#ff2244",
    "red_dim":    "#440011",
    "yellow":     "#ffcc00",
    "text":       "#dddddd",
    "dim":        "#777777",
    "muted":      "#444444",
    "white":      "#ffffff",
    "log_text":   "#aaaaaa",
}

PALETTES["GHOST"] = {
    "bg":         "#f0f0f0",
    "panel":      "#e2e2e2",
    "panel2":     "#d8d8d8",
    "logbg":      "#e8e8e8",
    "border":     "#333333",
    "border_dim": "#999999",
    "accent":     "#333333",
    "accent_hi":  "#555555",
    "accent_dim": "#999999",
    "accent_dk":  "#cccccc",
    "green":      "#00aa55",
    "green_dim":  "#bbddcc",
    "red":        "#cc2244",
    "red_dim":    "#ddbbbb",
    "yellow":     "#cc9900",
    "text":       "#222222",
    "dim":        "#777777",
    "muted":      "#aaaaaa",
    "white":      "#111111",
    "log_text":   "#444444",
}

PALETTES["CLAUDE"] = {
    "bg":         "#252423",
    "panel":      "#30302e",
    "panel2":     "#2b2a28",
    "logbg":      "#282726",
    "border":     "#d97757",
    "border_dim": "#6b4a3a",
    "accent":     "#d97757",
    "accent_hi":  "#e89a7f",
    "accent_dim": "#6b4a3a",
    "accent_dk":  "#3d2c23",
    "green":      "#00ff88",
    "green_dim":  "#004422",
    "red":        "#ff2244",
    "red_dim":    "#440011",
    "yellow":     "#ffcc00",
    "text":       "#e8e4de",
    "dim":        "#8a8680",
    "muted":      "#55524e",
    "white":      "#f5f0ea",
    "log_text":   "#c4b8a8",
}

THEME_ORDER = list(THEMES.keys()) + ["OBSIDIAN", "GHOST", "CLAUDE"]

THEME_FILE = Path.home() / ".claude_autobot_theme"

def _load_saved_theme():
    try:
        name = THEME_FILE.read_text().strip()
        if name in PALETTES:
            return name
    except Exception:
        pass
    return "CLAUDE"

_default_theme = _load_saved_theme()
C = dict(PALETTES[_default_theme])

# ─── Platform-aware constants ────────────────────────────────────────────────

_SYSTEM = platform.system()

if _SYSTEM == "Darwin":
    CURSOR_NW_SE = "arrow"
    CURSOR_NE_SW = "arrow"
    MONO_FONT = "Menlo"
elif _SYSTEM == "Windows":
    CURSOR_NW_SE = "size_nw_se"
    CURSOR_NE_SW = "size_ne_sw"
    MONO_FONT = "Consolas"
else:
    CURSOR_NW_SE = "top_left_corner"
    CURSOR_NE_SW = "top_right_corner"
    MONO_FONT = "DejaVu Sans Mono"

TRANSPARENT_COLOR = "#010101"


# ─── OCR Detection ────────────────────────────────────────────────────────────

def _run_ocr_winocr(image):
    """Run Windows OCR on a PIL image. Returns recognized text (lowercase)."""
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(winocr.recognize_pil(image, lang="en"))
        lines = [line.text for line in result.lines]
        return " ".join(lines).lower()
    except Exception:
        return ""
    finally:
        loop.close()


def _run_ocr_tesseract(image):
    """Run Tesseract OCR on a PIL image. Returns recognized text (lowercase)."""
    try:
        # Pre-process for better accuracy on screen text
        gray = image.convert("L")
        w, h = gray.size
        if w < 400:
            gray = gray.resize((w * 2, h * 2), Image.LANCZOS)
        return pytesseract.image_to_string(gray, config="--psm 6").lower()
    except Exception:
        return ""


def detect_prompt(image, search_text):
    """
    Scan the image for the search text using available OCR engine.
    Returns (detected: bool, ocr_text: str).
    """
    if not HAS_OCR:
        return False, "(no OCR engine)"

    if HAS_WINOCR:
        ocr_text = _run_ocr_winocr(image)
    else:
        ocr_text = _run_ocr_tesseract(image)

    found = search_text.lower() in ocr_text
    return found, ocr_text


# ─── Parse Key Combo ──────────────────────────────────────────────────────────

def parse_key_action(key_string):
    """
    Parse a key string like 'enter', 'ctrl+enter', 'ctrl+shift+a' into
    a format pyautogui can execute.

    Returns a list of keys for pyautogui.hotkey().
    """
    parts = [k.strip().lower() for k in key_string.split("+")]
    # Map common aliases
    aliases = {
        "return": "enter",
        "esc": "escape",
        "del": "delete",
        "ins": "insert",
        "pgup": "pageup",
        "pgdn": "pagedown",
        "cmd": "command",
        "meta": "command",
    }
    return [aliases.get(p, p) for p in parts]


# ─── Main App ─────────────────────────────────────────────────────────────────

class ClaudeAutoBot:
    def __init__(self):
        # Set AppUserModelID so Windows shows our icon in the taskbar
        if platform.system() == "Windows":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "claude.codeautobot.v1"
                )
            except Exception:
                pass

        self.root = tk.Tk()
        self.root.title("⟐ CLAUDE CODE AUTO-BOT")
        self.root.configure(bg=C["bg"])
        self.root.minsize(520, 420)
        self.root.geometry("600x460+80+80")
        self.root.attributes("-topmost", True)

        # Set window/taskbar icon
        self._set_app_icon()

        self.watching = False
        self.sound_enabled = tk.BooleanVar(value=False)
        self.alert_cooldown = False
        self.check_interval = 1.5
        self.cooldown_seconds = 5
        self.total_approvals = 0
        self.total_scans = 0
        self.status_text = tk.StringVar(value="STANDBY")
        self.ocr_result = tk.StringVar(value="—")
        self.reticle_cx = 0.5
        self.reticle_cy = 0.5
        self._pulse_phase = 0
        self.current_theme = _default_theme
        self._retina_scale = self._detect_retina_scale()

        self._build_control_panel()
        self._build_overlay()
        self._check_dependencies()
        self._start_pulse()

        self.log("▸ SYSTEM ONLINE")
        self.log("▸ Position scan frame over Claude's Reply... box")
        self.log("▸ Click inside scan area to place ◎ reticle on [Enter]")
        self.log("▸ Top bar = MOVE  |  Edges, bottom & corners = RESIZE")

    def _set_app_icon(self):
        """Set the window icon from bundled or local auto_bot.ico."""
        try:
            # PyInstaller sets _MEIPASS for bundled apps
            if getattr(sys, '_MEIPASS', None):
                icon_path = os.path.join(sys._MEIPASS, 'auto_bot.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auto_bot.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    # ── Control Panel ─────────────────────────────────────────────────────

    def _build_control_panel(self):
        self._top_accent = tk.Frame(self.root, bg=C["border"], height=2)
        self._top_accent.pack(fill="x")

        self._header = tk.Frame(self.root, bg=C["panel"], padx=14, pady=8)
        self._header.pack(fill="x")

        self._title_frame = tk.Frame(self._header, bg=C["panel"])
        self._title_frame.pack(fill="x")

        self.pulse_dot = tk.Label(self._title_frame, text="⬡", font=("Helvetica", 16),
                                  fg=C["accent"], bg=C["panel"])
        self.pulse_dot.pack(side="left", padx=(0, 8))

        self._title_label = tk.Label(self._title_frame, text="CLAUDE CODE AUTO-BOT",
                                     font=(MONO_FONT, 13, "bold"),
                                     fg=C["accent"], bg=C["panel"])
        self._title_label.pack(side="left")
        self._version_label = tk.Label(self._title_frame, text="v1.0", font=(MONO_FONT, 8),
                                       fg=C["dim"], bg=C["panel"])
        self._version_label.pack(side="left", padx=(6, 0), pady=(4, 0))

        self._status_frame = tk.Frame(self._title_frame, bg=C["panel"])
        self._status_frame.pack(side="right")
        self.approvals_label = tk.Label(self._status_frame, text="0",
                                        font=(MONO_FONT, 12, "bold"),
                                        fg=C["accent"], bg=C["panel"])
        self.approvals_label.pack(side="right")
        self._approvals_text = tk.Label(self._status_frame, text="APR ",
                                        font=(MONO_FONT, 7),
                                        fg=C["dim"], bg=C["panel"])
        self._approvals_text.pack(side="right")
        self._status_sep = tk.Label(self._status_frame, text="│",
                                    font=(MONO_FONT, 10), fg=C["dim"], bg=C["panel"])
        self._status_sep.pack(side="right", padx=(4, 4))
        self.status_label = tk.Label(self._status_frame, textvariable=self.status_text,
                                     font=(MONO_FONT, 10, "bold"), fg=C["dim"], bg=C["panel"])
        self.status_label.pack(side="right")
        self.status_dot = tk.Label(self._status_frame, text="●", font=("Helvetica", 10),
                                   fg=C["dim"], bg=C["panel"])
        self.status_dot.pack(side="right", padx=(0, 4))

        self._header_sep = tk.Frame(self.root, bg=C["border_dim"], height=1)
        self._header_sep.pack(fill="x")

        # ── Controls ──
        self._controls = tk.Frame(self.root, bg=C["panel2"], padx=14, pady=8)
        self._controls.pack(fill="x")

        # ── Theme swatches ──
        self._theme_row = tk.Frame(self._controls, bg=C["panel2"])
        self._theme_row.pack(fill="x", pady=(0, 6))
        self._theme_visible = False
        self._theme_toggle = tk.Label(self._theme_row, text="▸", font=(MONO_FONT, 8),
                                      fg=C["dim"], bg=C["panel2"], cursor="hand2")
        self._theme_toggle.pack(side="left")
        self._theme_toggle.bind("<ButtonPress-1>", lambda e: self._toggle_theme_bar())
        self._theme_label = tk.Label(self._theme_row, text="THEME", font=(MONO_FONT, 7),
                                     fg=C["dim"], bg=C["panel2"], cursor="hand2")
        self._theme_label.pack(side="left", padx=(2, 6))
        self._theme_label.bind("<ButtonPress-1>", lambda e: self._toggle_theme_bar())
        self._theme_swatches = {}
        for name in THEME_ORDER:
            accent = PALETTES[name]["accent"]
            hlbg = C["accent"] if name == self.current_theme else C["muted"]
            swatch = tk.Frame(self._theme_row, bg=accent, width=16, height=16,
                              cursor="hand2", highlightthickness=2,
                              highlightbackground=hlbg)
            swatch.pack_propagate(False)
            swatch.bind("<ButtonPress-1>", lambda e, n=name: self.apply_theme(n))
            self._theme_swatches[name] = swatch

        self._row1 = tk.Frame(self._controls, bg=C["panel2"])
        self._row1.pack(fill="x", pady=(0, 6))

        self.start_btn = tk.Button(
            self._row1, text="▶  ENGAGE", font=(MONO_FONT, 10, "bold"),
            fg=C["white"], bg=C["accent"], activebackground=C["accent_hi"],
            activeforeground=C["white"], relief="flat", padx=16, pady=5,
            cursor="hand2", command=self.toggle_watching)
        self.start_btn.pack(side="left", padx=(0, 10))

        self._audio_cb = tk.Checkbutton(
            self._row1, text="◉ AUDIO", variable=self.sound_enabled,
            font=(MONO_FONT, 9), fg=C["dim"], bg=C["panel2"],
            selectcolor=C["bg"], activebackground=C["panel2"],
            activeforeground=C["accent"], highlightthickness=0)
        self._audio_cb.pack(side="left")

        # ── Row 2: Timing ──
        self._row2 = tk.Frame(self._controls, bg=C["panel2"])
        self._row2.pack(fill="x", pady=(0, 6))

        self._timing_widgets = []
        for label_text, var_default, var_name in [
            ("INTERVAL", "1.5", "interval_var"), ("COOLDOWN", "5", "cooldown_var")]:
            grp = tk.Frame(self._row2, bg=C["panel2"])
            grp.pack(side="left", padx=(0, 16))
            lbl = tk.Label(grp, text=label_text, font=(MONO_FONT, 7),
                           fg=C["dim"], bg=C["panel2"])
            lbl.pack(side="left")
            sv = tk.StringVar(value=var_default)
            setattr(self, var_name, sv)
            ent = tk.Entry(grp, textvariable=sv, font=(MONO_FONT, 10),
                           fg=C["accent"], bg=C["bg"], insertbackground=C["accent"],
                           relief="flat", width=4, highlightthickness=1,
                           highlightcolor=C["border_dim"], highlightbackground=C["muted"])
            ent.pack(side="left", padx=(4, 2))
            slbl = tk.Label(grp, text="s", font=(MONO_FONT, 8),
                            fg=C["dim"], bg=C["panel2"])
            slbl.pack(side="left")
            self._timing_widgets.extend([grp, lbl, ent, slbl])

        # ── OCR readout (full width) ──
        self._ocr_frame = tk.Frame(self._controls, bg=C["panel2"])
        self._ocr_frame.pack(fill="x", pady=(0, 6))
        self._ocr_label = tk.Label(self._ocr_frame, text="OCR", font=(MONO_FONT, 7),
                                   fg=C["dim"], bg=C["panel2"])
        self._ocr_label.pack(side="left")
        self._ocr_value = tk.Label(self._ocr_frame, textvariable=self.ocr_result,
                                   font=(MONO_FONT, 9), fg=C["yellow"],
                                   bg=C["panel2"], anchor="w")
        self._ocr_value.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # ── Row 3: Search text + Key action ──
        self._row2_sep = tk.Frame(self._controls, bg=C["border_dim"], height=1)
        self._row2_sep.pack(fill="x", pady=(2, 6))

        self._row3 = tk.Frame(self._controls, bg=C["panel2"])
        self._row3.pack(fill="x")

        # Search text
        self._search_grp = tk.Frame(self._row3, bg=C["panel2"])
        self._search_grp.pack(side="left", padx=(0, 16))
        self._scan_label = tk.Label(self._search_grp, text="SCAN FOR", font=(MONO_FONT, 7),
                                    fg=C["dim"], bg=C["panel2"])
        self._scan_label.pack(side="left")
        self.search_var = tk.StringVar(value="Allow")
        self._search_entry = tk.Entry(self._search_grp, textvariable=self.search_var,
                                      font=(MONO_FONT, 10),
                                      fg=C["accent"], bg=C["bg"], insertbackground=C["accent"],
                                      relief="flat", width=14, highlightthickness=1,
                                      highlightcolor=C["border_dim"],
                                      highlightbackground=C["muted"])
        self._search_entry.pack(side="left", padx=(4, 0))

        # Key action
        self._key_grp = tk.Frame(self._row3, bg=C["panel2"])
        self._key_grp.pack(side="left")
        self._key_label = tk.Label(self._key_grp, text="KEY", font=(MONO_FONT, 7),
                                   fg=C["dim"], bg=C["panel2"])
        self._key_label.pack(side="left")
        self.key_var = tk.StringVar(value="enter")
        self._key_entry = tk.Entry(self._key_grp, textvariable=self.key_var,
                                   font=(MONO_FONT, 10),
                                   fg=C["accent"], bg=C["bg"], insertbackground=C["accent"],
                                   relief="flat", width=14, highlightthickness=1,
                                   highlightcolor=C["border_dim"],
                                   highlightbackground=C["muted"])
        self._key_entry.pack(side="left", padx=(4, 0))

        self._controls_sep = tk.Frame(self.root, bg=C["border_dim"], height=1)
        self._controls_sep.pack(fill="x")

        # ── Log ──
        self._log_outer = tk.Frame(self.root, bg=C["bg"], padx=10, pady=6)
        self._log_outer.pack(fill="both", expand=True)

        self._log_title = tk.Label(self._log_outer, text="◈ ACTIVITY LOG", font=(MONO_FONT, 8),
                                   fg=C["border"], bg=C["bg"])
        self._log_title.pack(anchor="w", pady=(0, 4))

        self.log_text = tk.Text(
            self._log_outer, font=(MONO_FONT, 9), fg=C["log_text"], bg=C["logbg"],
            insertbackground=C["accent"], relief="flat", wrap="word",
            state="disabled", padx=10, pady=8,
            highlightthickness=2, highlightcolor=C["border"],
            highlightbackground=C["border_dim"])
        self.log_text.pack(fill="both", expand=True)

        self.log_text.tag_configure("accent", foreground=C["accent"])
        self.log_text.tag_configure("green", foreground=C["green"])
        self.log_text.tag_configure("red", foreground=C["accent_hi"])
        self.log_text.tag_configure("yellow", foreground=C["yellow"])
        self.log_text.tag_configure("dim", foreground=C["dim"])

        self._bottom_accent = tk.Frame(self.root, bg=C["border"], height=2)
        self._bottom_accent.pack(fill="x")

    # ── Overlay (Scan Frame) ──────────────────────────────────────────────

    def _build_overlay(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title("")
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)

        system = platform.system()
        if system == "Windows":
            self.overlay.configure(bg=TRANSPARENT_COLOR)
            self.overlay.attributes("-transparentcolor", TRANSPARENT_COLOR)
            frame_bg = TRANSPARENT_COLOR
            canvas_bg = TRANSPARENT_COLOR
        elif system == "Darwin":
            # Use semi-transparent overlay (simpler and more reliable than systemTransparent)
            self.overlay.attributes("-alpha", 0.3)
            frame_bg = C["panel"]
            canvas_bg = C["panel"]
        else:
            self.overlay.attributes("-alpha", 0.4)
            frame_bg = C["panel"]
            canvas_bg = C["panel"]

        self.overlay_frame = tk.Frame(self.overlay, bg=frame_bg)
        self.overlay_frame.pack(fill="both", expand=True)

        # Top accent line
        self._ov_top_accent = tk.Frame(self.overlay_frame, bg=C["border"], height=2)
        self._ov_top_accent.pack(fill="x", side="top")

        # Top resize strip
        self._top_edge_zone = 30
        self.top_edge = tk.Frame(self.overlay_frame, bg=C["panel"], height=6,
                                 cursor="sb_v_double_arrow")
        self.top_edge.pack(fill="x", side="top")
        self.top_edge.bind("<ButtonPress-1>", self._resize_press)
        self.top_edge.bind("<B1-Motion>", lambda e: self._resize_motion(e, "n"))

        # Top move/resize bar
        self.move_bar = tk.Label(
            self.overlay_frame,
            text="═══ ⟐ Resize over Claude's Reply box ⟐ ═══",
            font=(MONO_FONT, 8, "bold"), fg=C["accent"], bg=C["panel"],
            cursor="fleur", padx=4, pady=3)
        self.move_bar.pack(fill="x", side="top")
        self.move_bar.bind("<ButtonPress-1>", self._topbar_press)
        self.move_bar.bind("<B1-Motion>", self._topbar_motion)
        self.move_bar.bind("<Motion>", self._topbar_hover)

        # Bottom accent + resize bar
        self._ov_bottom_accent = tk.Frame(self.overlay_frame, bg=C["border"], height=2)
        self._ov_bottom_accent.pack(fill="x", side="bottom")
        self.bottom_bar = tk.Label(
            self.overlay_frame, text="◆ ◆ ◆  DRAG TO RESIZE  ◆ ◆ ◆",
            font=(MONO_FONT, 7), fg=C["dim"], bg=C["panel"],
            cursor="sb_v_double_arrow", padx=4, pady=2)
        self.bottom_bar.pack(fill="x", side="bottom")
        self.bottom_bar.bind("<ButtonPress-1>", self._resize_press)
        self.bottom_bar.bind("<B1-Motion>", lambda e: self._resize_motion(e, "s"))

        # Corner handles (on overlay itself so they float above everything)
        corner_size = 16
        corner_bg = C["border_dim"]

        self.corner_bl = tk.Frame(self.overlay, bg=corner_bg,
                                  width=corner_size, height=corner_size, cursor=CURSOR_NE_SW)
        self.corner_bl.bind("<ButtonPress-1>", self._resize_press)
        self.corner_bl.bind("<B1-Motion>", lambda e: self._resize_motion(e, "sw"))

        self.corner_br = tk.Frame(self.overlay, bg=corner_bg,
                                  width=corner_size, height=corner_size, cursor=CURSOR_NW_SE)
        self.corner_br.bind("<ButtonPress-1>", self._resize_press)
        self.corner_br.bind("<B1-Motion>", lambda e: self._resize_motion(e, "se"))

        self.corner_tl = tk.Frame(self.overlay, bg=corner_bg,
                                  width=corner_size, height=corner_size, cursor=CURSOR_NW_SE)
        self.corner_tl.bind("<ButtonPress-1>", self._resize_press)
        self.corner_tl.bind("<B1-Motion>", lambda e: self._resize_motion(e, "nw"))

        self.corner_tr = tk.Frame(self.overlay, bg=corner_bg,
                                  width=corner_size, height=corner_size, cursor=CURSOR_NE_SW)
        self.corner_tr.bind("<ButtonPress-1>", self._resize_press)
        self.corner_tr.bind("<B1-Motion>", lambda e: self._resize_motion(e, "ne"))

        # Left/Right edges
        edge_bg = C["panel"]
        self._left_edge = tk.Frame(self.overlay_frame, bg=edge_bg, width=8,
                                   cursor="sb_h_double_arrow")
        self._left_edge.pack(fill="y", side="left")
        self._left_edge.bind("<ButtonPress-1>", self._resize_press)
        self._left_edge.bind("<B1-Motion>", lambda e: self._resize_motion(e, "w"))

        self._right_edge = tk.Frame(self.overlay_frame, bg=edge_bg, width=8,
                                    cursor="sb_h_double_arrow")
        self._right_edge.pack(fill="y", side="right")
        self._right_edge.bind("<ButtonPress-1>", self._resize_press)
        self._right_edge.bind("<B1-Motion>", lambda e: self._resize_motion(e, "e"))

        # Canvas
        self.cv = tk.Canvas(self.overlay_frame, highlightthickness=0,
                            bg=canvas_bg, cursor="crosshair")
        self.cv.pack(fill="both", expand=True)
        self.cv.bind("<ButtonPress-1>", self._cv_press)
        self.cv.bind("<B1-Motion>", self._cv_motion)
        self.cv.bind("<ButtonRelease-1>", self._cv_release)
        self.cv.bind("<Configure>", lambda e: self._draw_reticle())

        self.overlay.bind("<Configure>", self._on_overlay_configure)
        self.overlay.geometry("500x90+350+650")

        self._drag_data = {"x": 0, "y": 0}
        self._rz = {"x": 0, "y": 0, "ox": 0, "oy": 0, "ow": 0, "oh": 0}
        self._reticle_dragging = False
        self._topbar_mode = "move"

    def _on_overlay_configure(self, event):
        cs = 16
        try:
            w = self.overlay.winfo_width()
            h = self.overlay.winfo_height()
            self.corner_tl.place(x=0, y=0)
            self.corner_tr.place(x=w - cs, y=0)
            self.corner_bl.place(x=0, y=h - cs)
            self.corner_br.place(x=w - cs, y=h - cs)
            self.corner_tl.tkraise()
            self.corner_tr.tkraise()
            self.corner_bl.tkraise()
            self.corner_br.tkraise()
        except Exception:
            pass

    # ── Theme Switching ─────────────────────────────────────────────────

    def _toggle_theme_bar(self):
        self._theme_visible = not self._theme_visible
        self._theme_toggle.configure(text="▾" if self._theme_visible else "▸")
        for swatch in self._theme_swatches.values():
            if self._theme_visible:
                swatch.pack(side="left", padx=2)
            else:
                swatch.pack_forget()

    def apply_theme(self, theme_name):
        if theme_name not in PALETTES:
            return
        global C
        self.current_theme = theme_name
        C.update(PALETTES[theme_name])
        self._apply_colors()
        try:
            THEME_FILE.write_text(theme_name)
        except Exception:
            pass

    def _apply_colors(self):
        # Main window
        self.root.configure(bg=C["bg"])

        # Header
        for w in [self._header, self._title_frame, self._status_frame]:
            w.configure(bg=C["panel"])
        self.pulse_dot.configure(bg=C["panel"])
        self._title_label.configure(fg=C["accent"], bg=C["panel"])
        self._version_label.configure(fg=C["dim"], bg=C["panel"])
        self._approvals_text.configure(fg=C["dim"], bg=C["panel"])
        self.approvals_label.configure(fg=C["accent"], bg=C["panel"])
        self._status_sep.configure(fg=C["dim"], bg=C["panel"])
        if not self.watching:
            self.status_label.configure(fg=C["dim"], bg=C["panel"])
            self.status_dot.configure(fg=C["dim"], bg=C["panel"])
        else:
            self.status_label.configure(bg=C["panel"])
            self.status_dot.configure(bg=C["panel"])
        self._top_accent.configure(bg=C["border"])
        self._header_sep.configure(bg=C["border_dim"])

        # Controls area
        for w in [self._controls, self._theme_row, self._row1, self._row2, self._row3,
                  self._search_grp, self._key_grp,
                  self._ocr_frame]:
            w.configure(bg=C["panel2"])

        # Theme row
        self._theme_toggle.configure(fg=C["dim"], bg=C["panel2"])
        self._theme_label.configure(fg=C["dim"], bg=C["panel2"])
        for name, swatch in self._theme_swatches.items():
            swatch.configure(highlightbackground=(
                C["accent"] if name == self.current_theme else C["muted"]))

        # Buttons
        if self.watching:
            self.start_btn.configure(bg=C["accent_dk"], activebackground=C["red_dim"])
        else:
            self.start_btn.configure(bg=C["accent"], activebackground=C["accent_hi"])

        self._audio_cb.configure(fg=C["dim"], bg=C["panel2"], selectcolor=C["bg"],
                                 activebackground=C["panel2"], activeforeground=C["accent"])

        # Timing widgets (grp frames, labels, entries, s-labels)
        for w in self._timing_widgets:
            cls = w.winfo_class()
            if cls == "Frame":
                w.configure(bg=C["panel2"])
            elif cls == "Label":
                w.configure(fg=C["dim"], bg=C["panel2"])
            elif cls == "Entry":
                w.configure(fg=C["accent"], bg=C["bg"], insertbackground=C["accent"],
                            highlightcolor=C["border_dim"], highlightbackground=C["muted"])

        # OCR
        self._ocr_label.configure(fg=C["dim"], bg=C["panel2"])
        self._ocr_value.configure(fg=C["yellow"], bg=C["panel2"])

        # Search / Key labels and entries
        self._scan_label.configure(fg=C["dim"], bg=C["panel2"])
        self._key_label.configure(fg=C["dim"], bg=C["panel2"])
        for ent in [self._search_entry, self._key_entry]:
            ent.configure(fg=C["accent"], bg=C["bg"], insertbackground=C["accent"],
                          highlightcolor=C["border_dim"], highlightbackground=C["muted"])

        # Separators
        self._row2_sep.configure(bg=C["border_dim"])
        self._controls_sep.configure(bg=C["border_dim"])

        # Log area
        self._log_outer.configure(bg=C["bg"])
        self._log_title.configure(fg=C["border"], bg=C["bg"])
        self.log_text.configure(fg=C["log_text"], bg=C["logbg"],
                                insertbackground=C["accent"],
                                highlightcolor=C["border"], highlightbackground=C["border_dim"])
        self.log_text.tag_configure("accent", foreground=C["accent"])
        self.log_text.tag_configure("green", foreground=C["green"])
        self.log_text.tag_configure("red", foreground=C["accent_hi"])
        self.log_text.tag_configure("yellow", foreground=C["yellow"])
        self.log_text.tag_configure("dim", foreground=C["dim"])
        self._bottom_accent.configure(bg=C["border"])

        # Overlay
        self._ov_top_accent.configure(bg=C["border"])
        self._ov_bottom_accent.configure(bg=C["border"])
        self.top_edge.configure(bg=C["panel"])
        self.move_bar.configure(fg=C["accent"], bg=C["panel"])
        self.bottom_bar.configure(fg=C["dim"], bg=C["panel"])
        self._left_edge.configure(bg=C["panel"])
        self._right_edge.configure(bg=C["panel"])
        for corner in [self.corner_tl, self.corner_tr, self.corner_bl, self.corner_br]:
            corner.configure(bg=C["border_dim"])

        # Redraw reticle with new colors
        self._draw_reticle()

    # ── Overlay interaction ───────────────────────────────────────────────

    def _topbar_hover(self, event):
        w = self.move_bar.winfo_width()
        z = self._top_edge_zone
        if event.x < z:
            self.move_bar.configure(cursor=CURSOR_NW_SE)
        elif event.x > w - z:
            self.move_bar.configure(cursor=CURSOR_NE_SW)
        else:
            self.move_bar.configure(cursor="fleur")

    def _topbar_press(self, event):
        w = self.move_bar.winfo_width()
        z = self._top_edge_zone
        if event.x < z:
            self._topbar_mode = "nw"
            self._resize_press(event)
        elif event.x > w - z:
            self._topbar_mode = "ne"
            self._resize_press(event)
        else:
            self._topbar_mode = "move"
            self._drag_data["x"] = event.x_root - self.overlay.winfo_x()
            self._drag_data["y"] = event.y_root - self.overlay.winfo_y()

    def _topbar_motion(self, event):
        if self._topbar_mode == "move":
            self.overlay.geometry(
                f"+{event.x_root - self._drag_data['x']}+{event.y_root - self._drag_data['y']}")
        else:
            self._resize_motion(event, self._topbar_mode)

    def _resize_press(self, event):
        self._rz = {
            "x": event.x_root, "y": event.y_root,
            "ox": self.overlay.winfo_x(), "oy": self.overlay.winfo_y(),
            "ow": self.overlay.winfo_width(), "oh": self.overlay.winfo_height(),
        }

    def _resize_motion(self, event, edges):
        dx = event.x_root - self._rz["x"]
        dy = event.y_root - self._rz["y"]
        x, y = self._rz["ox"], self._rz["oy"]
        w, h = self._rz["ow"], self._rz["oh"]
        if "e" in edges: w = max(150, w + dx)
        if "s" in edges: h = max(60, h + dy)
        if "w" in edges:
            nw = max(150, w - dx); x += w - nw; w = nw
        if "n" in edges:
            nh = max(60, h - dy); y += h - nh; h = nh
        self.overlay.geometry(f"{w}x{h}+{x}+{y}")

    def _cv_press(self, event):
        self._reticle_dragging = True
        self._update_reticle(event)

    def _cv_motion(self, event):
        if self._reticle_dragging:
            self._update_reticle(event)

    def _cv_release(self, event):
        if self._reticle_dragging:
            self._reticle_dragging = False
            sx, sy = self._get_reticle_screen_pos()
            self.log(f"◎ Target locked: ({sx}, {sy})")

    def _update_reticle(self, event):
        w, h = self.cv.winfo_width(), self.cv.winfo_height()
        if w > 0 and h > 0:
            self.reticle_cx = max(0.02, min(0.98, event.x / w))
            self.reticle_cy = max(0.02, min(0.98, event.y / h))
            self._draw_reticle()

    def _draw_reticle(self):
        self.cv.delete("all")
        w, h = self.cv.winfo_width(), self.cv.winfo_height()
        if w < 10 or h < 10:
            return
        cx = int(self.reticle_cx * w)
        cy = int(self.reticle_cy * h)

        col = C["accent"]
        col_hi = C["accent_hi"]
        bk = 20
        for x0, y0, dx, dy in [
            (2, 2, 1, 1), (w-2, 2, -1, 1), (2, h-2, 1, -1), (w-2, h-2, -1, -1)]:
            self.cv.create_line(x0, y0, x0+dx*bk, y0, fill=col, width=2)
            self.cv.create_line(x0, y0, x0, y0+dy*bk, fill=col, width=2)

        r = 14
        self.cv.create_oval(cx-r, cy-r, cx+r, cy+r, outline=col, width=2)
        self.cv.create_oval(cx-6, cy-6, cx+6, cy+6, outline=col_hi, width=1)
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            self.cv.create_line(cx+dx*(r+1), cy+dy*(r+1),
                                cx+dx*(r+5), cy+dy*(r+5), fill=col, width=2)
        self.cv.create_oval(cx-3, cy-3, cx+3, cy+3, fill=col, outline=col_hi)

    def _get_reticle_screen_pos(self):
        self.overlay.update_idletasks()
        return (self.cv.winfo_rootx() + int(self.reticle_cx * self.cv.winfo_width()),
                self.cv.winfo_rooty() + int(self.reticle_cy * self.cv.winfo_height()))

    # ── Screenshot ────────────────────────────────────────────────────────

    def capture_region(self):
        if not HAS_PIL:
            return None
        try:
            # Get coordinates before any window changes
            cx, cy = self.cv.winfo_rootx(), self.cv.winfo_rooty()
            cw, ch = self.cv.winfo_width(), self.cv.winfo_height()

            if _SYSTEM == "Darwin":
                # On Mac, withdraw overlay so it doesn't appear in screenshot
                self.overlay.withdraw()
                self.overlay.update_idletasks()
                time.sleep(0.05)
                # Apply Retina scaling to bbox coordinates
                s = self._retina_scale
                img = ImageGrab.grab(bbox=(cx * s, cy * s, (cx + cw) * s, (cy + ch) * s))
                self.overlay.deiconify()
            else:
                # On Windows, clear reticle (overlay is transparent to screenshots)
                self.cv.delete("all")
                self.cv.update_idletasks()
                time.sleep(0.02)
                img = ImageGrab.grab(bbox=(cx, cy, cx + cw, cy + ch))

            self._draw_reticle()
            return img
        except Exception:
            if _SYSTEM == "Darwin":
                try:
                    self.overlay.deiconify()
                except Exception:
                    pass
            self._draw_reticle()
            return None

    # ── Pulse ─────────────────────────────────────────────────────────────

    def _start_pulse(self):
        self._pulse_phase = (self._pulse_phase + 1) % 40
        p = self._pulse_phase
        if self.watching and not self.alert_cooldown:
            self.pulse_dot.configure(fg=C["accent"] if p < 20 else C["accent_dim"])
        elif self.alert_cooldown:
            self.pulse_dot.configure(fg=C["yellow"] if p % 4 < 2 else C["red"])
        else:
            self.pulse_dot.configure(fg=C["dim"] if p < 30 else C["accent_dim"])
        self.root.after(100, self._start_pulse)

    # ── Watch Logic ───────────────────────────────────────────────────────

    def toggle_watching(self):
        self.stop_watching() if self.watching else self.start_watching()

    def start_watching(self):
        if not HAS_PIL:
            self.log("✖ MISSING: pip install Pillow"); return
        if not HAS_PYAUTOGUI:
            self.log("✖ MISSING: pip install pyautogui"); return
        if not HAS_OCR:
            if _SYSTEM == "Windows":
                self.log("✖ MISSING: pip install winocr")
            else:
                self.log("✖ MISSING: pip install pytesseract (+ install tesseract)")
            return
        try:
            self.check_interval = float(self.interval_var.get())
            self.cooldown_seconds = float(self.cooldown_var.get())
        except ValueError:
            self.check_interval, self.cooldown_seconds = 1.5, 5

        search = self.search_var.get().strip()
        key = self.key_var.get().strip()
        if not search:
            self.log("✖ SCAN FOR text cannot be empty"); return
        if not key:
            self.log("✖ KEY action cannot be empty"); return

        self.watching = True
        self.alert_cooldown = False
        self.total_scans = 0
        self.start_btn.configure(text="■  DISENGAGE", bg=C["accent_dk"], fg=C["white"],
                                 activebackground=C["red_dim"])
        self.status_text.set("SCANNING")
        self.status_label.configure(fg=C["green"])
        self.status_dot.configure(fg=C["green"])
        self.log(f"◉ SCANNING for \"{search}\" — action: click + [{key}]")
        threading.Thread(target=self._watch_loop, daemon=True).start()

    def stop_watching(self):
        self.watching = False
        self.start_btn.configure(text="▶  ENGAGE", bg=C["accent"], fg=C["white"],
                                 activebackground=C["accent_hi"])
        self.status_text.set("STANDBY")
        self.status_label.configure(fg=C["dim"])
        self.status_dot.configure(fg=C["dim"])
        self.log("◻ DISENGAGED")

    def _watch_loop(self):
        search = self.search_var.get().strip()
        while self.watching:
            if not self.alert_cooldown:
                img = self.capture_region()
                if img:
                    self.total_scans += 1
                    detected, ocr_text = detect_prompt(img, search)
                    n = self.total_scans

                    # Truncate OCR display
                    display = ocr_text[:80] if ocr_text else "—"
                    self.root.after(0, lambda d=display: self.ocr_result.set(d))

                    if detected:
                        self.root.after(0, lambda s=n, t=ocr_text: self._approve(s, t))
                    else:
                        self.root.after(0, lambda s=n: self.status_text.set(f"SCAN #{s}"))
            time.sleep(self.check_interval)

    def _approve(self, scan, ocr_text):
        self.alert_cooldown = True
        self.total_approvals += 1
        search = self.search_var.get().strip()
        self.approvals_label.configure(text=str(self.total_approvals))
        self.status_text.set("⚡ APPROVING")
        self.status_label.configure(fg=C["yellow"])
        self.status_dot.configure(fg=C["yellow"])
        self.log(f"⚡ FOUND \"{search}\" [scan #{scan}] — APPROVE #{self.total_approvals}")

        if self.sound_enabled.get():
            play_alert_sound()
        send_notification("Claude Watcher", f"Found \"{search}\" — auto-approving!")
        threading.Thread(target=self._do_approve, daemon=True).start()

        def reset():
            self.alert_cooldown = False
            if self.watching:
                self.status_text.set("SCANNING")
                self.status_label.configure(fg=C["green"])
                self.status_dot.configure(fg=C["green"])
                self.log("◉ Cooldown reset — scanning...")
        self.root.after(int(self.cooldown_seconds * 1000), reset)

    def _do_approve(self):
        if not HAS_PYAUTOGUI:
            return
        try:
            sx, sy = self._get_reticle_screen_pos()
            key_str = self.key_var.get().strip()
            keys = parse_key_action(key_str)

            self.root.after(0, lambda: self.overlay.withdraw())
            time.sleep(0.3)
            pyautogui.click(sx, sy)
            time.sleep(0.3)
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            time.sleep(0.3)
            self.root.after(0, lambda: self.overlay.deiconify())
            self.root.after(0, lambda: self.log(f"✓ APPROVED — click ({sx},{sy}) + [{key_str}]"))
        except Exception as e:
            self.root.after(0, lambda: self.overlay.deiconify())
            self.root.after(0, lambda: self.log(f"✖ FAILED: {e}"))

    @staticmethod
    def _detect_retina_scale():
        """Detect Retina scaling on macOS. Returns 1 on non-Retina or non-Mac."""
        if _SYSTEM != "Darwin":
            return 1
        try:
            out = subprocess.check_output(
                ["system_profiler", "SPDisplaysDataType"], text=True,
                timeout=5, stderr=subprocess.DEVNULL)
            if "Retina" in out:
                return 2
        except Exception:
            pass
        return 1

    def _check_dependencies(self):
        missing = []
        if not HAS_PIL: missing.append("Pillow")
        if not HAS_PYAUTOGUI: missing.append("pyautogui")
        if not HAS_OCR:
            if _SYSTEM == "Windows":
                missing.append("winocr")
            else:
                missing.append("pytesseract")
        if missing:
            self.log(f"✖ INSTALL: pip install {' '.join(missing)}")
            if "pytesseract" in missing:
                self.log("✖ Also install tesseract: brew install tesseract (Mac)")
        # macOS permission checks
        if _SYSTEM == "Darwin":
            self._check_mac_permissions()

    def _check_mac_permissions(self):
        """Check for Screen Recording and Accessibility permissions on macOS."""
        if HAS_PIL:
            try:
                img = ImageGrab.grab(bbox=(0, 0, 100, 100))
                pixels = list(img.getdata())[:100]
                if all(p == (0, 0, 0) or p == (0, 0, 0, 255) for p in pixels):
                    self.log("⚠ macOS Screen Recording permission required")
                    self.log("  → System Settings → Privacy → Screen Recording")
            except Exception:
                self.log("⚠ Could not verify Screen Recording permission")
        self.log("▸ macOS: Ensure Accessibility permission is granted")
        self.log("  → System Settings → Privacy → Accessibility")

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f" {ts}  ", "dim")
        if "APPROVED" in msg or "✓" in msg: tag = "green"
        elif "FOUND" in msg or "⚡" in msg: tag = "yellow"
        elif "✖" in msg or "FAILED" in msg: tag = "red"
        elif "SCAN" in msg or "◉" in msg: tag = "accent"
        else: tag = "dim"
        self.log_text.insert("end", f"{msg}\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   ⬡  CLAUDE CODE AUTO-BOT v1.0               ║
    ║   Auto-approves Claude Code prompts           ║
    ║   Install:  pip install -r requirements.txt   ║
    ╚═══════════════════════════════════════════════╝
    """)
    app = ClaudeAutoBot()
    app.run()
