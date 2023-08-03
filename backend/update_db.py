import os
import glob

files = glob.glob("authentication/migrations/*")

for file in files:
    if '00' not in file:
        continue
    os.remove(file)

files = glob.glob("posts/migrations/*")

for file in files:
    if '00' not in file:
        continue
    os.remove(file)

os.remove("db.sqlite3")