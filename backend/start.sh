#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "Stopping old server..."
pkill -f "python main.py" 2>/dev/null
sleep 2

echo "Starting server..."
nohup python main.py > server.log 2>&1 &
sleep 2

echo "Server started!"
echo "Admin: http://localhost:8000/admin"
lsof -i :8000 | grep python