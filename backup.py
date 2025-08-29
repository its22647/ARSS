import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pickle
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import subprocess
import hashlib
import shutil
import sys
import ctypes
import threading
import time

# ===================== Windows Toast (PowerShell) ===================== #
def show_notification(title, message):
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {title}: {message}"
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)  # 0x40 = Info icon
        print(f"[POPUP] {log_msg}")
    except Exception as e:
        print(f"[NOTIFY-FAIL] {log_msg} (Error: {e})")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception as e:
        print(f"[LOG-ERROR] Could not write to backup.log: {e}")

# ===================== Config ===================== #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'backup.log')
TASK_NAME = "AntiRansomwareBackup"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE      = os.path.join(BASE_DIR, 'token.pickle')
SCHEDULE_FILE   = os.path.join(BASE_DIR, 'backup_schedule.json')
BACKED_UP_DB    = os.path.join(BASE_DIR, 'backed_up_files.json')
CREDENTIALS_FILE= os.path.join(BASE_DIR, 'credentials.json')

log_lock = threading.Lock()
def log_message(msg):
    timestamped = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(timestamped)
    with log_lock:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(timestamped + "\n")
        except Exception as e:
            print(f"[LOG-ERROR] Could not write to log: {e}")

# ===================== Backed-up DB ===================== #
backed_up_db = {}  # {absolute_path: file_hash}

def load_backed_up_files():
    global backed_up_db
    if os.path.exists(BACKED_UP_DB):
        try:
            with open(BACKED_UP_DB, "r", encoding="utf-8") as f:
                backed_up_db = json.load(f)
        except:
            backed_up_db = {}
    else:
        backed_up_db = {}

def save_backed_up_files():
    try:
        with open(BACKED_UP_DB, "w", encoding="utf-8") as f:
            json.dump(backed_up_db, f, indent=2)
    except:
        pass

# ===================== Google Drive Auth ===================== #
def authenticate_google_drive():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    try:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    except Exception:
        creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

# ===================== Upload Helper ===================== #
# Global set for files that cannot be accessed
skipped_files = set()

def get_file_hash(file_path):
    try:
        if file_path in skipped_files:
            return None  # Already skipped
        file_size = os.path.getsize(file_path)
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            first_chunk = f.read(min(1024 * 1024, file_size))
            h.update(first_chunk)
            if file_size > 1024 * 1024:
                f.seek(max(file_size - 1024 * 1024, 0))
                last_chunk = f.read(min(1024 * 1024, file_size))
                h.update(last_chunk)
        return h.hexdigest()
    except PermissionError:
        log_message(f"[WARN] Permission denied, skipping: {file_path}")
        skipped_files.add(file_path)
        return None
    except Exception as e:
        log_message(f"[ERROR] Hashing failed for {file_path}: {e}")
        return None




# ---------------- Thread-safe batch notifications ---------------- #
uploaded_files_batch = []
batch_lock = threading.Lock()

def schedule_batch_notification(delay=5):
    """Schedule batch notification after a short delay to avoid multiple popups."""
    def notify():
        with batch_lock:
            if uploaded_files_batch:
                count = len(uploaded_files_batch)
                message = f"{count} file(s) uploaded successfully."
                log_message(f"[BATCH] {count} file(s) uploaded successfully.")
                ctypes.windll.user32.MessageBoxW(0, message, "File Backup", 0x40)
                uploaded_files_batch.clear()
    timer = threading.Timer(delay, notify)
    timer.daemon = True  # Ensure it doesn't block program exit
    timer.start()


