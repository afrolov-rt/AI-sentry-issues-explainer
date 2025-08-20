#!/bin/bash

echo "🚀 Starting AI Sentry Issues Explainer Backend..."

echo "⏳ Waiting for MongoDB to be ready..."
sleep 5

echo "🔧 Initializing demo data..."
python init_demo.py

echo "🚀 Starting FastAPI server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000
