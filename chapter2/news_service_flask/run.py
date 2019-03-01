# /run.py
import os
from src.app import load_app

app = load_app(os.getenv('APP_ENV'))

if __name__ == '__main__':
    port = os.getenv('APP_PORT')
    app.run(host='0.0.0.0', port=port)
