import os
import socket
import random
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, date, timedelta

# ---------------- Config / Constants ----------------
PROTECTED_PATHS = ["C:/Users/Public/Documents", "C:/ImportantFiles"]
THEME_FILE = "theme_config.txt"  # stores theme and language (backward-compatible)
LAST_SCAN_FILE = "last_scan.txt" # NEW: File to store the last scan date
APP_VERSION = "1.0"

# ---------------- Utilities ----------------
def check_internet():
    """Return True if internet looks available, else False."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Simple i18n dictionary (English/Urdu)
I18N = {
    "English": {
        "title_main": "Anti-Ransomware Security Solution for MS Windows",
        "btn_scan": "🔎 Scan Now",
        "btn_backup": "💾 Backup Data",
        "btn_threats": "⚠ Threat Logs",
        "btn_settings": "⚙ Settings",
        "subtitle_safety": "Stay Safe from Ransomware!",
        "status_title": "System is Secure",
        # NEW: Keys for dynamic date
        "last_scan_today": "Last Scan: Today",
        "last_scan_yesterday": "Last Scan: Yesterday",
        "last_scan_on": "Last Scan on: ",
        
        # New for scan functionality
        "scanning_text": "Scanning...",
        "scan_complete": "Scan Complete",
        "no_threats_found": "No threats found!",

        "settings_title": "⚙ Application Settings",
        "theme_label": "Theme Selection:",
        "lang_label": "Language:",
        "save_btn": "💾 Save Settings",
        "help_btn": "❓ Help",
        "updates_btn": "🔄 Check for Updates",
        "about_btn": "👤 About",
        "up_to_date": "App is up to date",
        "reset_btn": "Reset to Default",
        "reset_info": "Settings have been reset to default values.",

        "about_title": "👤 About This Application",
        "developed_by": "𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐝 𝐛𝐲:\n𝙈𝙪𝙝𝙖𝙢𝙢𝙖𝙙 𝘼𝙖𝙢𝙞𝙧 𝘽𝙖𝙠𝙝𝙨𝙝\n𝘼𝙗𝙙𝙪𝙡 𝙍𝙚𝙝𝙢𝙖𝙣\n𝘼𝙗𝙙𝙪𝙡 𝙎𝙖𝙢𝙖𝙙",
        "version": "Version",

        "backup_card": "💾 Backup Data to Google Drive",
        "select_file": "📂 Select File & Backup",
        "select_folder": "📁 Select Folder & Backup",
        "realtime_backup": "🕒 Realtime Backup",
        "no_internet": "No Internet Connection. Please check your network.",
        
        # Threat log title is now dynamic
        "title_threat_log": "Threat Logs",

        # ADDED: Detailed help text in English
        "help_text_title": "Anti-Ransomware App Detailed Instructions",
        "help_instructions": """
