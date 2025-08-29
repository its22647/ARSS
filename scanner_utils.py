import clamd
import os
import zipfile

def scan_and_delete(file_path, auto_delete=False):
    try:
        if not os.path.exists(file_path):
            return "Error: File does not exist."

        # Normalize path
        file_path = os.path.abspath(file_path)

        cd = clamd.ClamdNetworkSocket(host="127.0.0.1", port=3310)
        cd.ping()

        # Scan normal file
        if not zipfile.is_zipfile(file_path):
            result = cd.scan(file_path)
        else:
            # Scan ZIP contents
            result = {}
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for f in zip_ref.namelist():
                    with zip_ref.open(f) as file_content:
                        r = cd.scan_stream(file_content.read())
                        result[f] = r.get(f) if r else ("ERROR", "Scan failed")

        print(f"[DEBUG] Scan result for {file_path}: {result}")

        if not result:
            return "Error: Scan failed or unexpected result."

        # For simplicity, consider first threat found
        for key, val in result.items():
            if val[0] == "FOUND":
                if auto_delete:
                    try:
                        os.remove(file_path)
                        return f"❌ Threat detected ({val[1]}). File deleted."
                    except Exception as e:
                        return f"❌ Threat detected ({val[1]}), but could not delete file: {str(e)}"
                else:
                    return f"❌ Threat detected: {val[1]}"

        # No threats
        return "✅ No threat detected."

    except clamd.ConnectionError:
        return "Error: Cannot connect to ClamAV daemon. Ensure clamd is running."
    except Exception as e:
        return f"Error during scanning: {str(e)}"
