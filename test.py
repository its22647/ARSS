import os
import base64

# File path
test_file_path = "C:/Users/dell/Documents/high_entropy_test_file.txt"

# Generate 5MB random data
random_data = os.urandom(5 * 1024 * 1024)

# Encode into base64 to make it valid text
encoded_data = base64.b64encode(random_data)

# Save as text file
with open(test_file_path, "wb") as f:
    f.write(encoded_data)

print(f"High entropy test TEXT file created at {test_file_path}")