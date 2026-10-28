#!/usr/bin/env python3
"""Compatibility entry point for the modular picks pipeline."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.line_lab.constants import *
from scripts.line_lab.ingest import *
from scripts.line_lab.features import *
from scripts.line_lab.model import *
from scripts.line_lab.market import *
from scripts.line_lab.ledger import *
from scripts.line_lab.report import *
from scripts.line_lab.runner import main

if __name__ == '__main__':
    main()
