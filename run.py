
# Run this file to have Jarvis running in the background


import subprocess


subprocess.Popen(["python", "main.py"], creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
