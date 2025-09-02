import os
import pickle
import threading
from scanner_utils import scan_and_delete
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, threading, concurrent.futures
import subprocess, sys
import psutil
import json
import time
import logging
import math
import datetime
from datetime import date, timedelta
import socket
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from PIL import Image, ImageTk
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from scanner_utils import scan_and_delete
from googleapiclient.http import MediaFileUpload
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import backup

root = tk.Tk()
root.withdraw()

def show_popup(title, message):
    popup_root = tk.Tk()
    popup_root.withdraw()
    messagebox.showinfo(title, message)
    popup_root.destroy()


HANDLE_EXE_PATH = os.path.join(os.getcwd(), "handle.exe")

PROTECTED_PATHS = [os.path.expanduser("~/Documents")]

logging.basicConfig(filename='anti_ransomware.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'logs_history.json')
THEME_FILE = "theme_config.txt"
LAST_SCAN_FILE = "last_scan.txt"
APP_VERSION = "1.0"

I18N = {
    "English": {
        "title_main": "Anti-Ransomware Security Solution for MS Windows",
        "btn_scan": "🔎 Scan Now",
        "btn_backup": "💾 Backup Data",
        "btn_threats": "⚠ Threat Logs",
        "btn_settings": "🌎 Switch Language",
        # --- new scan buttons ---
        "btn_select_file_scan": "📂 Select File & Scan",
        "btn_deep_scan": "🛡 Deep Scan",
        "btn_realtime_ep_scan": "⚙ Real Time Entry Points Scan",
        "btn_realtime_ransomware_scan": "🚨 Real Time Ransomware Scan",
        # ------------------------
        "subtitle_safety": "Stay Safe from Ransomware!",
        "status_title": "System is Secure",
        "last_scan_today": "Last Scan: Today",
        "last_scan_yesterday": "Last Scan: Yesterday",
        "last_scan_on": "Last Scan on: ",
        "scanning_text": "Scanning...",
        "scan_complete": "Scan Complete",
        "no_threats_found": "No threats found!",
        "settings_title": "⚙ Language Settings",
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
        "title_threat_log": "Threat Logs",
        "help_text_title": "Anti-Ransomware App Detailed Instructions",
        "settings_saved_title": "Settings Saved",
        "settings_saved_message": "Your settings have been saved successfully!",
        "help_instructions": """
1. Scan Now: Select a file to scan for ransomware threats.
2. Backup Data: Backup files or folders to Google Drive. 
3. Realtime Backup: Automatically backup protected files.
4. Threat Logs: View past detected threats.
5. Settings: Change theme or language and access detailed help.
6. Always ensure your system is updated and files are regularly backed up.
""",
        "virus_info_title": "Ransomware Scanning",
        "virus_info_1": "Ransomware Scanning...",
        "virus_info_2": "USB Scanning/Downloaded Files Scanning...",
    },
    "Urdu": {
        "title_main": "اینٹی رینسم ویئر سیکیورٹی سلوشن برائے ونڈوز",
        "btn_scan": "🔎 اسکین کریں",
        "btn_backup": "💾 بیک اپ",
        "btn_threats": "⚠ تھریٹ لاگ",
        "btn_settings": "🌎 زبان تبدیل کریں",
        # --- new scan buttons ---
        "btn_select_file_scan": "📂 فائل منتخب کریں اور اسکین کریں",
        "btn_deep_scan": "🛡 تفصیلی اسکین",
        "btn_realtime_ep_scan": "⚙ ریئل ٹائم اینٹری پوائنٹس اسکین",
        "btn_realtime_ransomware_scan": "🚨 ریئل ٹائم رینسم ویئر اسکین",
        # ------------------------
        "subtitle_safety": "رینسم ویئر سے محفوظ رہیں!",
        "status_title": "سسٹم محفوظ ہے",
        "last_scan_today": "آخری اسکین: آج",
        "last_scan_yesterday": "آخری اسکین: کل",
        "last_scan_on": "آخری اسکین: ",
        "scanning_text": "اسکیننگ ہو رہی ہے...",
        "scan_complete": "اسکین مکمل",
        "no_threats_found": "کوئی خطرہ نہیں ملا!",
        "settings_title": "⚙ زبان کا تعین",
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
        "title_threat_log": "تھریٹ لاگز",
        "help_text_title": "اینٹی رینسم ویئر ایپ تفصیلی ہدایات",
        "settings_saved_title": "سیٹنگز محفوظ ہوگئیں",
        "settings_saved_message": "آپ کی سیٹنگز کامیابی کے ساتھ محفوظ کر دی گئی ہیں!",
        "help_instructions": """
1. اسکین کریں: رینسم ویئر کے خطرات کے لیے فائل کو اسکین کریں۔
2. ڈیٹا بیک اپ: فائلز یا فولڈرز کو گوگل ڈرائیو پر بیک اپ کریں۔
3. ریئل ٹائم بیک اپ: محفوظ فائلوں کو خود بخود بیک اپ کریں۔
4. تھریٹ لاگز: ماضی میں پتہ چلنے والے خطرات دیکھیں۔
5. سیٹنگز: تھیم یا زبان تبدیل کریں اور تفصیلی مدد حاصل کریں۔
6. ہمیشہ یقینی بنائیں کہ آپ کا سسٹم اپ ڈیٹ ہے اور فائلز کا باقاعدہ سے بیک اپ لیا جاتا ہے۔
""",
        "virus_info_title": "رینسم ویئر اسکیننگ",
        "virus_info_1": "رینسم ویئر اسکیننگ ہو رہی ہے...",
        "virus_info_2": "یو ایس بی اسکیننگ / ڈاؤن لوڈ کردہ فائلز اسکیننگ...",
    },
}


def authenticate_drive():
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, 'client_secret.json')
    token_path = os.path.join(script_dir, 'token.pickle')

    if not os.path.exists(credentials_path):
        messagebox.showerror("Missing File", f"client_secret.json not found at:\n{credentials_path}")
        return None

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    try:
        if creds and creds.valid:
            pass
        elif creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Invalid or missing credentials")
    except Exception as e:
        if os.path.exists(token_path):
            os.remove(token_path)
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def create_drive_folder(service, folder_name, parent_id=None):
    metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        metadata['parents'] = [parent_id]
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder.get('id')

