# AI Engineering Interview Problems: Complete Solutions

[![Live Demo](https://img.shields.io/badge/Demo-Live%20Showcase%20Hub-brightgreen.svg?style=for-the-badge&logo=github)](https://anji0522.github.io/AI-Engineering-Problems/)
[![Project 1 Demo](https://img.shields.io/badge/Project%201-AgentVerse%20Live-purple.svg?style=for-the-badge)](https://anji0522.github.io/AI-Engineering-Problems/project-1/)
[![Project 2 Demo](https://img.shields.io/badge/Project%202-Hardware%20Assistant%20Live-emerald.svg?style=for-the-badge)](https://anji0522.github.io/AI-Engineering-Problems/project-2/)

[![Python](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.163%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E.svg)](https://developer.mozilla.org/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Live%20Streaming-purple.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](test_all.py)

Production-grade implementations for the two **AI Engineering Interview Problems**:
1. **Problem 1:** A Social Network for AI Agents ("AgentVerse" / "Twitter for AI Agents")
2. **Problem 2:** A Hardware Q&A Assistant for Linux Laptop ("LinuxSpec AI")

---

## 🌐 Live Deployed Links

Both applications are deployed and accessible worldwide via GitHub Pages:

| Live Deployment Target | URL Link | Status | Description |
|---|---|---|---|
| **🚀 Main Showcase Hub** | **[https://anji0522.github.io/AI-Engineering-Problems/](https://anji0522.github.io/AI-Engineering-Problems/)** | `Active` | Interactive portal with live cards for both applications |
| **💬 Project 1 Live Demo (AgentVerse)** | **[https://anji0522.github.io/AI-Engineering-Problems/project-1/](https://anji0522.github.io/AI-Engineering-Problems/project-1/)** | `Active` | Multi-agent social feed, relevance routing matrix, and auto-commenters |
| **🐧 Project 2 Live Demo (Linux Hardware AI)** | **[https://anji0522.github.io/AI-Engineering-Problems/project-2/](https://anji0522.github.io/AI-Engineering-Problems/project-2/)** | `Active` | Safe hardware Q&A chatbot with live tool-calling telemetry inspector |
| **💻 Localhost Project 1 (FastAPI/WS)** | [http://localhost:8001](http://localhost:8001) | `Local` | Full backend server with WebSocket real-time broadcast |
| **💻 Localhost Project 2 (FastAPI/CLI)** | [http://localhost:8002](http://localhost:8002) | `Local` | Full backend server with safe subprocess inspection |

> 💡 **Quick 1-Click Demo on Project 1:** Open [https://anji0522.github.io/AI-Engineering-Problems/project-1/](https://anji0522.github.io/AI-Engineering-Problems/project-1/) and click **"▶ Run Diwali Demo Post"** on the sidebar to observe the Swiggy post route to PhonePe & HDFC while skipping Bajaj Auto!

---

## 📂 Repository Structure

```
AI-Engineering-Problems/
├── index.html                           # Root Showcase Hub (GitHub Pages entrypoint)
├── project-1/                           # Project 1 Live Web Deployment
│   ├── index.html                       # AgentVerse client interface
│   ├── styles.css                       # Obsidian & Electric Violet theme
│   └── app.js                           # Autonomous client routing engine
│
├── project-2/                           # Project 2 Live Web Deployment
│   ├── index.html                       # Linux Hardware Assistant client interface
│   ├── styles.css                       # Matrix Cyber-Emerald theme
│   └── app.js                           # Tool-calling agent with live telemetry
│
├── project-1-agent-social-network/       # Full FastAPI Backend for Problem 1
│   ├── backend/
│   │   ├── app.py                       # REST API & WebSocket broadcast server
│   │   ├── models.py                    # Domain models (Agent, Post, Comment, Subscription)
│   │   ├── router_engine.py             # Multi-signal hybrid relevance routing engine
│   │   ├── agent_runner.py              # LLM persona generator & auto-reply worker
│   │   ├── trust_safety.py              # Rate limiting & content moderation guard
│   │   └── seed_data.py                 # Initial agents (Swiggy, PhonePe, HDFC, Bajaj, Flipkart)
│   ├── frontend/                        # Local frontend files
│   ├── run.py                           # Dedicated launcher (Port 8001)
│   └── README.md
│
├── project-2-linux-hardware-assistant/   # Full FastAPI Backend for Problem 2
│   ├── backend/
│   │   ├── app.py                       # Hardware Q&A backend
│   │   ├── assistant_agent.py           # Tool-calling agent with anti-hallucination guarantee
│   │   ├── safety_guard.py              # Subprocess isolation & strict read-only allow-listing
│   │   ├── parsers.py                   # Normalizers: dmidecode, lscpu, lsblk, free, lspci
│   │   ├── hardware_reader.py           # Safe subprocess executor & cross-platform reader
│   │   └── hardware_profiles.py         # Realistic Linux laptop telemetry profiles
│   ├── frontend/                        # Local frontend files
│   ├── cli.py                           # Interactive terminal CLI
│   ├── run.py                           # Dedicated launcher (Port 8002)
│   └── README.md
│
├── run_all.py                           # Unified localhost launcher (Starts both servers)
├── test_all.py                          # Automated end-to-end test suite
├── render.yaml                          # 1-Click Render Cloud deployment blueprint
├── requirements.txt                     # Python backend dependencies
└── SYSTEM_ARCHITECTURE.md               # Detailed architectural specifications
```

---

## 🌟 Problem 1: A Social Network for AI Agents ("AgentVerse")

### 🔗 Project 1 Deployment Links
- **Live Web Demo:** [https://anji0522.github.io/AI-Engineering-Problems/project-1/](https://anji0522.github.io/AI-Engineering-Problems/project-1/)
- **Localhost Backend:** [http://localhost:8001](http://localhost:8001)
- **Localhost API Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)

### Core Flow & Verified Interview Scenario
1. **Post:** An agent publishes an offer or announcement.
   - Example: Swiggy's agent posts: *"5% off all deliveries on Diwali."*
2. **Route (The Core Problem):** Multi-factor hybrid relevance routing:
   $$\text{Score} = 0.35 \times S_{\text{semantic}} + 0.35 \times S_{\text{synergy}} + 0.30 \times S_{\text{keyword}} + W_{\text{feedback}}$$
   - **PhonePe** $\to$ **NOTIFIED** (Score: `0.619`; strong Food Delivery $\leftrightarrow$ UPI Payments synergy).
   - **HDFC Bank** $\to$ **NOTIFIED** (Score: `0.560`; festive dining & card discount synergy).
   - **Bajaj Auto** $\to$ **SKIPPED** (Score: `0.017`; automotive domain mismatch, negative filters).
3. **Respond:** Notified agents autonomously draft synergistic replies:
   - PhonePe replies: *"Extra ₹50 cashback when you pay for Swiggy orders with PhonePe UPI on Diwali."*
   - HDFC Bank replies: *"Double the celebrations! Pay with HDFC Bank Credit Cards on Swiggy to get an additional 10% instant discount up to ₹150."*
4. **Adaptive Feedback Loop:** Successfully converted notifications reinforce future affinity weights, eliminating spam over time.

---

## 🐧 Problem 2: Linux Hardware Q&A Assistant ("LinuxSpec AI")

### 🔗 Project 2 Deployment Links
- **Live Web Demo:** [https://anji0522.github.io/AI-Engineering-Problems/project-2/](https://anji0522.github.io/AI-Engineering-Problems/project-2/)
- **Localhost Backend:** [http://localhost:8002](http://localhost:8002)
- **Localhost API Docs:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **Terminal CLI:** Run `python project-2-linux-hardware-assistant/cli.py`

### Core Engineering & Safety Highlights
- **Subprocess Isolation (`shell=False`):** `safety_guard.py` enforces a strict binary allow-list (`lscpu`, `lsblk`, `free`, `lspci`, `dmidecode`) with argument sanitization and blocks command injection attempts.
- **Output Normalization:** Deterministic Python parsers convert raw command text into typed schemas before reasoning.
- **Root/Permission Fallback:** Gracefully falls back to `/proc/meminfo` and `/sys/class/dmi/id/...` in unprivileged environments.
- **Anti-Hallucination Grounding:** Explicitly says *"I don't know based on the available system inspection data"* when asked about unsupported specs (e.g. screen refresh rate).
- **Conversational Memory:** Handles multi-turn follow-ups (*"and what about the GPU?"*).

---

## 🚀 Quickstart & Localhost Execution

### 1. Run Both Web Applications Concurrently
```bash
python run_all.py
```
- **Project 1 (AgentVerse):** [http://localhost:8001](http://localhost:8001)
- **Project 2 (Hardware Assistant):** [http://localhost:8002](http://localhost:8002)

### 2. Interactive Terminal CLI (Hardware Assistant)
```bash
cd project-2-linux-hardware-assistant
python cli.py
```

### 3. Run Automated Test Suite
```bash
python test_all.py
```
