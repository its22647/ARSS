import os
import subprocess

def scan_and_delete(file_path):
    result = subprocess.run(["clamscan", file_path], capture_output=True, text=True)
    output = result.stdout

    if "FOUND" in output:
        print(f"⚠ Threat detected: {file_path}")
        os.remove(file_path)  # Deletes the infected file
        print("✅ Infected file deleted.")
    else:
        print("✅ No threats found.")

scan_and_delete("C:/Users/Dell/eicar.com")  # Test with the EICAR file
