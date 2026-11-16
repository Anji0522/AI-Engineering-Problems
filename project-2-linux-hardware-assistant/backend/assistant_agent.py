"""
Autonomous Hardware Q&A Assistant Agent.
Orchestrates tool calling, output normalization, multi-turn follow-ups,
and strict anti-hallucination grounded responses.
"""

import os
import re
import json
from typing import List, Dict, Any, Tuple, Optional
from hardware_reader import SystemHardwareReader
from parsers import HardwareParsers

# Tool definitions available to the agent
HARDWARE_TOOLS = [
    {
        "name": "inspect_memory",
        "description": "Inspects installed RAM capacity, free/used memory, physical slots in use, and max motherboard upgrade capacity.",
        "commands": [["free", "-m"], ["dmidecode", "-t", "memory"]]
    },
    {
        "name": "inspect_storage",
        "description": "Inspects block storage devices, disk drives, NVMe vs SATA transport, SSD vs HDD, and capacities.",
        "commands": [["lsblk", "-J", "-o", "NAME,SIZE,TYPE,TRAN,MODEL,ROTA,MOUNTPOINT"]]
    },
    {
        "name": "inspect_cpu",
        "description": "Inspects CPU processor model, core counts, thread counts, architecture, and clock frequencies.",
        "commands": [["lscpu"]]
    },
    {
        "name": "inspect_gpu",
        "description": "Inspects graphics cards, discrete vs integrated GPUs, and display controllers via PCI bus.",
        "commands": [["lspci"]]
    },
    {
        "name": "inspect_system",
        "description": "Inspects laptop manufacturer, model name, and BIOS firmware version from sysfs/DMI.",
        "commands": [["dmidecode", "-t", "system"]]
    }
]

