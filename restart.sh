sudo pkill -9 gunicorn
source venv/bin/activate
nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:backend_app --bind 0.0.0.0:8000 &
