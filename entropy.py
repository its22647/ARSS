import os
import math
import psutil
import time
import sys
import logging
import collections
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import messagebox
import queue
popup_queue = queue.Queue()
# ----------------------------------------
# --- Detect AppData directory ---
APPDATA_DIR = os.getenv("APPDATA", os.path.expanduser("~"))
LOG_DIR = os.path.join(APPDATA_DIR, "AntiRansomware", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Safe log file path ---
LOG_FILE = os.path.join(LOG_DIR, "entropy_monitor.log")

# --- Logging setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Config
ENTROPY_THRESHOLD = 7.5
# ✅ Extensions jo hamesha safe treat hon (no entropy check)
ALWAYS_SAFE_EXTENSIONS = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.jpg', '.jpeg', '.png',
    '.gif', '.mp3', '.mp4', '.avi', '.mkv', '.zip','.temp', '.rar', '.exe'
]

SAFE_EXTENSIONS = [
    '.enc', '.dat', '.bin', '.pak', '.idx', '.db', '.sqlite',
    '.cab', '.res', '.dll', '.sys', '.ini', '.cfg', '.conf',
    '.json', '.log', '.key', '.exe', '.dill', '.png'
]
# ✅ Extensions that are always suspicious if detected
ALWAYS_SUSPICIOUS_EXTENSIONS = [
    '.crypt', '.crypted', '.crypto', '.crypz', '.cryp1',
    '.locked', '.locky', '.payme', '.ransom',
    '.encrypted', '.enc1', '.enc2', '.enc3',
    '.wnry', '.wannacry', '.teslacrypt', '.cerber',
    '.djvu', '.tro', '.rumba', '.radman', '.stop'
]

USER_FOLDERS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Videos")
]
USER_FOLDERS = [os.path.normpath(p).lower() for p in USER_FOLDERS]

# ----------------------------------------
# Helpers
def calculate_entropy(file_path, chunk_size=1024*1024):  # 1 MB
    try:
        size = os.path.getsize(file_path)
        if size < 1024:  # chhoti files ignore karo
            return 0.0

        with open(file_path, "rb") as f:
            if size <= chunk_size:
                data = f.read()
            else:
                # sample start + middle + end
                part_size = chunk_size // 3
                data = f.read(part_size)
                f.seek(size // 2)
                data += f.read(part_size)
                f.seek(-part_size, os.SEEK_END)
                data += f.read(part_size)

        if not data:
            return 0.0

        from collections import Counter
        counter = Counter(data)
        total = len(data)
        entropy = -sum(
            count / total * math.log2(count / total)
            for count in counter.values()
        )
        return entropy
    except Exception:
        return 0.0



def terminate_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
        logger.warning(f"[💀] Terminated process tree {pid}")
    except Exception as e:
        logger.error(f"Failed to terminate process {pid}: {e}")


def find_process_by_file(file_path):
    norm = os.path.normpath(file_path).lower()

    for proc in psutil.process_iter(['pid', 'name', 'cwd', 'cmdline']):
        try:
            # 1) Exact open file handle
            for f in proc.open_files():
                if os.path.normpath(f.path).lower() == norm:
                    return proc

            # 2) Check if cwd matches file directory
            folder = os.path.dirname(norm)
            if proc.info.get('cwd') and proc.info['cwd'].lower() == folder:
                return proc

            # 3) Check if file path is in cmdline args
            cmdline = " ".join(proc.info.get('cmdline') or []).lower()
            if norm in cmdline:
                return proc

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return None


def safe_delete(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[🗑] Deleted suspicious file {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")

# ----------------------------------------
# Handler


class EntropyMonitorHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_entropy_cache = {}
        
    def on_created(self, event):
        if not event.is_directory:
            self.check_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.check_file(event.src_path)

    def check_file(self, file_path):
     try:
        ext = os.path.splitext(file_path)[1].lower()

        # ✅ 0) If extension is always suspicious → immediately alert
        if ext in ALWAYS_SUSPICIOUS_EXTENSIONS:
            logger.warning(f"[🚨] Suspicious extension detected: {file_path}")
            proc = find_process_by_file(file_path)
            popup_queue.put((file_path, proc, ENTROPY_THRESHOLD + 1))  # force trigger
            return  

        # ✅ 1) Ignore always-safe extensions completely
        if ext in ALWAYS_SAFE_EXTENSIONS:
            return  

        # ✅ 2) Calculate entropy for others
        entropy = calculate_entropy(file_path)

        # ✅ 3) If extension is in SAFE_EXTENSIONS and entropy is normal → ignore
        if ext in SAFE_EXTENSIONS and entropy <= ENTROPY_THRESHOLD:
            return  

        # ✅ 4) Already processed with same entropy? skip
        last_entropy = self.file_entropy_cache.get(file_path)
        if last_entropy and abs(last_entropy - entropy) < 0.05:
            return  

        # ✅ 5) Suspicious → alert
        if entropy > ENTROPY_THRESHOLD:
            logger.warning(f"[⚠] High entropy file: {file_path} ({entropy:.2f})")
            self.file_entropy_cache[file_path] = entropy  
            proc = find_process_by_file(file_path)
            popup_queue.put((file_path, proc, entropy))

     except Exception as e:
        logger.error(f"[❌] check_file failed: {e}")




def process_popups():
    try:
        while True:
            file_path, proc, entropy = popup_queue.get_nowait()

            if proc:
                try:
                    proc.suspend()
                    proc_name = proc.name()
                    logger.info(f"[⏸] Suspended process {proc_name} (PID: {proc.pid})")

                    result = messagebox.askyesno(
                        "Suspicious File Detected",
                        f"High entropy file detected:\n{file_path}\n\n"
                        f"Process: {proc_name} (PID: {proc.pid})\n\n"
                        f"Do you want to TERMINATE the process and DELETE the file?"
                    )

                    if result:
                        terminate_process_tree(proc.pid)
                        time.sleep(0.5)
                        safe_delete(file_path)

                        # ✅ reset cache
                        if file_path in handler.file_entropy_cache:
                            del handler.file_entropy_cache[file_path]
                    else:
                        proc.resume()
                        logger.info(f"[↩] Resumed process {proc_name} (PID: {proc.pid})")

                except Exception as e:
                    logger.error(f"Error handling suspicious process: {e}")

            else:
                result = messagebox.askyesno(
                    "Suspicious File Detected",
                    f"High entropy file detected:\n{file_path}\n\n"
                    f"No active process linked.\n\n"
                    f"Do you want to DELETE the file?"
                )
                if result:
                    safe_delete(file_path)

                    # ✅ reset cache
                    if file_path in handler.file_entropy_cache:
                        del handler.file_entropy_cache[file_path]

    except queue.Empty:
        pass




if __name__ == "__main__":
    observer = Observer()
    handler = EntropyMonitorHandler()

    for folder in USER_FOLDERS:
        if os.path.exists(folder):
            observer.schedule(handler, folder, recursive=True)
            logger.info(f"[✓] Monitoring {folder}")

    observer.start()

    # ✅ Tkinter root in main thread
    root = tk.Tk()
    root.withdraw()

    # ✅ Start popup processor loop
    def poll_queue():
        process_popups()
        root.after(500, poll_queue)  # keep polling every 500ms

    poll_queue()  # start loop

    try:
        root.mainloop()  # Tkinter event loop
    except KeyboardInterrupt:
        observer.stop()
    observer.join()