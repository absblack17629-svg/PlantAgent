# -*- coding: utf-8 -*-
import subprocess
import sys

# Run pip list and capture output
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                       capture_output=True, text=True)

# Write to file
with open('pip_output.txt', 'w', encoding='utf-8') as f:
    f.write(result.stdout)
    f.write(result.stderr)

print("Output written to pip_output.txt")