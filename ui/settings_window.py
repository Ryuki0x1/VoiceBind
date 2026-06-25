import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import logging
import webbrowser

from config.settings import app_settings
from config.constants import MODELS_DIR, MODEL_FOLDERS, ASSETS_DIR
from audio.device import get_input_devices
from download_model import is_model_downloaded, download_and_extract
from utils.startup import sync_startup_state
from recognition.engine import engine

logger = logging.getLogger(__name__)

THEME = "flatly"
MODEL_CODES = {"English (US)": "en-US", "English (India)": "en-IN"}


class SettingsWindow:
    def __init__(self, setup_mode=False):
        self.setup_mode = setup_mode
        self.root = tb.Window(themename=THEME)
        self.root.title("VoiceClip Setup" if setup_mode else "VoiceClip Settings")
        self.root.resizable(False, False)

        icon_path = ASSETS_DIR / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        self.root.update_idletasks()
        w, h = 620, 560
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.settings = app_settings.model_dump()
        self.command_rows = []

        self._build_ui()

    def _build_ui(self):
        if self.setup_mode:
            header = tb.Frame(self.root)
            header.pack(fill=tk.X, padx=20, pady=(20, 0))
            tb.Label(header, text="Welcome to VoiceClip!",
                     font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)
            tb.Label(header, text="Set up your voice commands and preferences below to get started.",
                     font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(5, 0))
            tb.Separator(self.root).pack(fill=tk.X, padx=20, pady=10)

        notebook = tb.Notebook(self.root)
        self._build_commands_tab(notebook)
        self._build_audio_tab(notebook)
        self._build_general_tab(notebook)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        btn_frame = tb.Frame(self.root)
        btn_frame.pack(pady=(5, 2))
        tb.Button(btn_frame, text="Save and Start" if self.setup_mode else "Save",
                  bootstyle=SUCCESS, command=self._save, width=15).pack(side=tk.LEFT, padx=5)
        if not self.setup_mode:
            tb.Button(btn_frame, text="Cancel", bootstyle=SECONDARY,
                      command=self.root.destroy, width=10).pack(side=tk.LEFT, padx=5)

        footer = tb.Frame(self.root)
        footer.pack(fill=tk.X, padx=20, pady=(0, 8))
        tb.Label(footer, text="github", foreground="#888").pack(side=tk.LEFT)
        gh = tb.Label(footer, text="  @ryuki0x1", cursor="hand2",
                      foreground="#888")
        gh.pack(side=tk.LEFT)
        gh.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Ryuki0x1"))
        tb.Label(footer, text="made with \u2665", foreground="#888").pack(side=tk.LEFT, expand=True)
        tb.Label(footer, text="discord  ", foreground="#888").pack(side=tk.RIGHT)
        tb.Label(footer, text="@ryukiwp", foreground="#888").pack(side=tk.RIGHT)

    # ── Commands Tab ──────────────────────────────────────────────

    def _build_commands_tab(self, notebook):
        frame = tb.Frame(notebook)
        notebook.add(frame, text="Commands")

        header = tb.Frame(frame)
        header.pack(fill=tk.X, pady=(10, 5))
        tb.Label(header, text="Voice Phrase", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(10, 70))
        tb.Label(header, text="Hotkey", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        canvas = tk.Canvas(frame, highlightthickness=0, bg=self.root.cget("bg"))
        scrollbar = tb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tb.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for phrase, hotkey in self.settings["commands"]["mapping"].items():
            self._add_command_row(scrollable, phrase, hotkey)

        tb.Button(frame, text="+ Add Command", bootstyle=SECONDARY,
                  command=lambda: self._add_command_row(scrollable, "", "")).pack(pady=(5, 10))

    def _add_command_row(self, parent, phrase, hotkey):
        row = tb.Frame(parent)
        row.pack(fill=tk.X, pady=2, padx=10)

        phrase_var = tk.StringVar(value=phrase)
        hotkey_var = tk.StringVar(value=hotkey)

        tb.Entry(row, textvariable=phrase_var, width=25).pack(side=tk.LEFT, padx=(0, 5))

        hk_entry = tb.Entry(row, textvariable=hotkey_var, width=20, state="readonly")
        hk_entry.pack(side=tk.LEFT, padx=(0, 5))
        self._bind_hotkey_capture(hk_entry, hotkey_var)

        def remove():
            row.destroy()
            self.command_rows = [r for r in self.command_rows if r[2] != row]

        tb.Button(row, text="✕", bootstyle=DANGER, width=3, command=remove).pack(side=tk.LEFT)
        self.command_rows.append((phrase_var, hotkey_var, row))

    @staticmethod
    def _bind_hotkey_capture(entry, var):
        def on_focus_in(event):
            entry.configure(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, "Press keys...")
            entry.configure(state="readonly")
            entry.bind("<KeyPress>", on_key)

        def on_key(event):
            mods = []
            if event.state & 0x0004: mods.append("ctrl")
            if event.state & 0x0001: mods.append("shift")
            if event.state & 0x0008: mods.append("alt")
            if event.state & 0x0080: mods.append("win")

            k = event.keysym.lower()
            if k in ("control_l", "control_r", "shift_l", "shift_r", "alt_l", "alt_r",
                     "super_l", "super_r", "caps_lock", "num_lock"):
                return "break"

            hotkey = "+".join(mods + [k])
            var.set(hotkey)
            entry.configure(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, hotkey)
            entry.configure(state="readonly")
            entry.unbind("<KeyPress>")
            return "break"

        def on_focus_out(event):
            if not var.get():
                entry.configure(state="normal")
                entry.delete(0, tk.END)
                entry.configure(state="readonly")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ── Audio Tab ─────────────────────────────────────────────────

    def _build_audio_tab(self, notebook):
        frame = tb.Frame(notebook)
        notebook.add(frame, text="Audio")

        tb.Label(frame, text="Microphone:", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(15, 2), padx=15)
        self.mic_var = tk.StringVar()
        self.mic_combo = tb.Combobox(frame, textvariable=self.mic_var, state="readonly", width=55)
        self.mic_combo.pack(padx=15, fill=tk.X)
        self._populate_microphones()

        tb.Label(frame, text="Cooldown (seconds):", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(15, 2), padx=15)
        self.cooldown_var = tk.DoubleVar(value=self.settings["audio"]["cooldown_seconds"])
        ttk.Spinbox(frame, from_=0.5, to=10.0, increment=0.5,
                    textvariable=self.cooldown_var, width=10).pack(anchor=tk.W, padx=15)

        self.feedback_var = tk.BooleanVar(value=self.settings["audio"]["audio_feedback_enabled"])
        tb.Checkbutton(frame, text="Play sound on command triggered",
                       variable=self.feedback_var).pack(anchor=tk.W, pady=(15, 0), padx=15)

    def _populate_microphones(self):
        devices = get_input_devices()
        self.mic_combo["values"] = [d["name"] for d in devices]
        current_id = self.settings["audio"]["microphone_id"]
        for d in devices:
            if d["index"] == current_id:
                self.mic_var.set(d["name"])
                return
        if devices:
            self.mic_var.set(devices[0]["name"])

    # ── General Tab ───────────────────────────────────────────────

    def _build_general_tab(self, notebook):
        frame = tb.Frame(notebook)
        notebook.add(frame, text="General")

        self.startup_var = tk.BooleanVar(value=self.settings["general"]["start_with_windows"])
        tb.Checkbutton(frame, text="Start with Windows",
                       variable=self.startup_var).pack(anchor=tk.W, pady=(20, 5), padx=15)

        self.tray_var = tk.BooleanVar(value=self.settings["general"]["minimize_to_tray"])
        tb.Checkbutton(frame, text="Minimize to tray",
                       variable=self.tray_var).pack(anchor=tk.W, padx=15)

        self.debug_var = tk.BooleanVar(value=self.settings["general"]["debug_logging"])
        tb.Checkbutton(frame, text="Debug logging",
                       variable=self.debug_var).pack(anchor=tk.W, pady=(20, 5), padx=15)

        tb.Separator(frame, bootstyle=SECONDARY).pack(fill=tk.X, padx=15, pady=15)

        tb.Label(frame, text="Speech Model:", font=("Segoe UI", 10)).pack(anchor=tk.W, padx=15)
        model_frame = tb.Frame(frame)
        model_frame.pack(fill=tk.X, padx=15, pady=(2, 5))

        current_code = self.settings["general"]["model_language"]
        current_label = next(k for k, v in MODEL_CODES.items() if v == current_code)
        self.model_var = tk.StringVar(value=current_label)
        model_combo = tb.Combobox(model_frame, textvariable=self.model_var,
                                   values=list(MODEL_CODES.keys()), state="readonly", width=18)
        model_combo.pack(side=tk.LEFT)
        model_combo.bind("<<ComboboxSelected>>", lambda e: self._update_model_status())

        self.model_status_var = tk.StringVar()
        self.model_status_label = tb.Label(model_frame, textvariable=self.model_status_var, bootstyle=SECONDARY)
        self.model_status_label.pack(side=tk.LEFT, padx=(10, 0))

        self.download_btn = tb.Button(frame, text="Download", command=self._download_model)

        self._update_model_status()

    def _update_model_status(self):
        code = MODEL_CODES[self.model_var.get()]
        if code == "en-US":
            self.model_status_var.set("Bundled")
            self.download_btn.pack_forget()
        else:
            if is_model_downloaded("en-IN"):
                self.model_status_var.set("Installed")
                self.download_btn.pack_forget()
            else:
                self.model_status_var.set("Not installed")
                self.download_btn.pack(anchor=tk.W, padx=15, pady=5)
                self.download_btn.configure(state="normal")

    def _download_model(self):
        self.download_btn.configure(state="disabled", text="Downloading...")
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        success = download_and_extract("en-IN")
        self.root.after(0, lambda: self._on_download_done(success))

    def _on_download_done(self, success):
        if success:
            self._update_model_status()
            messagebox.showinfo("Done", "English (India) model downloaded.")
        else:
            self.download_btn.configure(state="normal", text="Download")
            messagebox.showerror("Error", "Failed to download. Check your internet connection.")

    # ── Save ──────────────────────────────────────────────────────

    def _get_selected_mic_id(self):
        devices = get_input_devices()
        name = self.mic_var.get()
        for d in devices:
            if d["name"] == name:
                return d["index"]
        return None

    def _save(self):
        mapping = {}
        for phrase_var, hotkey_var, _ in self.command_rows:
            phrase = phrase_var.get().strip().lower()
            hotkey = hotkey_var.get().strip()
            if phrase and hotkey:
                mapping[phrase] = hotkey

        new_lang = MODEL_CODES[self.model_var.get()]
        needs_restart = (
            app_settings.commands.mapping != mapping
            or app_settings.general.model_language != new_lang
        )

        app_settings.commands.mapping = mapping
        app_settings.audio.microphone_id = self._get_selected_mic_id()
        app_settings.audio.cooldown_seconds = self.cooldown_var.get()
        app_settings.audio.audio_feedback_enabled = self.feedback_var.get()
        app_settings.general.start_with_windows = self.startup_var.get()
        app_settings.general.minimize_to_tray = self.tray_var.get()
        app_settings.general.debug_logging = self.debug_var.get()
        app_settings.general.model_language = new_lang
        app_settings.general.setup_completed = True

        app_settings.save()
        sync_startup_state()

        if needs_restart and engine.is_running:
            logger.info("Settings changed, restarting engine...")
            engine.stop()
            engine.start()

        self.root.destroy()

    def run(self):
        self.root.mainloop()


def open_settings_window(setup_mode=False):
    try:
        window = SettingsWindow(setup_mode=setup_mode)
        window.run()
    except Exception as e:
        logger.error(f"Settings window error: {e}")
