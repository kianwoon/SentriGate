#!/usr/bin/env python3
"""
Script to run the Mail Analysis API server.
"""

import sys
import os
import uvicorn

if __name__ == "__main__":
    """Run the API server."""
    # Add the project root directory to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
