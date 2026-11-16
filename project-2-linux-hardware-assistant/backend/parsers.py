"""
Output Parsers and Normalizers for Linux Hardware Assistant.
Converts raw command and sysfs output into strongly-typed structured dictionaries/schemas.
"""

import re
import json
from typing import Dict, Any, List, Optional

class HardwareParsers:

    @staticmethod
    def parse_lscpu(raw_text: str) -> Dict[str, Any]:
        """Parses lscpu output into a structured CPU telemetry object."""
        cpu_info: Dict[str, Any] = {
            "model_name": "Unknown CPU",
            "architecture": "Unknown",
            "cores": 0,
            "threads": 0,
            "sockets": 1,
            "threads_per_core": 1,
            "max_mhz": None,
            "min_mhz": None,
            "virtualization": None
        }

        for line in raw_text.splitlines():
            if ":" not in line:
                continue
            key, val = [p.strip() for p in line.split(":", 1)]
            k_lower = key.lower()

            if "model name" in k_lower:
                cpu_info["model_name"] = val
            elif k_lower == "architecture":
                cpu_info["architecture"] = val
            elif k_lower == "cpu(s)":
                try:
                    cpu_info["threads"] = int(val)
                except ValueError:
                    pass
            elif "thread(s) per core" in k_lower:
                try:
                    cpu_info["threads_per_core"] = int(val)
                except ValueError:
                    pass
            elif "core(s) per socket" in k_lower:
                try:
                    cpu_info["cores"] = int(val)
                except ValueError:
                    pass
            elif "socket(s)" in k_lower:
                try:
                    cpu_info["sockets"] = int(val)
                except ValueError:
                    pass
            elif "cpu max mhz" in k_lower:
                try:
                    cpu_info["max_mhz"] = float(val)
                except ValueError:
                    pass
            elif "virtualization" in k_lower:
                cpu_info["virtualization"] = val

        return cpu_info

    @staticmethod
    def parse_free(raw_text: str) -> Dict[str, Any]:
        """Parses free -m output."""
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        mem_data = {"total_mb": 0, "used_mb": 0, "available_mb": 0, "swap_total_mb": 0}

        for line in lines:
            parts = line.split()
            if parts[0].startswith("Mem:"):
                try:
                    mem_data["total_mb"] = int(parts[1])
                    mem_data["used_mb"] = int(parts[2])
                    mem_data["available_mb"] = int(parts[6]) if len(parts) > 6 else int(parts[3])
                except (ValueError, IndexError):
                    pass
            elif parts[0].startswith("Swap:"):
                try:
                    mem_data["swap_total_mb"] = int(parts[1])
                except (ValueError, IndexError):
                    pass

        mem_data["total_gb"] = round(mem_data["total_mb"] / 1024.0, 1)
        mem_data["available_gb"] = round(mem_data["available_mb"] / 1024.0, 1)
        return mem_data

    @staticmethod
    def parse_lsblk(raw_text: str) -> List[Dict[str, Any]]:
        """Parses lsblk JSON or column format into structured disk list."""
        disks = []
        try:
            # Try JSON first
            data = json.loads(raw_text)
            devices = data.get("blockdevices", [])
            for dev in devices:
                # Top level disks
                size_str = dev.get("size", "0")
                try:
                    size_gb = round(int(size_str) / (1024 ** 3), 1)
                except ValueError:
                    size_gb = size_str

                disks.append({
                    "name": dev.get("name"),
                    "model": dev.get("model") or "Generic Storage",
                    "transport": (dev.get("tran") or "sata").lower(),
                    "is_nvme": (dev.get("tran") or "").lower() == "nvme" or "nvme" in (dev.get("name") or "").lower(),
                    "is_ssd": not dev.get("rota", True),
                    "size_gb": size_gb,
                    "partitions_count": len(dev.get("children", []))
                })
        except json.JSONDecodeError:
            # Fallback simple line parsing
            for line in raw_text.splitlines():
                if "disk" in line.lower():
                    is_nvme = "nvme" in line.lower()
                    disks.append({
                        "name": line.split()[0],
                        "model": "Generic Disk",
                        "transport": "nvme" if is_nvme else "sata",
                        "is_nvme": is_nvme,
                        "is_ssd": True,
                        "size_gb": "Unknown",
                        "partitions_count": 1
                    })

        return disks

    @staticmethod
    def parse_lspci(raw_text: str) -> Dict[str, Any]:
        """Parses lspci to identify GPU and key peripherals."""
        gpus = []
        nvme_controllers = []

        for line in raw_text.splitlines():
            line_lower = line.lower()
            if "vga compatible" in line_lower or "3d controller" in line_lower or "display controller" in line_lower:
                # Extract device description
                parts = line.split(":", 2)
                desc = parts[-1].strip() if len(parts) >= 3 else line
                is_dedicated = "nvidia" in line_lower or "amd" in line_lower and "radeon" in line_lower
                gpus.append({
                    "description": desc,
                    "is_dedicated": is_dedicated,
                    "type": "Discrete GPU" if is_dedicated else "Integrated GPU"
                })
            elif "non-volatile memory" in line_lower or "nvme" in line_lower:
                nvme_controllers.append(line.strip())

        return {
            "gpus": gpus,
            "nvme_controllers": nvme_controllers
        }

    @staticmethod
    def parse_dmidecode_memory(raw_text: str) -> Dict[str, Any]:
        """
        Parses dmidecode SMBIOS Type 16 (Physical Memory Array)
        and Type 17 (Memory Device).
        Extracts slot counts, installed modules, max board capacity, and upgradeability.
        """
        result = {
            "slots_total": 0,
            "slots_used": 0,
            "slots_free": 0,
            "installed_gb": 0,
            "max_capacity_gb": 0,
            "modules": [],
            "can_add_ram": False,
            "max_additional_gb": 0,
            "unprivileged_warning": False
        }

        # Check if dmidecode was rejected due to permissions
        if "permission denied" in raw_text.lower() or "operation not permitted" in raw_text.lower():
            result["unprivileged_warning"] = True
            return result

        # Max Capacity from Type 16
        cap_match = re.search(r"Maximum Capacity:\s*(\d+)\s*(GB|MB)", raw_text, re.IGNORECASE)
        if cap_match:
            cap_val = int(cap_match.group(1))
            unit = cap_match.group(2).upper()
            result["max_capacity_gb"] = cap_val if unit == "GB" else round(cap_val / 1024)

        devices = raw_text.split("Memory Device")
        # First element is header/Type 16
        for dev_block in devices[1:]:
            result["slots_total"] += 1
            size_match = re.search(r"Size:\s*([^\n\r]+)", dev_block)
            type_match = re.search(r"Type:\s*([^\n\r]+)", dev_block)
            speed_match = re.search(r"Speed:\s*([^\n\r]+)", dev_block)
            locator_match = re.search(r"Locator:\s*([^\n\r]+)", dev_block)

            size_str = size_match.group(1).strip() if size_match else "Unknown"
            mod_type = type_match.group(1).strip() if type_match else "Unknown"
            speed = speed_match.group(1).strip() if speed_match else "Unknown"
            locator = locator_match.group(1).strip() if locator_match else f"Slot {result['slots_total']}"

            if "no module" in size_str.lower() or size_str == "0":
                result["slots_free"] += 1
            else:
                result["slots_used"] += 1
                # Parse installed size
                gb_match = re.search(r"(\d+)\s*(GB|MB)", size_str, re.IGNORECASE)
                if gb_match:
                    val = int(gb_match.group(1))
                    unit = gb_match.group(2).upper()
                    result["installed_gb"] += val if unit == "GB" else round(val / 1024)

                result["modules"].append({
                    "locator": locator,
                    "size": size_str,
                    "type": mod_type,
                    "speed": speed
                })

        # Upgrade potential
        if result["slots_free"] > 0 and result["max_capacity_gb"] > result["installed_gb"]:
            result["can_add_ram"] = True
            result["max_additional_gb"] = result["max_capacity_gb"] - result["installed_gb"]

        return result
