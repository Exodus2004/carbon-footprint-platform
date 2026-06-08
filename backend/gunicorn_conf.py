import os
import multiprocessing

# Bind to the port provided by Cloud Run, default to 8080
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"

# Set worker count based on CPU cores for optimal performance
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))

# Timeout and keepalive settings for robust request handling
graceful_timeout = 120
timeout = 120
keepalive = 5
