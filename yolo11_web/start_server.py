#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import time
import sys

# Start the server
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Wait for startup
time.sleep(15)

# Check if process is still running
if proc.poll() is None:
    print("Server started successfully!")
else:
    print("Server failed to start")
    # Print output
    output, _ = proc.communicate()
    print(output[-2000:] if len(output) > 2000 else output)