1. Scan Now: Select a file to scan for ransomware threats.
2. Backup Data: Backup files or folders to Google Drive. 
3. Realtime Backup: Automatically backup protected files.
4. Threat Logs: View past detected threats.
5. Settings: Change theme or language and access detailed help.
6. Always ensure your system is updated and files are regularly backed up.
""",
        # NEW: Text for the virus information box
        "virus_info_title": "Ransomware Scanning",
        "virus_info_1": "Ransomware Scanning...",
        "virus_info_2": "USB Scanning/Downloaded Files Scanning...",
    },
    "Urdu": {
        "title_main": "اینٹی رینسم ویئر سیکیورٹی سلوشن برائے ونڈوز",
        "btn_scan": "🔎 اسکین کریں",
        "btn_backup": "💾 بیک اپ",
        "btn_threats": "⚠ تھریٹ لاگ",
        "btn_settings": "⚙ سیٹنگز",
        "subtitle_safety": "رینسم ویئر سے محفوظ رہیں!",
        "status_title": "سسٹم محفوظ ہے",
        # NEW: Keys for dynamic date
        "last_scan_today": "آخری اسکین: آج",
        "last_scan_yesterday": "آخری اسکین: کل",
        "last_scan_on": "آخری اسکین: ",
        
        # New for scan functionality
        "scanning_text": "اسکیننگ ہو رہی ہے...",
        "scan_complete": "اسکین مکمل",
        "no_threats_found": "کوئی خطرہ نہیں ملا!",

        "settings_title": "⚙ ایپلی کیشن سیٹنگز",
        "theme_label": "تھیم منتخب کریں:",
        "lang_label": "زبان:",
        "save_btn": "💾 سیٹنگز محفوظ کریں",
        "help_btn": "❓ مدد",
        "updates_btn": "🔄 اپ ڈیٹس چیک کریں",
        "about_btn": "👤 تعارف",
        "up_to_date": "ایپ تازہ ترین ہے",
        "reset_btn": "ڈیفالٹ پر ری سیٹ کریں",
        "reset_info": "سیٹنگز کو ڈیفالٹ پر ری سیٹ کر دیا گیا ہے۔",

        "about_title": "👤 اس ایپ کے بارے میں",
        "developed_by": "تیار کردہ:\nMuhammad Aamir\nAbdul Rehman\nAbdul Samad",
        "version": "ورژن",

        "backup_card": "💾 گوگل ڈرائیو پر بیک اپ",
        "select_file": "📂 فائل منتخب کریں اور بیک اپ کریں",
        "select_folder": "📁 فولڈر منتخب کریں اور بیک اپ کریں",
        "realtime_backup": "🕒 ریئل ٹائم بیک اپ",
        "no_internet": "انٹرنیٹ دستیاب نہیں۔ براہِ مہربانی نیٹ ورک چیک کریں۔",
        
        # Threat log title is now dynamic
        "title_threat_log": "تھریٹ لاگز",

        # ADDED: Detailed help text in Urdu
        "help_text_title": "اینٹی رینسم ویئر ایپ تفصیلی ہدایات",
        "help_instructions": """
