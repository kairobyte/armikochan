# ============================================================================
# File: 1. rename.py
# Auto-added section markers and high-level comments
# ============================================================================

# ====== Imports ======
import os

# ====== Constants / Config ======
header = input("Enter file header: ")

file_name = __file__
file_name = os.path.basename(file_name)

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

files = os.listdir()
updated_file = []

for file in files:
    if file == file_name:
        continue
    else:
        os.rename(file, header+file)

files = os.listdir()
print(files)