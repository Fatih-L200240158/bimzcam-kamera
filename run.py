# -*- coding: utf-8 -*-
"""
Main entry point for BimzCam Flask Application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Default Flask port for development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
