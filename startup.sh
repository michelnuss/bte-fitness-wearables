#!/bin/bash
# Azure App Service startup script
cd /home/site/wwwroot/backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