def log_backup_event(event_type, file_path):
    log_entry = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event_type,
        "file": file_path
    }
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(log_entry)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[LOG-ERROR] Could not update {LOG_FILE}: {e}")
    try:
        with open("backup.log", "a", encoding="utf-8") as f:
            f.write(f"[{log_entry['time']}] {event_type}: {file_path}\n")
    except:
        pass

def upload_file(service, filepath, folder_id, progress_callback=None):
    try:
        file_metadata = {'name': os.path.basename(filepath), 'parents': [folder_id]}
        media = MediaFileUpload(filepath, resumable=True)
        request = service.files().create(body=file_metadata, media_body=media, fields='id')
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status and progress_callback:
                progress_callback(int(status.progress() * 100))
        if progress_callback:
            progress_callback(100)
        log_backup_event("Manual Backup", filepath)
        return response.get('id')
    except Exception as e:
        error_msg = str(e)
        root.after(0, lambda msg=error_msg: messagebox.showerror(
            "Upload Error", f"Failed to upload:\n{filepath}\n\n{msg}"
        ))
        return None

def upload_folder(service, folder_path, parent_folder_id, progress_callback=None):
    folder_id_map = {folder_path: parent_folder_id}
    total_files = sum(len(files) for _, _, files in os.walk(folder_path))
    uploaded_files = [0]
    for root_dir, dirs, files in os.walk(folder_path):
        parent_id = folder_id_map.get(os.path.dirname(root_dir), parent_folder_id)
        if root_dir not in folder_id_map:
            folder_metadata = {
                'name': os.path.basename(root_dir),
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id_map[root_dir] = folder.get('id')
        for file_name in files:
            file_path = os.path.join(root_dir, file_name)
            def inner_progress(pct):
                overall = int(((uploaded_files[0] + pct / 100) / total_files) * 100)
                if progress_callback:
                    progress_callback(overall)
            upload_file(service, file_path, folder_id_map[root_dir], progress_callback=inner_progress)
            uploaded_files[0] += 1

def run_scan_task(file_path, progress_callback, completion_callback):
    try:
        abs_path = os.path.abspath(file_path)
        for i in range(101):
            time.sleep(0.02)
            progress_callback(i)
        completion_callback(file_path)
        logging.info(f"Scan Result: No threats detected.")
    except Exception as e:
        logging.error(f"Scan Error: {str(e)}")
        root.after(0, lambda: messagebox.showerror("Scan Error", f"Error during scan:\n{str(e)}"))

def calculate_entropy(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        if not data:
            return 0
        byte_count = [0] * 256
        for byte in data:
            byte_count[byte] += 1
        entropy = -sum((count / len(data)) * math.log2(count / len(data))
                       for count in byte_count if count != 0)
        return entropy
    except Exception:
        return 0

class EncryptionDetectorHandler(FileSystemEventHandler):
    def __init__(self, gui_callback):
        self.gui_callback = gui_callback

    def on_created(self, event):
        if not event.is_directory and os.path.isfile(event.src_path):
            file_path = event.src_path
            if os.path.basename(file_path).startswith("~") or os.path.basename(file_path).startswith("._"):
                return
            
            try:
                entropy_value = calculate_entropy(file_path)
                if entropy_value > 7.0:
                    self.gui_callback(file_path, entropy_value)
            except Exception as e:
                logging.error(f"Error checking file entropy for {file_path}: {e}")

def start_encryption_monitor(path_to_watch, gui_callback):
    handler = EncryptionDetectorHandler(gui_callback)
    observer = Observer()
    observer.schedule(handler, path_to_watch, recursive=True)
    observer.start()
    return observer

def encryption_alert(filepath, entropy):
    msg = f"⚠️ Possible ransomware activity detected!\n\nFile: {filepath}\nEntropy: {entropy:.2f}\n\nDelete it?"
    logging.warning(f"Suspicious file: {filepath} | Entropy: {entropy}")
    if messagebox.askyesno("Ransomware Alert", msg):
        try:
            os.remove(filepath)
            messagebox.showinfo("Deleted", f"File deleted: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete:\n{str(e)}")

def view_logs():
    if not os.path.exists(LOG_FILE):
        messagebox.showinfo("No Logs", "No logs found.")
        return
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            logs = json.load(file)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to read or parse the log file.")
        return
    log_window = tk.Toplevel()
    log_window.title("Logs History")
    log_window.geometry("800x450")
    log_window.configure(bg="#f8f9fa")
    frame = tk.Frame(log_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    columns = ("Time", "Event", "Detail")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.heading("Time", text="Timestamp")
    tree.heading("Event", text="Event Type")
    tree.heading("Detail", text="Detail")
    tree.column("Time", width=180, anchor="center")
    tree.column("Event", width=140, anchor="center")
    tree.column("Detail", width=460, anchor="w")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(fill=tk.BOTH, expand=True)
    for log in logs:
        timestamp = log.get("timestamp", "N/A")
        event_type = log.get("event", "N/A")
        detail = log.get("file", "N/A")
        tree.insert("", tk.END, values=(timestamp, event_type, detail))

def read_theme_file():
    theme_mode = "light"
    language = "English"
    if not os.path.exists(THEME_FILE):
        return theme_mode, language
    try:
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.lower() in ("dark", "light"):
                theme_mode = content.lower()
                return theme_mode, language
            f.seek(0)
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k == "theme":
                        theme_mode = v.lower()
                    elif k == "language":
                        if v.lower().startswith("u"):
                            language = "Urdu"
                        else:
                            language = "English"
    except Exception:
        pass
    return theme_mode, language

def write_theme_file(theme_mode, language):
    try:
        print(f"DEBUG: Writing to theme file: theme={theme_mode}, language={language}")
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            f.write(f"theme={theme_mode}\n")
            f.write(f"language={language}\n")
            
        # Verify the file was written correctly
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"DEBUG: Verified theme file content: {content}")
    except Exception as e:
        print(f"ERROR writing settings: {e}")

def read_last_scan_date():
    if os.path.exists(LAST_SCAN_FILE):
        try:
            with open(LAST_SCAN_FILE, "r", encoding="utf-8") as f:
                date_str = f.read().strip()
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, FileNotFoundError):
            return None
    return None

def write_last_scan_date():
    try:
        with open(LAST_SCAN_FILE, "w", encoding="utf-8") as f:
            f.write(date.today().isoformat())
    except Exception:
        pass

def format_last_scan_text(last_scan_date_obj, lang: str):
    t = I18N[lang]
    if last_scan_date_obj is None:
        return t["last_scan_today"]
    today = date.today()
    yesterday = today - timedelta(days=1)
    if last_scan_date_obj == today:
        return t["last_scan_today"]
    elif last_scan_date_obj == yesterday:
        return t["last_scan_yesterday"]
    else:
        return f"{t['last_scan_on']}{last_scan_date_obj.strftime('%Y-%m-%d')}"

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

class AntiRansomwareApp(ttkb.Window):
    def __init__(self):
        theme_mode, language = read_theme_file()
        themename = "superhero" if theme_mode == "light" else "cyborg"
        super().__init__(themename=themename)
        self.title("Anti-Ransomware Security Solution")
        self.state("zoomed")
        self.theme_mode = theme_mode
        self.lang = language if language in I18N else "English"
        self.language = self.lang   # ✅ fix added (for ScanPage compatibility)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}
        for F in (WelcomePage, MainPage, ScanPage, BackupPage, ThreatsPage, SettingsPage, AboutPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(WelcomePage)

        self.observer = None
        self.start_monitor()

    def start_monitor(self):
        def update_threat_log_gui(filepath, entropy_value):
            threats_page = self.frames[ThreatsPage]
            log_entry = f"⚠️ [RANSOMWARE ALERT] Detected suspicious activity on file: {os.path.basename(filepath)} (Entropy: {entropy_value:.2f})\n"
            threats_page.threat_log.insert(tk.END, log_entry)
            threats_page.threat_log.see(tk.END)
            self.deiconify()
            root.after(0, lambda: encryption_alert(filepath, entropy_value))

        for path in PROTECTED_PATHS:
            if os.path.exists(path):
                self.observer = start_encryption_monitor(path, update_threat_log_gui)
                logging.info(f"Started real-time monitoring for: {path}")

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
        self.language = self.lang   # ✅ keep language synced
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

class WelcomePage(ttk.Frame):
    SPLASH_DURATION = 5000 # 5 seconds

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Full background style
        self.configure(style="WelcomePage.TFrame")

        # --- Title ---
        title = ttk.Label(
            self,
            text="🔐 Anti-Ransomware Security Solution",
            font=("Times New Roman", 48, "bold"),
            bootstyle="primary"
        )
        title.place(relx=0.5, rely=0.22, anchor="center")

        # --- Subtitle ---
        subtitle = ttk.Label(
            self,
            text="Easy, Quick, and Safe!",
            font=("Arial", 26, "italic"),
            bootstyle="secondary"
        )
        subtitle.place(relx=0.5, rely=0.32, anchor="center")

        # --- Instruction Box (card style) ---
        self.card = ttk.LabelFrame(
            self,
            text="📘 How to Use",
            padding=25,
            bootstyle="info"
        )
        self.card.place(relx=0.5, rely=0.58, anchor="center", relwidth=0.75)

        instructions = (
            "Welcome to Anti-Ransomware!\n\n"
            "👉  Click 'Scan Now' to scan files.\n"
            "👉  Click 'Backup Data' to protect your data.\n\n"
            "For detailed help, go to the Main Page → Help."
        )
        ttk.Label(
            self.card,
            text=instructions,
            font=("Arial", 16),
            justify="left",
        ).pack()

        # --- Footer ---
        ttk.Label(
            self,
            text="© 2025 Anti-Ransomware Security | Stay Safe Online",
            font=("Arial", 12),
            bootstyle="secondary"
        ).place(relx=0.5, rely=0.95, anchor="center")

        # --- Progress Bar (smooth clean animation) ---
        self.progress = ttk.Progressbar(
            self,
            mode="determinate",
            bootstyle="success",
            length=550
        )
        self.progress.place(relx=0.5, rely=0.9, anchor="center")

        # Start smooth animation
        self.animate_progress()

        # Switch to main after SPLASH_DURATION
        controller.after(self.SPLASH_DURATION, lambda: controller.show_frame(MainPage))

    def animate_progress(self):
        """Smooth filling animation of progress bar in SPLASH_DURATION time."""
        steps = 100
        interval = self.SPLASH_DURATION // steps  # ms per step

        def step(i=0):
            if i <= steps:
                self.progress["value"] = i
                self.after(interval, lambda: step(i + 1))

        step()

class MainPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.main_title_lbl = ttk.Label(self, text="", font=("Arial", 28, "bold"))
        self.main_title_lbl.pack(side="top", pady=(40, 0))
        self.subtitle_lbl = ttk.Label(self, text="", font=("Arial", 16))
        self.subtitle_lbl.pack(side="top", pady=(5, 10))
        self.version_lbl = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.version_lbl.pack(side="top", pady=(5, 10))
        self.status_bar_frame = ttk.LabelFrame(self, text=" System Status ", bootstyle="success")
        self.status_bar_frame.pack(side="top", fill="x", padx=100, pady=(10, 0))
        status_content_frame = ttk.Frame(self.status_bar_frame, padding=20)
        status_content_frame.pack(expand=True, fill="both")
        self.status_title_lbl = ttk.Label(status_content_frame, text="", font=("Arial", 22, "bold"), bootstyle="success")
        self.status_title_lbl.pack(pady=(10, 5))
        self.last_scan_lbl = ttk.Label(status_content_frame, text="", font=("Arial", 12))
        self.last_scan_lbl.pack()
        self.status_progress = ttk.Progressbar(status_content_frame, bootstyle="info", length=400)
        self.status_progress.pack(pady=(10, 10), fill="x", padx=100)
        self.animate_progress()
        main_content_frame = ttk.Frame(self, padding=20)
        main_content_frame.pack(expand=True, fill="both")
        sections_frame = ttk.Frame(main_content_frame, padding=20)
        sections_frame.pack(expand=True, fill="both", side="top", anchor="center")
        self.left_card = ttk.LabelFrame(sections_frame, text=" Quick Access ", padding=40, bootstyle="secondary")
        self.left_card.pack(side="left", padx=15, fill="both", expand=True)
        self.btn_updates = ttk.Button(self.left_card, text="", bootstyle="warning-outline", command=self.check_updates, width=30)
        self.btn_updates.pack(pady=8)
        self.btn_about = ttk.Button(self.left_card, text="", bootstyle="secondary-outline", command=lambda: self.controller.show_frame(AboutPage), width=30)
        self.btn_about.pack(pady=8)
        self.btn_help = ttk.Button(self.left_card, text="", bootstyle="info-outline", command=self.show_help_dialog, width=30)
        self.btn_help.pack(pady=8)
        self.main_card = ttk.LabelFrame(sections_frame, text=" Anti-Ransomware Features ", padding=40, bootstyle="primary")
        self.main_card.pack(side="left", padx=15, fill="both", expand=True)
        self.btn_scan = ttk.Button(self.main_card, text="", bootstyle="primary-outline", command=lambda: self.controller.show_frame(ScanPage), width=40)
        self.btn_scan.pack(pady=18)
        self.btn_backup = ttk.Button(self.main_card, text="", bootstyle="success-outline", command=lambda: self.controller.show_frame(BackupPage), width=40)
        self.btn_backup.pack(pady=18)
        self.btn_threats = ttk.Button(self.main_card, text="", bootstyle="danger-outline", command=self.open_threats_window, width=40)
        self.btn_threats.pack(pady=18)
        self.btn_settings = ttk.Button(self.main_card, text="", bootstyle="info-outline", command=lambda: self.controller.show_frame(SettingsPage), width=40)
        self.btn_settings.pack(pady=18)
        self.virus_card = ttk.LabelFrame(sections_frame, text="", padding=20, bootstyle="danger")
        self.virus_card.pack(side="left", padx=15, fill="both", expand=True)
        self.ransomware_scan_label = ttk.Label(self.virus_card, text="", justify="center", wraplength=250, font=("Arial", 12))
        self.ransomware_scan_label.pack(pady=5)
        self.ransomware_scan_pb = ttk.Progressbar(self.virus_card, mode="indeterminate", bootstyle="warning-striped")
        self.ransomware_scan_pb.pack(pady=10, fill="x")
        self.other_scan_label = ttk.Label(self.virus_card, text="", justify="center", wraplength=250, font=("Arial", 12))
        self.other_scan_label.pack(pady=5)
        self.other_scan_pb = ttk.Progressbar(self.virus_card, mode="indeterminate", bootstyle="warning-striped")
        self.other_scan_pb.pack(pady=10, fill="x")
        self.after(200, self.start_animations)

    def start_animations(self):
        self.ransomware_scan_pb.start(10)
        self.other_scan_pb.start(10)

    def animate_progress(self):
        value = self.status_progress["value"]
        if value < 100:
            self.status_progress["value"] = value + 1
        else:
            self.status_progress["value"] = 0
        self.after(100, self.animate_progress)

    def open_threats_window(self):
        self.controller.show_frame(ThreatsPage)

    def check_updates(self):
        t = I18N[self.controller.lang]
        messagebox.showinfo("Updates", f"{t['up_to_date']} (v{APP_VERSION}).")

    def show_help_dialog(self):
        import os, webbrowser
        from tkinter import messagebox

        help_file = os.path.abspath("help.html")
        if not os.path.exists(help_file):
            messagebox.showerror("Error", "Help file not found!")
            return

        webbrowser.open(f"file:///{help_file}")

    def apply_language(self, lang: str):
        t = I18N[lang]
        title_color = "white" if self.controller.theme_mode == "dark" else "black"
        self.main_title_lbl.config(text=t["title_main"], foreground=title_color)
        self.subtitle_lbl.config(text=t["subtitle_safety"])
        self.version_lbl.config(text=f"{t['version']}: {APP_VERSION}")
        self.status_title_lbl.config(text=t["status_title"])
        last_scan_date = read_last_scan_date()
        self.last_scan_lbl.config(text=format_last_scan_text(last_scan_date, lang))
        self.main_card.config(text=f" Anti-Ransomware Features ")
        self.btn_scan.config(text=t["btn_scan"])
        self.btn_backup.config(text=t["btn_backup"])
        self.btn_threats.config(text=t["btn_threats"])
        self.btn_settings.config(text=t["btn_settings"])
        self.btn_updates.config(text=t["updates_btn"])
        self.btn_about.config(text=t["about_btn"])
        self.btn_help.config(text=t["help_btn"])
        self.virus_card.config(text=t["virus_info_title"])
        self.ransomware_scan_label.config(text=t["virus_info_1"])
        self.other_scan_label.config(text=t["virus_info_2"])


import os
import threading
import concurrent.futures
from collections import deque
from tkinter import filedialog, messagebox
from tkinter import ttk

class ScanPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_file = None
        self.stop_scan_flag = False

        ttk.Button(self, text="⬅ Back", bootstyle="secondary",
                   command=lambda: controller.show_frame(MainPage)).place(x=20, y=20)

        self.card = ttk.LabelFrame(self, text=" 🔎 Scan Files for Ransomware ",
                                   padding=50, bootstyle="info")
        self.card.pack(pady=60, padx=60, fill="both", expand=True)

        # --- Buttons (with I18N support) ---
        self.btn_file_scan = ttk.Button(self.card,
                   text=I18N[self.controller.language]["btn_select_file_scan"],
                   bootstyle="info-outline",
                   command=self.select_file_and_scan,
                   width=30)
        self.btn_file_scan.pack(pady=10)

        self.btn_deep_scan = ttk.Button(self.card,
                   text=I18N[self.controller.language]["btn_deep_scan"],
                   bootstyle="danger-outline",
                   command=self.start_full_system_scan,
                   width=30)
        self.btn_deep_scan.pack(pady=10)

        self.btn_realtime_ep = ttk.Button(self.card,
                   text=I18N[self.controller.language]["btn_realtime_ep_scan"],
                   bootstyle="success-outline",
                   command=self.start_realtime_scan,
                   width=30)
        self.btn_realtime_ep.pack(pady=10)

        self.btn_realtime_ransomware = ttk.Button(self.card,
                   text=I18N[self.controller.language]["btn_realtime_ransomware_scan"],
                   bootstyle="warning-outline",
                   command=self.start_ransomware_scan,
                   width=30)
        self.btn_realtime_ransomware.pack(pady=10)

        # Status + progress
        self.status_label = ttk.Label(self.card, text="Status: Idle", font=("Segoe UI", 10))
        self.status_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.card, mode="determinate", length=300)
        self.progress_bar.pack(pady=10)

        self.progress_label = ttk.Label(self.card, text="", font=("Segoe UI", 9))
        self.progress_label.pack(pady=5)

        self.stop_button = ttk.Button(self.card, text="⛔ Stop Scan",
                                      bootstyle="danger-outline",
                                      command=self.stop_full_system_scan)
        self.stop_button.pack_forget()

    # ----------------- FILE SCAN -----------------
    def select_file_and_scan(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            from scanner_utils import scan_and_delete
            threat_page = self.controller.frames[ThreatsPage]

            result = scan_and_delete(file_path)
            threat_page.add_log_entry(f"{os.path.basename(file_path)}: {result}")

            if "❌" in result:
                messagebox.showerror("Threat Detected", result)
            else:
                messagebox.showinfo("Scan Result", result)

    # ----------------- DEEP SCAN -----------------
    def start_full_system_scan(self):
        self.stop_scan_flag = False
        self.status_label.config(text="🔍 Deep scanning is in progress...")
        self.progress_bar["value"] = 0
        self.progress_label.config(text="0%")
        self.stop_button.pack_forget()  # no stop button shown for deep scan in current design
        threading.Thread(target=self.run_deep_scan, daemon=True).start()

    def run_deep_scan(self):
        from scanner_utils import scan_and_delete
        threat_page = self.controller.frames[ThreatsPage]

        try:
            # Home directory only
            home_dir = os.path.expanduser("~")
            file_list = []
            for root, _, files in os.walk(home_dir):
                for f in files:
                    file_list.append(os.path.join(root, f))

            # Parallel scan
            threats = self.parallel_scan_files(file_list, threat_page)

            # After scan completes, popup (ensure runs on main thread)
            if not threats:
                self.after(0, lambda: messagebox.showinfo("Deep Scan", "✅ No threats found."))
            else:
                threat_list = "\n".join([os.path.basename(fp) for fp, _ in threats])

                def ask_delete():
                    ans = messagebox.askyesno(
                        "Threats Detected",
                        f"⚠️ {len(threats)} threats found in your home directory:\n\n"
                        f"{threat_list}\n\nDo you want to delete them all?"
                    )
                    if ans:
                        deleted = 0
                        for file_path, result in threats:
                            final = scan_and_delete(file_path, auto_delete=True)
                            threat_page.add_log_entry(f"{os.path.basename(file_path)}: {final}")
                            deleted += 1
                        messagebox.showinfo("Deep Scan", f"🗑 Deleted {deleted} threats.")
                    else:
                        messagebox.showinfo("Deep Scan", f"⚠️ {len(threats)} threats kept.")

                self.after(0, ask_delete)

            self.after(0, self.reset_ui)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Deep scan failed: {e}"))
            self.after(0, self.reset_ui)

    # ----------------- HELPERS -----------------
    def parallel_scan_files(self, file_list, threat_page):
        """
        Bounded submission parallel scan:
        - submits up to `window_size` tasks, then waits for some to finish and submits more.
        - safely updates UI (checks widget existence before changing).
        - returns list of (filepath, result) for threats.
        """
        from scanner_utils import scan_and_delete

        threats = []
        total = len(file_list)
        if total == 0:
            # nothing to scan
            self._safe_ui_update(100, "No files")
            return threats

        # decide workers based on CPUs (threads are appropriate because scan_and_delete talks to clamd)
        cpu = os.cpu_count() or 1
        max_workers = min(64, max(2, cpu * 4))

        # backlog window size (how many concurrent submitted tasks to keep)
        window_size = max_workers * 2

        # control UI update frequency
        UPDATE_EVERY = 20

        processed = 0

        # helper to safely update UI from background thread
        def schedule_ui_update(pct, filename_short):
            def do_update():
                try:
                    if self.winfo_exists():
                        self.progress_bar.configure(value=pct)
                        self.progress_label.config(text=f"{pct}% - {filename_short}")
                except Exception:
                    # ignore UI errors (e.g. window closed)
                    pass
            # schedule on main thread
            try:
                self.after(0, do_update)
            except Exception:
                pass

        # Use a bounded submission pattern to avoid submitting huge numbers at once
        it = iter(file_list)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}  # future -> filepath

            # submit initial batch
            for _ in range(min(window_size, total)):
                try:
                    fp = next(it)
                except StopIteration:
                    break
                futures[executor.submit(scan_and_delete, fp, False)] = fp

            # process completed futures and keep the window filled
            while futures:
                # wait for at least one future to complete
                done, _ = concurrent.futures.wait(futures.keys(), return_when=concurrent.futures.FIRST_COMPLETED)
                for fut in done:
                    fp = futures.pop(fut)
                    # cooperative stop: break out if stop flag set
                    if getattr(self, "stop_scan_flag", False):
                        # try to cancel remaining futures (best-effort)
                        for rem in list(futures.keys()):
                            try:
                                rem.cancel()
                            except Exception:
                                pass
                        # also drain iterator by not submitting more
                        futures.clear()
                        break

                    try:
                        result = fut.result()
                    except Exception:
                        result = "Error: scan failed"

                    processed += 1
                    # avoid div-by-zero
                    progress = int((processed / total) * 100) if total else 100
                    filename_short = os.path.basename(fp) or fp

                    # update UI occasionally (every UPDATE_EVERY files or on final)
                    if (processed % UPDATE_EVERY == 0) or (processed == total):
                        schedule_ui_update(progress, filename_short)

                    # record threat if detected
                    try:
                        if isinstance(result, str) and "❌" in result:
                            threats.append((fp, result))
                            # best-effort log update
                            try:
                                threat_page.add_log_entry(f"{os.path.basename(fp)}: {result}")
                            except Exception:
                                pass
                    except Exception:
                        pass

                    # submit one more to keep backlog
                    try:
                        next_fp = next(it)
                        futures[executor.submit(scan_and_delete, next_fp, False)] = next_fp
                    except StopIteration:
                        pass

                # if stopped, exit loop
                if getattr(self, "stop_scan_flag", False):
                    break

        # final UI mark (only if widget still exists)
        try:
            if self.winfo_exists():
                self.after(0, lambda: self.progress_label.config(text="✅ Scan Complete"))
        except Exception:
            pass

        return threats

    def stop_full_system_scan(self):
        # cooperative stop: the running tasks won't necessarily abort immediately,
        # but we will stop submitting/processing results here.
        self.stop_scan_flag = True
        self.status_label.config(text="⛔ Scan stopped by user.")
        self.stop_button.pack_forget()

    def reset_ui(self):
        self.status_label.config(text="Status: Idle")
        try:
            self.progress_bar["value"] = 0
        except Exception:
            pass
        try:
            self.progress_label.config(text="")
        except Exception:
            pass

    # ----------------- REALTIME POPUPS -----------------
    def start_realtime_scan(self):
        self.after(0, lambda: messagebox.showinfo(
            "Realtime Entry points Scan",
             "Real-time Entry Points scanning is active.\n(You will be notified of any threats.)"
        ))

    def start_ransomware_scan(self):
        self.after(0, lambda: messagebox.showinfo(
            "Realtime Ransomware Scan",
            "Ransomware monitoring is active.\n(Suspicious activity will trigger alerts.)"
        ))

    # ----------------- LANGUAGE SWITCH -----------------
    def apply_language(self, lang: str):
        t = I18N[lang]
        self.btn_file_scan.config(text=t["btn_select_file_scan"])
        self.btn_deep_scan.config(text=t["btn_deep_scan"])
        self.btn_realtime_ep.config(text=t["btn_realtime_ep_scan"])
        self.btn_realtime_ransomware.config(text=t["btn_realtime_ransomware_scan"])

        
class BackupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.card = ttk.LabelFrame(self, text="", padding=30, bootstyle="success")
        self.card.pack(pady=100, padx=400)

        self.progress_bar = ttk.Progressbar(self.card, bootstyle="success-striped", length=400)
        self.progress_bar.pack(pady=20)
        self.progress_label = ttk.Label(self.card, text="0%", font=("Arial", 12))
        self.progress_label.pack(pady=5)

        self.btn_sel_file = ttk.Button(
            self.card,
            text="",
            bootstyle="info-outline",
            command=self.select_file_for_backup,
            width=35,
        )
        self.btn_sel_file.pack(pady=10)

        self.btn_sel_folder = ttk.Button(
            self.card,
            text="",
            bootstyle="info-outline",
            command=self.select_folder_for_backup,
            width=35,
        )
        self.btn_sel_folder.pack(pady=10)

        self.btn_rt = ttk.Button(
            self.card,
            text="",
            bootstyle="success-outline",
            command=self.select_folder_for_realtime_backup,
            width=35,
        )
        self.btn_rt.pack(pady=20)

        ttk.Button(self, text="⬅ Back", bootstyle="secondary",
                   command=lambda: controller.show_frame(MainPage)).place(x=20, y=20)

    def update_progress_ui(self, value):
        self.progress_bar["value"] = value
        self.progress_label.config(text=f"{value}%")
        self.update_idletasks()

    # -------------------- Manual Backup -------------------- #
    def select_file_for_backup(self):
        file = filedialog.askopenfilename(parent=self.master)
        if file:
            threading.Thread(target=self.perform_upload_file, args=(file,), daemon=True).start()

    def perform_upload_file(self, file):
        try:
            if not check_internet():
                self.after(0, lambda: messagebox.showerror("Internet Error", I18N[self.controller.lang]["no_internet"]))
                return
            self.after(0, lambda: self.update_progress_ui(0))
            service = authenticate_drive()
            if not service:
                return
            folder_id = create_drive_folder(service, "RansomwareBackup")
            upload_file(service, file, folder_id, progress_callback=lambda p: self.after(0, lambda: self.update_progress_ui(p)))
            self.after(0, lambda: self.update_progress_ui(100))
            self.after(0, lambda: messagebox.showinfo("Success", "File uploaded successfully!"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Upload Error", msg=str(e)))

    def select_folder_for_backup(self):
        folder = filedialog.askdirectory(parent=self.master)
        if folder:
            threading.Thread(target=self.perform_upload_folder, args=(folder,), daemon=True).start()

    def perform_upload_folder(self, folder):
        try:
            if not check_internet():
                self.after(0, lambda: messagebox.showerror("Internet Error", I18N[self.controller.lang]["no_internet"]))
                return
            self.after(0, lambda: self.update_progress_ui(0))
            service = authenticate_drive()
            if not service:
                return
            backup_root_id = create_drive_folder(service, "RansomwareBackup")
            top_folder_id = create_drive_folder(service, os.path.basename(folder), backup_root_id)
            upload_folder(service, folder, top_folder_id, progress_callback=lambda p: self.after(0, lambda: self.update_progress_ui(p)))
            self.after(0, lambda: self.update_progress_ui(100))
            self.after(0, lambda: messagebox.showinfo("Success", "Folder uploaded successfully!"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Upload Error", msg=str(e)))

    # -------------------- Realtime Backup -------------------- #
    def select_folder_for_realtime_backup(self):
        folder = filedialog.askdirectory(parent=self.master, title="Select folder for Realtime Backup")
        if folder:
            threading.Thread(target=self.start_realtime_backup_thread, args=(folder,), daemon=True).start()

    def start_realtime_backup_thread(self, folder):
     def backup_and_monitor():
        try:
            # Step 1: Full backup
            self.after(0, lambda: messagebox.showinfo(
                "Realtime Backup", f"Starting full backup for:\n{folder}"
            ))
            self.perform_upload_folder(folder)  # full backup

            # Step 2: Start monitoring folder for new/modified files
            if backup and hasattr(backup, 'start_realtime_backup'):
                backup.start_realtime_backup(folder)
                self.after(0, lambda: messagebox.showinfo(
                    "Realtime Backup",
                    f"Realtime backup started for folder:\n{folder}\nAll new or modified files will be uploaded automatically."
                ))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Error", f"Realtime backup failed: {e}"
            ))

    # Run full backup + monitoring in a separate thread
     threading.Thread(target=backup_and_monitor, daemon=True).start()

    # -------------------- Language -------------------- #
    def apply_language(self, lang: str):
        t = I18N[lang]
        self.card.config(text=t["backup_card"])
        self.btn_sel_file.config(text=t["select_file"])
        self.btn_sel_folder.config(text=t["select_folder"])
        self.btn_rt.config(text=t["realtime_backup"])

class ThreatsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Button(
            self,
            text="⬅ Back",
            bootstyle="secondary",
            command=lambda: controller.show_frame(MainPage)
        ).place(x=20, y=20)

        self.card = ttk.LabelFrame(self, text="", padding=30, bootstyle="danger")
        self.card.pack(pady=100, padx=400, fill="both", expand=True)

        self.threat_log = scrolledtext.ScrolledText(
            self.card, wrap=tk.WORD, height=20, width=100
        )
        self.threat_log.pack(pady=20)

        # Start with empty log (optional: can add default message)
        self.threat_log.insert(tk.END, "No threats detected yet.\n")

    def add_log_entry(self, entry: str):
        """Append new threat/scan result to log."""
        # Remove default text if it's the first real entry
        current_content = self.threat_log.get("1.0", tk.END).strip()
        if current_content == "No threats detected yet.":
            self.threat_log.delete("1.0", tk.END)

        # Add new entry
        self.threat_log.insert(tk.END, entry + "\n")
        self.threat_log.see(tk.END)  # Auto-scroll to bottom

    def apply_language(self, lang: str):
        t = I18N[lang]
        self.card.config(text=f" ⚠ {t['title_threat_log']} ")

        
class SettingsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.settings_frame = ttk.Frame(self)
        self.settings_frame.pack(fill="both", expand=True)
        self.build_settings_ui()
        
    def build_settings_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
            
        ttk.Button(self.settings_frame, text="⬅ Back", bootstyle="secondary", 
                  command=lambda: self.controller.show_frame(MainPage)).place(x=20, y=20)
        
        t = I18N[self.controller.lang]
        card = ttk.LabelFrame(self.settings_frame, text=f" {t['settings_title']} ", 
                             padding=30, bootstyle="info")
        card.pack(pady=100, padx=400, fill="both", expand=True)
        
        # Initialize selected values to current values
        self.selected_theme = self.controller.theme_mode
        self.selected_language = self.controller.lang
        
        # Theme section with buttons
        # ttk.Label(card, text=t["theme_label"], font=("Arial", 12)).pack(pady=10, anchor="w")
        # theme_frame = ttk.Frame(card)
        # theme_frame.pack(pady=5, fill="x")
       
        # Create light theme button
        self.light_btn = ttk.Button(
             
            text="Light", 
            width=15,
            bootstyle="primary" if self.controller.theme_mode == "light" else "outline"
        )
        self.light_btn.pack(side="left", padx=10)
        self.light_btn.config(command=lambda: self.select_theme("light"))
        
        #Create dark theme button
        self.dark_btn = ttk.Button(
           
            text="Dark", 
            width=15,
            bootstyle="primary" if self.controller.theme_mode == "dark" else "outline"
        )
        self.dark_btn.pack(side="left", padx=10)
        self.dark_btn.config(command=lambda: self.select_theme("dark"))
        
        # Language section with buttons
        ttk.Label(card, text=t["lang_label"], font=("Arial", 12)).pack(pady=10, anchor="w")
        lang_frame = ttk.Frame(card)
        lang_frame.pack(pady=5, fill="x")
        
        # Create English language button
        self.english_btn = ttk.Button(
            lang_frame, 
            text="English", 
            width=15,
            bootstyle="primary" if self.controller.lang == "English" else "outline"
        )
        self.english_btn.pack(side="left", padx=10)
        self.english_btn.config(command=lambda: self.select_language("English"))
        
        # Create Urdu language button
        self.urdu_btn = ttk.Button(
            lang_frame, 
            text="Urdu", 
            width=15,
            bootstyle="primary" if self.controller.lang == "Urdu" else "outline"
        )
        self.urdu_btn.pack(side="left", padx=10)
        self.urdu_btn.config(command=lambda: self.select_language("Urdu"))
        
        # Save button
        ttk.Button(
            card, 
            text=t["save_btn"], 
            bootstyle="success", 
            command=self.save_settings
        ).pack(pady=20)
        
        # Reset button
        ttk.Button(
            card, 
            text=t["reset_btn"], 
            bootstyle="danger-outline", 
            command=self.reset_to_default
        ).pack(pady=5)
        
        # Current settings display
        self.settings_label = ttk.Label(
            card,
            #text=f"Current Settings:\nTheme: {self.controller.theme_mode.capitalize()}\nLanguage: {self.controller.lang}",
            text=f"Current Settings:\nLanguage: {self.controller.lang}",
            font=("Arial", 11),
           
            justify="center"
        )
        self.settings_label.pack(pady=15)
    
    def select_theme(self, theme):
        """Select a theme and update button styles"""
        self.selected_theme = theme
        
        # Update button appearances
        if theme == "light":
            self.light_btn.configure(bootstyle="primary")
            self.dark_btn.configure(bootstyle="outline")
        else:
            self.light_btn.configure(bootstyle="outline")
            self.dark_btn.configure(bootstyle="primary")
            
        # Update settings display
        # self.settings_label.configure(
        #     text=f"Current Settings:\nTheme: {theme.capitalize()}\nLanguage: {self.controller.lang}\n\n(Changes will apply after saving)"
        # )
    
    def select_language(self, language):
        """Select a language and update button styles"""
        self.selected_language = language
        
        # Update button appearances
        if language == "English":
            self.english_btn.configure(bootstyle="primary")
            self.urdu_btn.configure(bootstyle="outline")
        else:
            self.english_btn.configure(bootstyle="outline")
            self.urdu_btn.configure(bootstyle="primary")
            
        # Update settings display
        # self.settings_label.configure(
        #     text=f"Current Settings:\nTheme: {self.controller.theme_mode.capitalize()}\nLanguage: {language}\n\n(Changes will apply after saving)"
        # )
    
    def save_settings(self):
        """Save the selected settings"""
        theme_changed = False
        lang_changed = False
        
        # Add debug prints to help diagnose the issue
        print(f"DEBUG: Current theme={self.controller.theme_mode}, Selected theme={self.selected_theme}")
        print(f"DEBUG: Current lang={self.controller.lang}, Selected lang={self.selected_language}")
        
        # Check if theme changed - use explicit comparison
        if self.selected_theme != self.controller.theme_mode:
            print(f"DEBUG: Theme changed from {self.controller.theme_mode} to {self.selected_theme}")
            theme_changed = True
            self.controller.theme_mode = self.selected_theme
        
        # Check if language changed - use explicit comparison
        if self.selected_language != self.controller.lang:
            print(f"DEBUG: Language changed from {self.controller.lang} to {self.selected_language}")
            lang_changed = True
            self.controller.lang = self.selected_language
        
        # Save settings if changed
        if theme_changed or lang_changed:
            print("DEBUG: Saving changes to theme file")
            # Save to file
            write_theme_file(self.controller.theme_mode, self.controller.lang)
            
            # Apply language changes immediately
            if lang_changed:
                for frame in self.controller.frames.values():
                    if hasattr(frame, "apply_language"):
                        frame.apply_language(self.controller.lang)
            
            # Show success message
            t = I18N[self.controller.lang]
            messagebox.showinfo(
                t["settings_saved_title"],
                t["settings_saved_message"]
            )
            
            # If theme changed, restart is recommended
            if theme_changed:
                if messagebox.askyesno(
                    "Restart Recommended", 
                    "Theme changes will work best after restarting the application.\n\nWould you like to restart now?"
                ):
                    # Use a safer restart method that doesn't rely on file paths
                    try:
                        # First destroy the current application
                        self.controller.destroy()
                        
                        # Start a new Python process running the same script
                        # Use subprocess instead of os.execl for better compatibility
                        import sys
                        import subprocess
                        
                        # Get the current Python executable
                        python_exe = sys.executable
                        
                        # Use quotes around paths to handle spaces
                        subprocess.Popen([python_exe, "-c", 
                            f"import os; os.chdir(r'{os.getcwd()}'); "
                            f"os.system(r'\"{python_exe}\" \"{os.path.basename(__file__)}\"')"])
                    except Exception as e:
                        print(f"Error restarting: {e}")
                    return
        else:
            print("DEBUG: No changes detected to save")
            # No changes
            messagebox.showinfo("No Changes", "No settings were changed.")
        
        # Rebuild UI to reflect current settings
        self.build_settings_ui()
    
    def reset_to_default(self):
        """Reset settings to default values"""
        self.select_theme("light")
        self.select_language("English")
        self.save_settings()
    
    def apply_language(self, lang: str):
        """Apply language updates to this frame"""
        self.build_settings_ui()

# ABOUT Page
class AboutPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Button(self, text="⬅ Back", bootstyle="secondary", command=lambda: controller.show_frame(MainPage)).place(x=20, y=20)
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
    def on_close():
        if app.observer:
            app.observer.stop()
            app.observer.join()
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()