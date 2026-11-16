import uvicorn
import os
import sys

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)
    print("==================================================================")
    print("  AgentVerse: Social Network for AI Agents (Problem 1)")
    print("  Running at http://localhost:8001")
    print("==================================================================")
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=False, app_dir=backend_dir)
