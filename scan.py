import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def scan_and_delete():
    # Open file dialog to select a file for scanning
    file_path = filedialog.askopenfilename(title="Select File to Scan")
    
    if not file_path:
        return  # If user cancels, do nothing

    result = subprocess.run(["clamscan", file_path], capture_output=True, text=True)
    output = result.stdout

    if "FOUND" in output:
        messagebox.showwarning("Threat Detected!", f"⚠ Threat detected: {file_path}\nFile will be deleted.")
        os.remove(file_path)  # Deletes the infected file
        messagebox.showinfo("File Removed", "✅ Infected file deleted successfully.")
    else:
        messagebox.showinfo("Scan Complete", "✅ No threats found.")

# GUI Setup
root = tk.Tk()
root.title("Anti-Ransomware Security Solution")
root.geometry("400x300")

scan_button = tk.Button(root, text="🛡 Start Scan", fg="white", bg="#FF5733", font=("Arial", 14), command=scan_and_delete)
scan_button.pack(pady=20)

root.mainloop()
