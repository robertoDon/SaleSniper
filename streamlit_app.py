"""Wrapper entrypoint for Streamlit Cloud.

Streamlit Cloud expects a main script at the repo root (by default `streamlit_app.py`).
This wrapper simply imports the real app implementation located in `scr/streamlit_app.py`.
"""

# Ensure the package directory is importable (should already be the case on Streamlit Cloud).
# This is just a small helper to keep the streamlit entrypoint at the repo root.

import scr.streamlit_app  # noqa: F401
