#!/usr/bin/env python3
"""
Lanceur direct de la Caisse Enregistreuse.
Ouvre automatiquement la caisse dans votre navigateur.
"""

import os
import sys
from pathlib import Path

# Assure que le dossier parent est dans le path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from caisse_enregistreuse.app import run_server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    is_cloud = "PORT" in os.environ or "RENDER" in os.environ or "DYNO" in os.environ or os.environ.get("HEADLESS") == "1"
    run_server(port=port, open_browser=not is_cloud)
