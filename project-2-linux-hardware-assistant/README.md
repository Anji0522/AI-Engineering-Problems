# Project 2: Linux Hardware Q&A Assistant

An autonomous local hardware inspection assistant designed for Linux laptops that answers natural language questions accurately using safe, strictly allow-listed read-only system inspection tools (`lscpu`, `lsblk`, `free`, `lspci`, `dmidecode`, `/proc`, `/sys`).

---

## 🎮 Interactive Live Demo Links

When running `python run.py`:

- **Interactive Web UI:** [http://localhost:8002](http://localhost:8002)
- **Interactive OpenAPI / Swagger Docs:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **ReDoc API Reference:** [http://localhost:8002/redoc](http://localhost:8002/redoc)
- **Interactive Terminal CLI:** `python cli.py`

> 💡 **Try These Prompts in the Demo UI:**
> 1. *"Can I add more RAM, and how much?"* $\to$ Inspects memory slots and motherboard capacity limit.
> 2. *"How much RAM do I have?"* $\to$ Checks installed vs currently available memory.
> 3. *"Is my SSD NVMe?"* $\to$ Checks block storage transport bus.
> 4. *"and what about the GPU?"* $\to$ Evaluates multi-turn context and inspects display controllers on PCI bus.
> 5. *"What is my screen refresh rate?"* $\to$ Tests anti-hallucination refusal (*"I don't know"*).

---

## 🎯 Architecture & Safety Engineering Highlights

### 1. Safety & Subprocess Isolation (Interviewer Core Criterion)
- **Zero Arbitrary Shell Execution**: Every system command runs with `shell=False` passing explicit, sanitized string tokens.
- **Strict Allow-Listing**:
  - Binaries strictly restricted to `["lscpu", "lsblk", "free", "lspci", "dmidecode"]`.
  - Flags strictly restricted per tool (e.g. `lsblk` allowed only `-J`, `-o`, `-d`; rejects any unauthorized flags).
  - Prohibits all shell operators: `;`, `&&`, `|`, `>`, `<`, backticks, `$()`, `eval`.
- **Read-Only Virtual Filesystem Access**:
  - Restricts direct procfs/sysfs reads to approved paths (`/proc/cpuinfo`, `/proc/meminfo`, `/sys/class/dmi/id/...`).
  - Directory traversal (`..`) is strictly blocked.

### 2. Output Normalization & Parsers
Raw CLI textual output is passed through deterministic Python parsers (`parsers.py`) before the LLM sees it:
- `parse_dmidecode_memory`: Extracts SMBIOS Type 16 (Physical Memory Array) and Type 17 (Memory Device) into total slots, installed modules, empty slots, maximum board capacity, and upgrade headroom.
- `parse_lsblk`: Parses JSON tree into transport (`nvme` vs `sata`), rotational state (`SSD` vs `HDD`), and mount points.
- `parse_lscpu`: Extracts architecture, physical cores, threads, and clock rates.
- `parse_lspci`: Classifies discrete vs integrated graphics cards.

### 3. Anti-Hallucination Grounding Guarantee
- The reasoning engine answers strictly from normalized telemetry fields.
- **"I don't know" Guarantee**: If a user asks a question about hardware outside the telemetry (e.g., *"What is my screen refresh rate?"* or *"Is my RAM ECC?"* when SMBIOS reports non-ECC), the assistant explicitly responds:
  > *"I don't know based on the available system inspection data. The allow-listed hardware commands do not report that specification, and I will not guess."*

### 4. Cross-Platform & Dual-Mode Execution
- **Live Linux Mode**: Runs live on Ubuntu, Debian, Fedora, Arch, or WSL.
- **Simulation Profile Mode**: Built-in realistic hardware presets (Dell XPS 15 9520 with 16GB RAM in 1 of 2 slots, max 64GB board support, Samsung 980 PRO NVMe SSD, Intel Core i7-12700H, NVIDIA RTX 3050 Ti Mobile) allows immediate out-of-the-box testing and review on Windows and macOS.

---

## 🚀 How to Run

### Option A: Web UI
```bash
python run.py
```
Open **[http://localhost:8002](http://localhost:8002)** in your browser.

### Option B: Terminal CLI
```bash
python cli.py
```
Interactive terminal prompt supporting multi-turn conversation.
