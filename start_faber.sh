#!/bin/bash

# Activate virtual environment
source /root/datpt/Faber_server/FABER_App_Backend/venv/bin/activate

# Start the application
cd /root/datpt/Faber_server/FABER_App_Backend
python3 -m app.main
