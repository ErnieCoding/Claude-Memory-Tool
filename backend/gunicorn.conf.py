import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('FLASK_PORT', '5000')}"
backlog = 2048

workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = int(os.getenv('GUNICORN_TIMEOUT', 1200))  # Настраиваемый timeout
keepalive = 2

accesslog = '-' 
errorlog = '-'  
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = 'claude-memory-backend'

daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

keyfile = None
certfile = None

preload_app = True

max_requests = 1000
max_requests_jitter = 50
