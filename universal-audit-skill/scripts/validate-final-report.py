#!/usr/bin/env python3
"""Thin wrapper — see scripts/auditkit.py for the implementation."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auditkit
sys.exit(auditkit.main([sys.argv[0], "report", *sys.argv[1:]]))
