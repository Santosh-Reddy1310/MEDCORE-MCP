#!/usr/bin/env python
"""Get the full error message."""
import os
import sys
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_LOCAL_PATH = os.path.join(PROJECT_ROOT, ".env.local")
load_dotenv(ENV_LOCAL_PATH, override=True)

sys.path.insert(0, '.')

from client.ai_client import ask_sync

result = ask_sync("How many patients are there?")
print(result)
