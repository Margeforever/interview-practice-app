#!/bin/bash
# Startup script for running the Streamlit application in server or container environments.
# Provides a reproducible entry point with explicit server configuration (port, address, headless mode).
# Primarily intended for non-managed deployments (e.g., Docker, VM, cloud servers);
# not required for Streamlit Cloud but kept for deployment completeness and clarity.
streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true