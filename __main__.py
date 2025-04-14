#!/usr/bin/env python3
"""
Main entry point for the integrated blockchain application.
This script runs the Flask app with the configured host and port.
"""
from app import run_app

if __name__ == "__main__":
    # Run the Flask application
    run_app(host="0.0.0.0", port=5000, debug=True) 