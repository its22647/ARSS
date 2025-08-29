import time, os
p = os.path.expanduser("~/Documents/test_encrypt.txt")
while True:
    with open(p, 'a') as f:
        f.write("0"*10000)
    time.sleep(0.01)