def upload_file_to_drive(service, file_path, force_upload=False, realtime=False):
    """Upload file to Google Drive. Prevent duplicate uploads across manual + realtime."""
    # 1. Check if the file exists
    if not os.path.isfile(file_path):
        log_message(f"[WARN] File not found: {file_path}")
        return False

    filename = os.path.basename(file_path)

    try:
        # 2. Compute file hash for deduplication
        file_hash = get_file_hash(file_path)
        if not file_hash:
            log_message(f"[WARN] Cannot compute hash for {file_path}")
            return False

        # 3. Check if the file or its content is already backed up
        already_backed_up = (file_path in backed_up_db and backed_up_db[file_path] == file_hash)
        duplicate_content = (file_hash in backed_up_db.values())

        # 4. Skip if duplicate (unless force_upload is True)
        if already_backed_up or (duplicate_content and not force_upload):
            log_message(f"[INFO] Skipped duplicate: {file_path}")
            return False

        # 5. Prepare metadata and upload to Google Drive
        file_metadata = {'name': filename}
        media = MediaFileUpload(file_path, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 6. Update the backup database
        backed_up_db[file_path] = file_hash
        save_backed_up_files()

        log_message(f"[SUCCESS] Uploaded: {file_path}")

        # 7. Send notifications
        if realtime:
            with batch_lock:
                uploaded_files_batch.append(filename)
            schedule_batch_notification()
        else:
            safe_show_notification("File Backup", f"Uploaded: {filename}")

        return True

    except Exception as e:
        # 8. Handle errors gracefully
        log_message(f"[ERROR] Upload failed for {file_path}: {e}")
        safe_show_notification("File Backup Failed", f"{filename}: {e}")
        return False



# ===================== Manual Backup ===================== #
def manual_backup():
    critical_folders = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Pictures")
    ]
    drive_service = authenticate_google_drive()
    uploaded = 0
    for folder in critical_folders:
        for root_dir, _, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root_dir, file)
                if upload_file_to_drive(drive_service, full_path):
                    uploaded += 1
    messagebox.showinfo("Manual Backup", f"Manual backup finished. {uploaded} file(s) uploaded.")

def add_to_startup():
    """Add run_backup.py to Current User Startup folder"""
    startup_folder = os.path.join(os.getenv('APPDATA'), r"Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    script_path = os.path.join(BASE_DIR, "run_backup.py")
    shortcut_path = os.path.join(startup_folder, "AntiRansomwareBackup.lnk")
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = BASE_DIR
        shortcut.IconLocation = sys.executable
        shortcut.save()
        show_notification("Startup Enabled", "Realtime backup will run on Windows startup.")
        return True
    except Exception as e:
        show_notification("Startup Error", str(e))
        return False

# ===================== Real-Time Backup ===================== #
def safe_show_notification(title, message):
    threading.Thread(target=show_notification, args=(title, message)).start()

class FolderEventHandler(FileSystemEventHandler):
    """Handle file system events and upload to Google Drive."""
    def __init__(self, drive_service):
        self.drive_service = drive_service

    def on_created(self, event):
        if not event.is_directory:
            upload_file_to_drive(self.drive_service, event.src_path, realtime=True)

    def on_modified(self, event):
        if not event.is_directory:
            upload_file_to_drive(self.drive_service, event.src_path, realtime=True)

def start_realtime_backup(folders=None):
    """Start realtime backup for a folder or list of folders."""
    if folders is None:
        folders = []
        while True:
            folder = filedialog.askdirectory(title="Select folder to monitor for backup")
            if not folder:
                break
            folders.append(folder)
            if not messagebox.askyesno("More?", "Add another folder?"):
                break
        if not folders:
            print("[DEBUG] No folders selected, exiting...")
            return
    elif isinstance(folders, str):
        folders = [folders]

    print(f"[DEBUG] Final folders list: {folders}")

    # Save folder list to schedule file for future automatic startup monitoring
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump({"folders": folders}, f)
        print(f"[DEBUG] Saved folders to {SCHEDULE_FILE}")
    except Exception as e:
        print(f"[ERROR] Could not save schedule: {e}")

    # Load already backed-up files
    load_backed_up_files()
    print("[DEBUG] Loaded backed-up files DB")

    # Authenticate Google Drive
    drive_service = authenticate_google_drive()
    print("[DEBUG] Google Drive authenticated")

    # Setup watchdog observer
    event_handler = FolderEventHandler(drive_service)
    observer = Observer()
    for folder in folders:
        print(f"[DEBUG] Scheduling observer for folder: {folder}")
        observer.schedule(event_handler, folder, recursive=True)

    observer.daemon = True
    observer.start()
    print("[DEBUG] Observer started in background thread")

    # Add to Windows startup so this script auto-runs after reboot
    added = add_to_startup()
    if added:
        print("[DEBUG] Realtime backup will auto-start on Windows login.")
    else:
        print("[DEBUG] Failed to add to startup. Manual start required.")

    show_notification("Realtime Backup", f"Monitoring {len(folders)} folder(s) for new/modified files...")
    print(f"[DEBUG] Notification triggered for {len(folders)} folders")
