import subprocess

def update_clamav():
    try:
        subprocess.run(["freshclam"], check=True)
        print("✅ ClamAV database updated successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to update ClamAV database.")
