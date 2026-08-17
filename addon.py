import subprocess
import os
import time

os.system('taskkill /f /fi "WINDOWTITLE eq Browse*" >nul 2>&1')  # Close browse tab
time.sleep(0.1)
os.system('taskkill /f /fi "WINDOWTITLE eq Korean - Anki*" >nul 2>&1')  # Close Anki main window
time.sleep(0.25)

filepath = r"D:\Programs\Anki\anki.exe"
Anki = subprocess.Popen(filepath)
