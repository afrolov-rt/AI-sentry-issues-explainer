#!/bin/bash

echo "🚀 Starting AI Sentry Issues Explainer Backend..."

echo "🚀 Starting FastAPI server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000
