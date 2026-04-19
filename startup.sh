#!/bin/bash
cd /home/site/wwwroot/backend
/antenv/bin/pip install -r requirements.txt
/antenv/bin/uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
