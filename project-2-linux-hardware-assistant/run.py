import uvicorn
import os
import sys

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)
    print("==================================================================")
    print("  Linux Hardware Q&A Assistant (Problem 2)")
    print("  Running Web UI at http://localhost:8002")
    print("  (Or run terminal CLI via: python cli.py)")
    print("==================================================================")
    uvicorn.run("app:app", host="127.0.0.1", port=8002, reload=False, app_dir=backend_dir)
