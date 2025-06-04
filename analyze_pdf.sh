#!/bin/bash
#
# Wrapper script for simple_pdf_analyzer.py
# Automatically uses the unified-redaction-hub virtual environment
#

# Set the virtual environment path
VENV_PATH="/home/lroc/unified-redaction-hub/venv"
SCRIPT_PATH="/home/lroc/simple_pdf_analyzer.py"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PATH"
    echo "Please ensure the unified-redaction-hub environment is set up."
    exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "ERROR: PDF analyzer script not found at $SCRIPT_PATH"
    exit 1
fi

# Run the PDF analyzer with the virtual environment's Python
"$VENV_PATH/bin/python" "$SCRIPT_PATH" "$@"