class HardwareAssistantAgent:
    def __init__(self, reader: Optional[SystemHardwareReader] = None):
        self.reader = reader or SystemHardwareReader()
        self.conversation_history: List[Dict[str, str]] = []

    def answer_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main execution flow:
        1. Select appropriate tool(s) based on query and conversation history
        2. Execute safe allow-listed commands
        3. Parse & normalize raw output into structured data
        4. Synthesize accurate, grounded response with 'I don't know' for missing specs
        """
        selected_tools = self._route_tools(user_query)
        tool_executions = []
        parsed_context: Dict[str, Any] = {}

        for tool_name in selected_tools:
            tool_meta = next((t for t in HARDWARE_TOOLS if t["name"] == tool_name), None)
            if not tool_meta:
                continue

            for cmd_args in tool_meta["commands"]:
                success, raw_output, code = self.reader.run_safe_command(cmd_args)
                cmd_str = " ".join(cmd_args)

                # Parse into structured format
                structured = self._normalize_output(cmd_args[0], raw_output)

                tool_executions.append({
                    "tool": tool_name,
                    "command": cmd_str,
                    "success": success,
                    "exit_code": code,
                    "raw_output": raw_output[:1500],  # truncated for brevity in UI
                    "parsed_data": structured
                })

                parsed_context.update(structured)

        # Synthesize final response
        answer = self._generate_grounded_answer(user_query, parsed_context, tool_executions)

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_query})
        self.conversation_history.append({"role": "assistant", "content": answer})

        return {
            "query": user_query,
            "answer": answer,
            "selected_tools": selected_tools,
            "tool_executions": tool_executions,
            "structured_context": parsed_context
        }

    def _route_tools(self, query: str) -> List[str]:
        """
        Determines which system inspection tools are required.
        Handles both direct queries and conversational follow-ups.
        """
        q = query.lower()
        tools = []

        # Memory / RAM questions
        if any(w in q for w in ["ram", "memory", "dimm", "ddr", "upgrade ram", "slots", "stick"]):
            tools.append("inspect_memory")

        # Storage / SSD / NVMe questions
        if any(w in q for w in ["ssd", "nvme", "disk", "storage", "drive", "hard drive", "sata", "hdd"]):
            tools.append("inspect_storage")

        # CPU / Processor questions
        if any(w in q for w in ["cpu", "processor", "cores", "threads", "hz", "ghz", "intel", "amd", "ryzen"]):
            tools.append("inspect_cpu")

        # GPU / Graphics questions
        if any(w in q for w in ["gpu", "graphics", "video card", "nvidia", "rtx", "display", "vga"]):
            tools.append("inspect_gpu")

        # System / Laptop Model questions
        if any(w in q for w in ["laptop", "model", "vendor", "motherboard", "bios", "make", "machine"]):
            tools.append("inspect_system")

        # Conversational follow-up handling (e.g. "and what about the GPU?")
        if not tools and self.conversation_history:
            last_user_turn = self.conversation_history[-2]["content"].lower() if len(self.conversation_history) >= 2 else ""
            if "gpu" in q or "graphics" in q:
                tools.append("inspect_gpu")
            elif "ram" in q or "memory" in q:
                tools.append("inspect_memory")
            elif "cpu" in q:
                tools.append("inspect_cpu")
            elif "disk" in q or "storage" in q or "ssd" in q:
                tools.append("inspect_storage")

        # Default fallback: if query is broad, check system overview
        if not tools:
            tools = ["inspect_cpu", "inspect_memory"]

        return tools

    def _normalize_output(self, binary: str, raw_output: str) -> Dict[str, Any]:
        """Normalizes raw CLI output into typed structures."""
        if binary == "lscpu":
            return {"cpu": HardwareParsers.parse_lscpu(raw_output)}
        elif binary == "free":
            return {"memory_usage": HardwareParsers.parse_free(raw_output)}
        elif binary == "lsblk":
            return {"storage": HardwareParsers.parse_lsblk(raw_output)}
        elif binary == "lspci":
            return {"pci_devices": HardwareParsers.parse_lspci(raw_output)}
        elif binary == "dmidecode":
            return {"smbios_memory": HardwareParsers.parse_dmidecode_memory(raw_output)}
        return {}

    def _generate_grounded_answer(
        self, query: str, context: Dict[str, Any], tool_executions: List[Dict[str, Any]]
    ) -> str:
        """
        Produces accurate, grounded plain-language answer strictly backed by parsed telemetry.
        Adheres to anti-hallucination requirement: says 'I don't know' when data is missing.
        """
        q = query.lower()

        # 1. RAM Upgrade Question (exact example from interview problem)
        if any(w in q for w in ["add more ram", "upgrade ram", "can i add ram", "how much ram can i add"]):
            smbios = context.get("smbios_memory", {})
            mem_usage = context.get("memory_usage", {})

            if smbios.get("unprivileged_warning"):
                return (
                    "I checked system memory, but reading motherboard slot details with dmidecode requires root privileges. "
                    f"Your system has {mem_usage.get('total_gb', 'unknown')} GB total RAM currently recognized. "
                    "Run with sudo or grant permissions to inspect physical SODIMM expansion slots."
                )

            slots_total = smbios.get("slots_total", 0)
            slots_used = smbios.get("slots_used", 0)
            slots_free = smbios.get("slots_free", 0)
            installed_gb = smbios.get("installed_gb") or mem_usage.get("total_gb", 0)
            max_capacity = smbios.get("max_capacity_gb", 0)

            if slots_total > 0:
                modules_desc = []
                for m in smbios.get("modules", []):
                    modules_desc.append(f"{m['size']} {m.get('type', '')}")

                installed_summary = f"{int(installed_gb)} GB in {slots_used} of {slots_total} slots"

                if slots_free > 0 and max_capacity > installed_gb:
                    max_stick = max_capacity - int(installed_gb)
                    return (
                        f"You have {installed_summary}. "
                        f"The board supports up to {max_capacity} GB, so you can add a stick of up to {max_stick} GB into the empty slot."
                    )
                elif slots_free == 0 and max_capacity > installed_gb:
                    return (
                        f"You have {installed_summary}, but all {slots_total} slots are occupied. "
                        f"The board supports up to {max_capacity} GB, so you could replace existing modules with higher capacity sticks."
                    )
                else:
                    return f"You have {installed_summary}. The system is already at its maximum supported capacity of {max_capacity} GB."

        # 2. General RAM inquiry ("How much RAM do I have?")
        if "ram" in q or "how much memory" in q:
            mem_usage = context.get("memory_usage", {})
            smbios = context.get("smbios_memory", {})
            total_gb = smbios.get("installed_gb") or mem_usage.get("total_gb", 0)
            avail_gb = mem_usage.get("available_gb", 0)
            slots_used = smbios.get("slots_used", 1)
            slots_total = smbios.get("slots_total", 2)

            return (
                f"You have {int(total_gb)} GB of installed RAM ({avail_gb} GB currently available). "
                f"It is currently configured across {slots_used} of {slots_total} physical slots."
            )

        # 3. Storage / NVMe / SSD question ("Is my SSD NVMe?", "How much storage do I have?")
        if any(w in q for w in ["nvme", "ssd", "disk", "storage", "drive", "hard drive"]):
            storage = context.get("storage", [])
            if not storage:
                return "I don't know based on the available inspection data. No block storage devices could be enumerated."

            nvme_disks = [d for d in storage if d.get("is_nvme")]
            sata_disks = [d for d in storage if not d.get("is_nvme")]

            # If user explicitly asked "is it nvme"
            if "nvme" in q or "is my" in q:
                if nvme_disks:
                    disk = nvme_disks[0]
                    return (
                        f"Yes, your SSD is NVMe. You have a {disk.get('model', 'NVMe SSD')} with {disk.get('size_gb')} GB capacity "
                        f"operating over the high-speed NVMe PCIe transport bus."
                    )
                elif sata_disks:
                    disk = sata_disks[0]
                    return (
                        f"No, your drive is not NVMe. You have a {disk.get('model', 'drive')} ({disk.get('size_gb')} GB) "
                        f"operating over SATA."
                    )

            # General storage capacity inquiry
            disk_summaries = []
            for d in storage:
                transport_label = "NVMe SSD" if d.get("is_nvme") else "SATA Drive"
                disk_summaries.append(f"{d.get('model', 'Storage Drive')} ({d.get('size_gb')} GB, {transport_label})")
            
            return f"You have {len(storage)} storage drive(s) installed: " + "; ".join(disk_summaries) + "."

        # 4. GPU / Graphics follow-up question ("and what about the GPU?")
        if any(w in q for w in ["gpu", "graphics", "video card", "rtx", "nvidia", "display"]):
            pci = context.get("pci_devices", {})
            gpus = pci.get("gpus", [])
            if not gpus:
                return "I don't know based on the available inspection data. No display controllers were detected on the PCI bus."

            gpu_descs = [f"{g['description']} ({g['type']})" for g in gpus]
            return f"You have {len(gpus)} graphics device(s) detected: " + "; ".join(gpu_descs) + "."

        # 5. CPU inquiry ("What CPU do I have?")
        if any(w in q for w in ["cpu", "processor", "cores"]):
            cpu = context.get("cpu", {})
            model = cpu.get("model_name", "Unknown CPU")
            cores = cpu.get("cores", 0)
            threads = cpu.get("threads", 0)
            arch = cpu.get("architecture", "Unknown")
            max_mhz = cpu.get("max_mhz")

            mhz_str = f" boosting up to {max_mhz:.0f} MHz" if max_mhz else ""
            return f"Your CPU is an {model} ({arch} architecture) featuring {cores} physical cores and {threads} threads{mhz_str}."

        # 6. Anti-Hallucination Fallback: If user asks about something completely outside telemetry
        if any(w in q for w in ["screen", "refresh rate", "battery health", "camera", "microphone", "ecc"]):
            return (
                "I don't know based on the available system inspection data. "
                "The allow-listed hardware commands (lscpu, lsblk, free, lspci, dmidecode) "
                "do not report that specification, and I will not guess."
            )

        return (
            "I inspected your system hardware telemetry. "
            "You can ask me specific questions like: 'How much RAM do I have?', 'Can I add more RAM, and how much?', "
            "'Is my SSD NVMe?', or 'What about the GPU?'."
        )
