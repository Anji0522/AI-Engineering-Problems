"""
Unified Launcher for Both Interview Engineering Projects:
1. AgentVerse: Social Network for AI Agents (Port 8001)
2. Linux Hardware Q&A Assistant (Port 8002)

Usage:
  python run_all.py
"""

import sys
import os
import subprocess
import time
import signal

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    p1_script = os.path.join(root_dir, "project-1-agent-social-network", "run.py")
    p2_script = os.path.join(root_dir, "project-2-linux-hardware-assistant", "run.py")

    print("\n" + "=" * 76)
    print("  🚀  AI ENGINEERING INTERVIEW PROJECTS - LOCALHOST LAUNCHER")
    print("=" * 76)
    print("  Initializing local web servers on isolated ports:")
    print("  • Project 1 (AgentVerse - AI Social Network)  --> http://localhost:8001")
    print("  • Project 2 (Linux Hardware Q&A Assistant)    --> http://localhost:8002")
    print("=" * 76 + "\n")

    # Start Project 1
    proc1 = subprocess.Popen([sys.executable, p1_script])
    time.sleep(1.2)

    # Start Project 2
    proc2 = subprocess.Popen([sys.executable, p2_script])
    time.sleep(1.0)

    print("\n" + "-" * 76)
    print("  ✅ Both Localhost Servers Are Live and Ready!")
    print("  ------------------------------------------------------------------------")
    print("  🔗 Project 1 Web UI:  http://localhost:8001  (or http://127.0.0.1:8001)")
    print("  🔗 Project 2 Web UI:  http://localhost:8002  (or http://127.0.0.1:8002)")
    print("  ------------------------------------------------------------------------")
    print("  Press Ctrl+C anytime in this terminal to gracefully terminate both.")
    print("-" * 76 + "\n")

    try:
        while True:
            time.sleep(0.5)
            # If any process terminated prematurely, break
            if proc1.poll() is not None or proc2.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n[Shutdown] Stopping servers gracefully...")
    finally:
        for proc in [proc1, proc2]:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("Shutdown complete. All localhost ports freed.\n")

if __name__ == "__main__":
    main()
