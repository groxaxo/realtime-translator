#!/bin/bash

# Start ngrok tunnels for frontend and LiveKit
echo "Starting ngrok tunnels..."
echo ""

# Start ngrok with the config file
ngrok start --config=ngrok.yml --all &
NGROK_PID=$!

# Wait for ngrok to start
echo "Waiting for ngrok to start tunnels..."
sleep 5

# Get the ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; tunnels = json.load(sys.stdin)['tunnels']; print(next(t['public_url'] for t in tunnels if t['name'] == 'frontend'), '')" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "ERROR: Could not get ngrok URL"
    kill $NGROK_PID
    exit 1
fi

echo ""
echo "=========================================="
echo "Ngrok tunnels started successfully!"
echo "=========================================="
echo "Frontend URL:  $NGROK_URL"
echo "LiveKit URL:   ${NGROK_URL}/livekit"
echo "=========================================="
echo ""

# Update .env file with the ngrok URL
echo "Updating .env file with ngrok configuration..."

# Replace NEXT_PUBLIC_LIVEKIT_URL with the ngrok LiveKit URL
sed -i "s|^NEXT_PUBLIC_LIVEKIT_URL=.*|NEXT_PUBLIC_LIVEKIT_URL=wss://$(echo $NGROK_URL | sed 's|https://||')|g" .env

echo "Updated NEXT_PUBLIC_LIVEKIT_URL to: wss://$(echo $NGROK_URL | sed 's|https://||')"
echo ""
echo "Rebuilding frontend with new configuration..."
docker compose build frontend && docker compose up -d frontend

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo "Access the app at: $NGROK_URL"
echo ""
echo "Press Ctrl+C to stop ngrok"
echo "=========================================="

# Wait for user to stop
wait $NGROK_PID
