import os
import subprocess
import logging

# Configure logging
logging.basicConfig(filename='clamav_scan.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def scan_and_delete(file_path):
    if not os.path.isfile(file_path):
        logging.error(f"File not found: {file_path}")
        print(f"❌ File not found: {file_path}")
        return

    logging.info(f"🔍 Scanning: {file_path}")
    print(f"🔍 Scanning: {file_path}")

    result = subprocess.run(["clamscan", file_path], capture_output=True, text=True)
    output = result.stdout

    if "FOUND" in output:
        logging.warning(f"⚠ Threat detected: {file_path}")
        print(f"⚠ Threat detected: {file_path}")
        os.remove(file_path)  # Deletes the infected file
        logging.info("✅ Infected file deleted.")
        print("✅ Infected file deleted.")
    else:
        logging.info(f"✅ No threats found in: {file_path}")
        print(f"✅ No threats found in: {file_path}")

if __name__ == "__main__":
    # Specify the correct path to the infected file
    infected_file_path = r"C:\Users\Dell\Desktop\test_folder\eicar.com"
    scan_and_delete(infected_file_path) 