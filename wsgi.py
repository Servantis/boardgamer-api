import os
import sys


path = "/home/servantis/boardgamer-api"

if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

from app import app as application