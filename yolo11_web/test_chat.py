#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

url = "http://localhost:8000/api/agent/chat"

# Test with a message that should trigger planting intent
messages = [
    "I want planting advice",
    "give me planting suggestions",
    "how to plant rice",
    "what crops should I plant",
]

for msg in messages:
    files = {"image": ("", "")}
    data = {"message": msg}
    response = requests.post(url, files=files, data=data)
    result = response.json()
    if result.get("code") == 200:
        resp = result["data"]["response"][:200]
        print(f"\n[{msg}]")
        print(f"Response: {resp}")
    else:
        print(f"\n[{msg}] Error: {result}")
