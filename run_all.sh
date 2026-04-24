#!/bin/bash

echo ""
echo "========================================"
echo "Electrical Fault Detection & Classification"
echo "FastAPI + Streamlit Deployment"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Starting FastAPI Backend..."
echo "========================================"
echo "FastAPI will run on: http://localhost:8000"
echo "Swagger Docs: http://localhost:8000/docs"
echo ""

# Start FastAPI in background
python main.py &
FASTAPI_PID=$!

# Wait for FastAPI to start
sleep 3

echo ""
echo "========================================"
echo "Starting Streamlit Frontend..."
echo "========================================"
echo "Streamlit will run on: http://localhost:8501"
echo ""

# Start Streamlit in foreground
streamlit run app.py

# Clean up background process
kill $FASTAPI_PID 2>/dev/null

echo ""
echo "Application stopped"