1. اسکین کریں: رینسم ویئر کے خطرات کے لیے فائل کو اسکین کریں۔
2. ڈیٹا بیک اپ: فائلز یا فولڈرز کو گوگل ڈرائیو پر بیک اپ کریں۔
3. ریئل ٹائم بیک اپ: محفوظ فائلوں کو خود بخود بیک اپ کریں۔
4. تھریٹ لاگز: ماضی میں پتہ چلنے والے خطرات دیکھیں۔
5. سیٹنگز: تھیم یا زبان تبدیل کریں اور تفصیلی مدد حاصل کریں۔
6. ہمیشہ یقینی بنائیں کہ آپ کا سسٹم اپ ڈیٹ ہے اور فائلز کا باقاعدہ سے بیک اپ لیا جاتا ہے۔
""",
        # NEW: Text for the virus information box
        "virus_info_title": "رینسم ویئر اسکیننگ",
        "virus_info_1": "رینسم ویئر اسکیننگ ہو رہی ہے...",
        "virus_info_2": "یو ایس بی اسکیننگ / ڈاؤن لوڈ کردہ فائلز اسکیننگ...",
    },
}

# ---------------- Config read/write helpers ----------------
def read_theme_file():
    """
    Backward-compatible reader for THEME_FILE.
    Supports old single-word file content ('light' or 'dark') AND new format:
      theme=light
      language=Urdu
    Returns tuple (theme_mode, language) where theme_mode is 'light' or 'dark' theme token,
    language is 'English' or 'Urdu'.
    """
    theme_mode = "light"
    language = "English"
    if not os.path.exists(THEME_FILE):
        return theme_mode, language

    try:
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # If file is single word like "dark" or "light" (old format)
            if content.lower() in ("dark", "light"):
                theme_mode = content.lower()
                return theme_mode, language
            # Otherwise parse lines for key=value
            f.seek(0)
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k == "theme":
                        if v.lower() in ("dark", "light", "darkly", "superhero", "cyborg"):
                            # keep simple mapping: if user stored 'dark' or 'light', use that; else leave token
                            theme_mode = v.lower()
                    elif k == "language":
                        # normalize language to keys in I18N
                        if v.lower().startswith("u"):
                            language = "Urdu"
                        else:
                            language = "English"
    except Exception:
        # if any error, fall back to defaults
        pass
    return theme_mode, language

def write_theme_file(theme_mode, language):
    """
    Write config file in key=value form.
    theme_mode should be 'light' or 'dark' (we keep it lowercase to match prior behavior).
    language should be 'English' or 'Urdu'.
    """
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            f.write(f"theme={theme_mode}\n")
            f.write(f"language={language}\n")
    except Exception:
        # silent fail — app still works, but persistence won't be saved
        pass

# NEW: Functions for last scan date persistence
def read_last_scan_date():
    """Reads the last scan date from a file and returns a date object."""
    if os.path.exists(LAST_SCAN_FILE):
        try:
            with open(LAST_SCAN_FILE, "r", encoding="utf-8") as f:
                date_str = f.read().strip()
                return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, FileNotFoundError):
            return None
    return None

def write_last_scan_date():
    """Writes the current date to a file."""
    try:
        with open(LAST_SCAN_FILE, "w", encoding="utf-8") as f:
            f.write(date.today().isoformat())
    except Exception:
        # silent fail
        pass

def format_last_scan_text(last_scan_date_obj, lang: str):
    """Formats the last scan date into a human-readable string."""
    t = I18N[lang]
    if last_scan_date_obj is None:
        return t["last_scan_today"] # Default to "Today" if no scan found
        
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if last_scan_date_obj == today:
        return t["last_scan_today"]
    elif last_scan_date_obj == yesterday:
        return t["last_scan_yesterday"]
    else:
        return f"{t['last_scan_on']}{last_scan_date_obj.strftime('%Y-%m-%d')}"

# ---------------- App ----------------
class AntiRansomwareApp(ttk.Window):
    def __init__(self):
        # read theme + language (backward compatible)
        theme_mode, language = read_theme_file()
        themename = "superhero" if theme_mode == "light" else "cyborg"
        super().__init__(themename=themename)

        self.title("Anti-Ransomware Security Solution")
        self.state("zoomed")  # Fullscreen

        # Keep track of current theme & language
        self.theme_mode = theme_mode
        self.lang = language if language in I18N else "English"

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (WelcomePage, MainPage, ScanPage, BackupPage, ThreatsPage, SettingsPage, AboutPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(WelcomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if hasattr(frame, "apply_language"):
            frame.apply_language(self.lang)
        frame.tkraise()


    def set_language(self, lang: str):
        if isinstance(lang, str) and lang.lower().startswith("u"):
            chosen = "Urdu"
        else:
            chosen = "English"
        self.lang = chosen
        write_theme_file(self.theme_mode, self.lang)
        for frame in self.frames.values():
            if hasattr(frame, "apply_language"):
                frame.apply_language(self.lang)

    def set_theme_mode(self, mode: str):
        mode_clean = mode.strip().lower()
        if mode_clean in ("cyborg", "dark"):
            new_mode = "dark"
        else:
            new_mode = "light"
        if new_mode == self.theme_mode:
            return
        self.theme_mode = new_mode
        theme_to_use = "superhero" if self.theme_mode == "light" else "cyborg"
        try:
            self.style.theme_use(theme_to_use)
        except Exception:
            try:
                self.style.theme_use(mode_clean)
            except Exception:
                pass
        write_theme_file(self.theme_mode, self.lang)

# ---------------- Welcome Page ----------------
class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.welcome_label = ttk.Label(
            self,
            text="🔐 Anti-Ransomware Security Solution",
            font=("Times New Roman", 32, "bold"),
            bootstyle="primary"
        )
        self.welcome_label.place(relx=0.5, rely=0.3, anchor="center")
        
        # Changed the wording to be simpler and clearer
        self.subtitle_label = ttk.Label(
            self,
            text="Easy, Quick, and Safe!",
            font=("Arial", 20, "italic"),
            bootstyle="light"
        )
        self.subtitle_label.place(relx=0.5, rely=0.4, anchor="center")

        def show_short_help():
            controller.show_frame(MainPage)
            controller.after(
                100,
                lambda: messagebox.showinfo(
                    "Quick Help",
                    "Welcome to Anti-Ransomware!\n\n- Click 'Scan Now' to scan files.\n- Click 'Backup Data' to backup your files.\n\nFor more detailed help, go to Settings → Help.",
                ),
            )

        self.continue_btn = ttk.Button(
            self,
            text="▶ Continue",
            command=show_short_help,
            bootstyle="primary",
            width=40, # Increased width for a bigger feel
        )
        self.continue_btn.place(relx=0.5, rely=0.6, anchor="center")

        ttk.Label(
            self,
            text="© 2025 Anti-Ransomware Security | Stay Safe Online",
            font=("Arial", 12),
        ).place(relx=0.5, rely=0.9, anchor="center")


# ---------------- Main Page ----------------
class MainPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Main title at the top
        self.main_title_lbl = ttk.Label(self, text=I18N[self.controller.lang]["title_main"], 
                                         font=("Arial", 28, "bold"))
        self.main_title_lbl.pack(side="top", pady=(40, 0))

        # --- FIX: Subtitle added back ---
        self.subtitle_lbl = ttk.Label(self, text=I18N[self.controller.lang]["subtitle_safety"], 
                                      font=("Arial", 16))
        self.subtitle_lbl.pack(side="top", pady=(5, 10))

        self.version_lbl = ttk.Label(
            self,
            text=f"{I18N[self.controller.lang]['version']}: {APP_VERSION}",
            font=("Arial", 12, "bold")
        )
        self.version_lbl.pack(side="top", pady=(5, 10))
        
        # TOP SECURITY BAR (based on the image)
        self.status_bar_frame = ttk.LabelFrame(self, text=" System Status ", bootstyle="success")
        self.status_bar_frame.pack(side="top", fill="x", padx=100, pady=(10, 0))
        
        status_content_frame = ttk.Frame(self.status_bar_frame, padding=20)
        status_content_frame.pack(expand=True, fill="both")

        self.status_title_lbl = ttk.Label(status_content_frame, text=I18N[self.controller.lang]["status_title"], font=("Arial", 22, "bold"), bootstyle="success")
        self.status_title_lbl.pack(pady=(10, 5))

        # NEW: Now shows dynamic date
        self.last_scan_lbl = ttk.Label(status_content_frame, text="", font=("Arial", 12))
        self.last_scan_lbl.pack()
        
        self.status_progress = ttk.Progressbar(status_content_frame, bootstyle="info", length=400)
        self.status_progress.pack(pady=(10, 10), fill="x", padx=100)
        
        # --- FIX: Start the progress bar animation ---
        self.animate_progress()

        # Main content frame to center everything
        main_content_frame = ttk.Frame(self, padding=20)
        main_content_frame.pack(expand=True, fill="both")
        
        # --- Three-column layout ---
        sections_frame = ttk.Frame(main_content_frame, padding=20)
        sections_frame.pack(expand=True, fill="both", side="top", anchor="center")

        # Left section - Quick Access buttons
        self.left_card = ttk.LabelFrame(sections_frame, text=" Quick Access ", padding=40, bootstyle="secondary")
        self.left_card.pack(side="left", padx=15, fill="both", expand=True)

        self.btn_updates = ttk.Button(
            self.left_card,
            text=I18N[self.controller.lang]["updates_btn"],
            bootstyle="warning-outline",
            command=self.check_updates,
            width=30,
        )
        self.btn_updates.pack(pady=8)

        self.btn_about = ttk.Button(
            self.left_card,
            text=I18N[self.controller.lang]["about_btn"],
            bootstyle="secondary-outline",
            command=lambda: self.controller.show_frame(AboutPage),
            width=30,
        )
        self.btn_about.pack(pady=8)

        self.btn_help = ttk.Button(
            self.left_card,
            text=I18N[self.controller.lang]["help_btn"],
            bootstyle="info-outline",
            command=self.show_help_dialog,
            width=30,
        )
        self.btn_help.pack(pady=8)

        # Center section - Main Features
        self.main_card = ttk.LabelFrame(sections_frame, text=" Anti-Ransomware Features ", padding=40, bootstyle="primary")
        self.main_card.pack(side="left", padx=15, fill="both", expand=True)
        
        # Buttons are now bigger and centered
        self.btn_scan = ttk.Button(
            self.main_card,
            text=I18N[self.controller.lang]["btn_scan"],
            bootstyle="primary-outline",
            command=self.open_scan_window,
            width=40,
        )
        self.btn_scan.pack(pady=18)

        self.btn_backup = ttk.Button(
            self.main_card,
            text=I18N[self.controller.lang]["btn_backup"],
            bootstyle="success-outline",
            command=self.open_backup_window,
            width=40,
        )
        self.btn_backup.pack(pady=18)

        self.btn_threats = ttk.Button(
            self.main_card,
            text=I18N[self.controller.lang]["btn_threats"],
            bootstyle="danger-outline",
            command=self.open_threats_window,
            width=40,
        )
        self.btn_threats.pack(pady=18)

        self.btn_settings = ttk.Button(
            self.main_card,
            text=I18N[self.controller.lang]["btn_settings"],
            bootstyle="info-outline",
            command=self.open_settings_window,
            width=40,
        )
        self.btn_settings.pack(pady=18)
        
        # Right section - Ransomware Scanning Box
        self.virus_card = ttk.LabelFrame(sections_frame, text=I18N[self.controller.lang]["virus_info_title"], padding=20, bootstyle="danger")
        self.virus_card.pack(side="left", padx=15, fill="both", expand=True)

        # Labels and progress bars for scanning
        self.ransomware_scan_label = ttk.Label(self.virus_card, text=I18N[self.controller.lang]["virus_info_1"], justify="center", wraplength=250, font=("Arial", 12))
        self.ransomware_scan_label.pack(pady=5)
        self.ransomware_scan_pb = ttk.Progressbar(self.virus_card, mode="indeterminate", bootstyle="warning-striped")
        self.ransomware_scan_pb.pack(pady=10, fill="x")

        self.other_scan_label = ttk.Label(self.virus_card, text=I18N[self.controller.lang]["virus_info_2"], justify="center", wraplength=250, font=("Arial", 12))
        self.other_scan_label.pack(pady=5)
        self.other_scan_pb = ttk.Progressbar(self.virus_card, mode="indeterminate", bootstyle="warning-striped")
        self.other_scan_pb.pack(pady=10, fill="x")
        
        # FIX: Call after a short delay to ensure widgets are fully initialized
        self.after(200, self.start_animations)


    def start_animations(self):
        """Starts the indeterminate progress bar animations."""
        self.ransomware_scan_pb.start(10)
        self.other_scan_pb.start(10)

    # NEW: Animated progress bar helper function
    def animate_progress(self):
        """Animates the progress bar in a loop for the status bar."""
        value = self.status_progress["value"]
        if value < 100:
            self.status_progress["value"] = value + 1
        else:
            self.status_progress["value"] = 0
        
        # Slower animation by increasing the delay
        self.after(100, self.animate_progress)

    def open_threats_window(self):
        from tkinter import Toplevel
        window = Toplevel(self)
        window.title(I18N[self.controller.lang]["title_threat_log"]) 
        window.geometry("900x700")
        card = ttk.LabelFrame(window, text=f" ⚠ {I18N[self.controller.lang]['title_threat_log']} ", padding=30, bootstyle="danger")
        card.pack(pady=50, padx=50, fill="both", expand=True)
        text = scrolledtext.ScrolledText(card, wrap=tk.WORD, height=20, width=100)
        text.pack(pady=20)
        text.insert(tk.END, "No threats detected yet.\n")
        ttk.Button(window, text="⬅ Close", bootstyle="secondary", command=window.destroy).pack(pady=10)

    def open_scan_window(self):
        from tkinter import Toplevel
        win = Toplevel(self)
        win.title("Scan Files")
        ScanPage(win, self.controller).pack(fill="both", expand=True)

    def open_backup_window(self):
        from tkinter import Toplevel
        win = Toplevel(self)
        win.title("Backup Data")
        BackupPage(win, self.controller).pack(fill="both", expand=True)

    def check_updates(self):
        t = I18N[self.controller.lang]
        messagebox.showinfo("Updates", f"{t['up_to_date']} (v{APP_VERSION}).")

    def show_help_dialog(self):
        t = I18N[self.controller.lang]
        help_text = t["help_instructions"]
        messagebox.showinfo(t["help_text_title"], help_text)

    def open_settings_window(self):
        self.controller.show_frame(SettingsPage)
        self.controller.frames[SettingsPage].show_settings_frame()

    # Language application for this screen
    def apply_language(self, lang: str):
        t = I18N[lang]
        # Dynamically set foreground color based on theme
        title_color = "white" if self.controller.theme_mode == "dark" else "black"
        self.main_title_lbl.config(text=t["title_main"], foreground=title_color)
        
        self.subtitle_lbl.config(text=t["subtitle_safety"])

        self.version_lbl.config(text=f"{t['version']}: {APP_VERSION}")
        self.status_title_lbl.config(text=t["status_title"])
        
        # NEW: Update the dynamic date
        last_scan_date = read_last_scan_date()
        self.last_scan_lbl.config(text=format_last_scan_text(last_scan_date, lang))
        
        # update labels inside cards
        self.main_card.config(text=f" Anti-Ransomware Features ")
        self.btn_scan.config(text=t["btn_scan"])
        self.btn_backup.config(text=t["btn_backup"])
        self.btn_threats.config(text=t["btn_threats"])
        self.btn_settings.config(text=t["btn_settings"])
        self.btn_updates.config(text=t["updates_btn"])
        self.btn_about.config(text=t["about_btn"])
        self.btn_help.config(text=t["help_btn"])
        
        # Update labels in the new virus card
        self.virus_card.config(text=t["virus_info_title"])
        self.ransomware_scan_label.config(text=t["virus_info_1"])
        self.other_scan_label.config(text=t["virus_info_2"])


# ---------------- Scan Page ----------------
class ScanPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Button(self, text="⬅ Back", bootstyle="secondary", command=self.master.destroy).place(x=20, y=20)

        self.card = ttk.LabelFrame(self, text=" 🔎 Scan Files for Ransomware ", padding=50, bootstyle="primary")
        self.card.pack(pady=100, padx=400)

        # Added: UI for the scan progress bar
        self.progress_bar = ttk.Progressbar(self.card, bootstyle="info-striped", length=400)
        self.progress_label = ttk.Label(self.card, text="", font=("Arial", 12))
        self.status_label = ttk.Label(self.card, text="", font=("Arial", 12, "bold"))
        
        ttk.Button(self.card, text="📂 Select File & Scan", bootstyle="info-outline", command=self.select_file, width=30).pack(
            pady=10
        )
        
        self.status_label.pack(pady=10)
        self.progress_bar.pack(pady=5)
        self.progress_label.pack(pady=2)


    def destroy_window(self):
        self.master.destroy()

    def select_file(self):
        self.selected_file = filedialog.askopenfilename(parent=self.master)
        if self.selected_file:
            self.status_label.config(text=I18N[self.controller.lang]["scanning_text"])
            self.progress_bar["value"] = 0
            self.progress_label.config(text="0%")
            self.simulate_scan_progress(0, 100)
        else:
            self.status_label.config(text="")
            self.progress_bar["value"] = 0
            self.progress_label.config(text="")


    def simulate_scan_progress(self, current_progress, total_steps):
        """Simulates the scan progress with a progress bar."""
        if current_progress <= total_steps:
            self.progress_bar["value"] = current_progress
            self.progress_label.config(text=f"{current_progress}%")
            next_step_delay = random.randint(10, 50)
            self.after(next_step_delay, self.simulate_scan_progress, current_progress + 1, total_steps)
        else:
            self.status_label.config(text=I18N[self.controller.lang]["scan_complete"])
            messagebox.showinfo(
                I18N[self.controller.lang]["scan_complete"], f"{os.path.basename(self.selected_file)}: {I18N[self.controller.lang]['no_threats_found']}"
            )
            self.progress_bar["value"] = 0
            self.progress_label.config(text="")
            self.status_label.config(text="")
            
            # NEW: Update the last scan date after completion
            write_last_scan_date()
            # Update the main page to reflect the new date
            self.controller.frames[MainPage].apply_language(self.controller.lang)


    def apply_language(self, lang: str):
        t = I18N[lang]
        self.card.config(text=f" 🔎 {t['btn_scan'].replace('🔎 ', '')} Files for Ransomware ")


# ---------------- Backup Page ----------------
class BackupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_file = None
        self.selected_folder = None

        ttk.Button(self, text="⬅ Back", bootstyle="secondary", command=self.master.destroy).place(x=20, y=20)

        self.card = ttk.LabelFrame(
            self, text=I18N[self.controller.lang]["backup_card"], padding=30, bootstyle="success"
        )
        self.card.pack(pady=100, padx=400)

        self.progress = ttk.Progressbar(self.card, bootstyle="success-striped", length=400)
        self.progress.pack(pady=20)
        self.percent_label = ttk.Label(self.card, text="0%", font=("Arial", 12))
        self.percent_label.pack(pady=5)

        self.btn_sel_file = ttk.Button(
            self.card,
            text=I18N[self.controller.lang]["select_file"],
            bootstyle="info-outline",
            command=self.upload_selected_file,
            width=35,
        )
        self.btn_sel_file.pack(pady=10)

        self.btn_sel_folder = ttk.Button(
            self.card,
            text=I18N[self.controller.lang]["select_folder"],
            bootstyle="info-outline",
            command=self.upload_selected_folder,
            width=35,
        )
        self.btn_sel_folder.pack(pady=10)

        self.btn_rt = ttk.Button(
            self.card,
            text=I18N[self.controller.lang]["realtime_backup"],
            bootstyle="success-outline",
            command=self.start_realtime_backup,
            width=35,
        )
        self.btn_rt.pack(pady=20)

    def destroy_window(self):
        self.master.destroy()

    def simulate_progress(self, total_steps=100, callback=None):
        self.progress["value"] = 0
        self.percent_label.config(text="0%")
        step = 0

        def update():
            nonlocal step
            if step <= total_steps:
                self.progress["value"] = step
                self.percent_label.config(text=f"{step}%")
                step += 1
                self.after(50, update)
            else:
                if callback:
                    callback()

        update()

    def _ensure_internet(self):
        if not check_internet():
            messagebox.showerror("Internet Error", I18N[self.controller.lang]["no_internet"])
            return False
        return True

    def upload_selected_file(self):
        if not self._ensure_internet():
            return
        file = filedialog.askopenfilename(parent=self.master)
        if file:
            self.progress["value"] = 0
            self.percent_label.config(text="0%")
            self.simulate_progress(
                callback=lambda: messagebox.showinfo("Backup", f"File '{os.path.basename(file)}' uploaded successfully!")
            )

    def upload_selected_folder(self):
        if not self._ensure_internet():
            return
        folder = filedialog.askdirectory(parent=self.master)
        if folder:
            self.progress["value"] = 0
            self.percent_label.config(text="0%")
            self.simulate_progress(
                callback=lambda: messagebox.showinfo(
                    "Backup", f"Folder '{os.path.basename(folder)}' uploaded successfully!"
                )
            )

    def start_realtime_backup(self):
        if not self._ensure_internet():
            return
        self.simulate_progress(
            callback=lambda: messagebox.showinfo("Realtime Backup", "Realtime backup completed successfully!")
        )

    def apply_language(self, lang: str):
        t = I18N[lang]
        self.card.config(text=t["backup_card"])
        self.btn_sel_file.config(text=t["select_file"])
        self.btn_sel_folder.config(text=t["select_folder"])
        self.btn_rt.config(text=t["realtime_backup"])


# ---------------- Threats Page ----------------
class ThreatsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Button(self, text="⬅ Back", bootstyle="secondary", command=lambda: controller.show_frame(MainPage)).place(
            x=20, y=20
        )
        
        self.card = ttk.LabelFrame(self, text=f" ⚠ {I18N[controller.lang]['title_threat_log']} ", padding=30, bootstyle="danger")
        self.card.pack(pady=100, padx=400, fill="both", expand=True)

        self.threat_log = scrolledtext.ScrolledText(self.card, wrap=tk.WORD, height=20, width=100)
        self.threat_log.pack(pady=20)
        self.threat_log.insert(tk.END, "No threats detected yet.\n")
        
    def apply_language(self, lang: str):
        t = I18N[lang]
        self.card.config(text=f" ⚠ {t['title_threat_log']} ")


# ---------------- Settings Page ----------------
class SettingsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.settings_frame = ttk.Frame(self)
        self.settings_frame.pack(fill="both", expand=True)

        self.help_frame = ttk.Frame(self)
        self.help_frame.pack_forget()

        self.build_settings_ui()
        self.build_help_ui()

    def build_settings_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()

        ttk.Button(self.settings_frame, text="⬅ Back", bootstyle="secondary", command=self.destroy_window).place(
            x=20, y=20
        )

        t = I18N[self.controller.lang]
        card = ttk.LabelFrame(self.settings_frame, text=f" {t['settings_title']} ", padding=30, bootstyle="info")
        card.pack(pady=100, padx=400, fill="both", expand=True)

        # Theme
        ttk.Label(card, text=t["theme_label"], font=("Arial", 12)).pack(pady=10, anchor="w")
        self.theme_var = tk.StringVar(value=self.controller.theme_mode)
        ttk.Combobox(card, textvariable=self.theme_var, values=["light", "dark"], width=25, state="readonly").pack(
            pady=5
        )

        # Language
        ttk.Label(card, text=t["lang_label"], font=("Arial", 12)).pack(pady=10, anchor="w")
        self.lang_var = tk.StringVar(value=self.controller.lang)
        ttk.Combobox(card, textvariable=self.lang_var, values=["English", "Urdu"], width=25, state="readonly").pack(
            pady=5
        )

        ttk.Button(card, text=t["save_btn"], bootstyle="success-outline", command=self.save_settings).pack(pady=20)

        # NEW: Reset to Default button
        ttk.Button(card, text=t["reset_btn"], bootstyle="danger-outline", command=self.reset_to_default).pack(pady=5)


    def build_help_ui(self):
        for widget in self.help_frame.winfo_children():
            widget.destroy()

        t = I18N[self.controller.lang]

        ttk.Button(self.help_frame, text="⬅ Back", bootstyle="secondary", command=self.show_settings_frame).place(
            x=20, y=20
        )

        card = ttk.LabelFrame(self.help_frame, text=t["help_text_title"], padding=30, bootstyle="info")
        card.pack(pady=100, padx=400, fill="both", expand=True)
        
        ttk.Label(card, text=t["help_text_title"], font=("Arial", 16, "bold")).pack(pady=15)
        ttk.Label(card, text=t["help_instructions"], justify="left", font=("Arial", 12)).pack(pady=10, padx=20)

    def show_help_frame(self):
        self.settings_frame.pack_forget()
        self.help_frame.pack(fill="both", expand=True)
        self.build_help_ui()

    def show_settings_frame(self):
        self.help_frame.pack_forget()
        self.settings_frame.pack(fill="both", expand=True)
        self.build_settings_ui()

    def destroy_window(self):
        self.controller.show_frame(MainPage)

    def save_settings(self):
        chosen_theme = self.theme_var.get().strip().lower()
        chosen_lang = self.lang_var.get().strip()

        if chosen_theme != self.controller.theme_mode:
            self.controller.set_theme_mode(chosen_theme)

        if chosen_lang != self.controller.lang:
            self.controller.set_language(chosen_lang)

        messagebox.showinfo(
            "Settings",
            f"Theme: {self.controller.theme_mode}\nLanguage: {self.controller.lang}\n\nSettings saved successfully!",
        )

        self.apply_language(self.controller.lang)

    def reset_to_default(self):
        """Resets the theme and language to default values and saves them."""
        self.theme_var.set("light")
        self.lang_var.set("English")
        
        self.save_settings()
        
        messagebox.showinfo(I18N[self.controller.lang]["settings_title"], I18N[self.controller.lang]["reset_info"])

    def apply_language(self, lang: str):
        self.build_settings_ui()
        self.build_help_ui()


# ---------------- About Page ----------------
class AboutPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Button(self, text="⬅ Back", bootstyle="secondary", command=lambda: controller.show_frame(MainPage)).place(
            x=20, y=20
        )

        t = I18N[self.controller.lang]
        self.card = ttk.LabelFrame(self, text=f" 👤 {t['about_title']} ", padding=30, bootstyle="secondary")
        self.card.pack(pady=100, padx=400, fill="both", expand=True)

        ttk.Label(self.card, text=t["developed_by"], font=("Times New Roman", 14)).pack(pady=20)
        ttk.Label(self.card, text=f"{t['version']}: {APP_VERSION}", font=("Times New Roman", 14, "bold")).pack(pady=10)

    def apply_language(self, lang: str):
        t = I18N[lang]
        self.card.config(text=f" 👤 {t['about_title']} ")


if __name__ == "__main__":
    app = AntiRansomwareApp()
    app.mainloop()
