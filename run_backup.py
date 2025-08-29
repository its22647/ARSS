import os
import sys
import json
from backup import show_notification, load_backed_up_files, authenticate_google_drive, FolderEventHandler, SCHEDULE_FILE
from watchdog.observers import Observer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

if __name__ == "__main__":
    try:
        # ✅ Load DB & Google Drive auth
        load_backed_up_files()
        drive_service = authenticate_google_drive()

        # ✅ Load saved folders
        if not os.path.exists(SCHEDULE_FILE):
            show_notification("Realtime Backup", "No folders configured for monitoring.")
            sys.exit(0)

        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        folders = data.get("folders", [])

        if not folders:
            show_notification("Realtime Backup", "No folders configured for monitoring.")
            sys.exit(0)

        # ✅ Start monitoring saved folders
        event_handler = FolderEventHandler(drive_service)
        observer = Observer()
        for folder in folders:
            if os.path.exists(folder):
                observer.schedule(event_handler, folder, recursive=True)

        observer.daemon = True
        observer.start()

        show_notification("Realtime Backup", f"Monitoring {len(folders)} folder(s)...")

        # ✅ Keep observer alive forever
        observer.join()

    except Exception as e:
        show_notification("Realtime Backup Error", str(e))
        sys.exit(1)
