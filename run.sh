#!/bin/bash

# This script starts the Flask server in the background, 
# then starts the SvelteKit server in the background, and waits for both to finish. 
#
# FLASK_PID: The process ID of the Flask server
# SVELTE_PID: The process ID the SvelteKit server
#    

# Activate the conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate claspp

# Start the backend Flask server
cd backend-flask
echo "Starting Flask server..."
python app.py &
FLASK_PID=$!
echo "Flask server started with PID $FLASK_PID"

# Start the frontend SvelteKit server
cd ../frontend-sveltekit
echo "Starting SvelteKit server..."
npm run dev &
SVELTE_PID=$!
echo "SvelteKit server started with PID $SVELTE_PID"

# Wait for both servers to finish
wait $FLASK_PID
wait $SVELTE_PID

# CLEANUP
# kill $(lsof -t -i :5200)