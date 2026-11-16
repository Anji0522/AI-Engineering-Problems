#!/usr/bin/env python3
"""
Interactive Terminal CLI for Linux Hardware Q&A Assistant.
Run: python cli.py
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

from assistant_agent import HardwareAssistantAgent
from hardware_reader import SystemHardwareReader

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def main():
    reader = SystemHardwareReader()
    agent = HardwareAssistantAgent(reader=reader)

    mode = "Live Linux Host" if not reader.use_mock else "High-Fidelity Linux Simulation (Dell XPS 15 9520)"

    print(f"\n{BOLD}{CYAN}========================================================================{RESET}")
    print(f"{BOLD}{GREEN}  🐧 Linux Hardware Q&A Assistant (Problem 2){RESET}")
    print(f"  Target Environment: {YELLOW}{mode}{RESET}")
    print(f"  Security: {GREEN}Strict Read-Only Allow-Listing & Subprocess Isolation{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}")
    print("Ask any hardware question in natural language. Type 'exit' or 'quit' to end.\n")
    print(f"{BOLD}Sample prompts you can try:{RESET}")
    print(f"  1. {YELLOW}\"Can I add more RAM, and how much?\"{RESET}")
    print(f"  2. {YELLOW}\"How much RAM do I have?\"{RESET}")
    print(f"  3. {YELLOW}\"Is my SSD NVMe?\"{RESET}")
    print(f"  4. {YELLOW}\"and what about the GPU?\"{RESET} (Follow-up)")
    print(f"  5. {YELLOW}\"What is my screen refresh rate?\"{RESET} (Tests anti-hallucination refusal)")
    print("-" * 72 + "\n")

    while True:
        try:
            user_input = input(f"{BOLD}You > {RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n{GREEN}Goodbye!{RESET}")
                break

            print(f"\n{CYAN}🔍 Inspecting hardware telemetry...{RESET}")
            res = agent.answer_query(user_input)

            # Display tool calls
            print(f"{BOLD}🛠️ Tools Invoked:{RESET} {', '.join(res['selected_tools'])}")
            for ex in res["tool_executions"]:
                print(f"  └─ Executed: {YELLOW}`{ex['command']}`{RESET} (Exit Code: {ex['exit_code']})")

            # Display final grounded answer
            print(f"\n{BOLD}{GREEN}Assistant >{RESET} {res['answer']}\n")
            print("-" * 72)

        except (KeyboardInterrupt, EOFError):
            print(f"\n{GREEN}Session ended.{RESET}")
            break

if __name__ == "__main__":
    main()
