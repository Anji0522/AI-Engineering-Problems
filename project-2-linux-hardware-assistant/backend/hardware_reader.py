"""
System Hardware Inspection Reader.
Executes allow-listed commands safely on Linux, handles permission elevation/fallbacks,
and provides seamless high-fidelity simulation on non-Linux hosts.
"""

import sys
import os
import subprocess
import platform
from typing import Dict, Any, List, Tuple
from safety_guard import SafetyGuard, SecurityException
from hardware_profiles import DELL_XPS_15_PROFILE

class SystemHardwareReader:
    def __init__(self, force_mock: bool = False):
        self.is_linux = platform.system().lower() == "linux"
        self.use_mock = force_mock or not self.is_linux

    def run_safe_command(self, cmd_args: List[str]) -> Tuple[bool, str, int]:
        """
        Validates and executes an allow-listed hardware command.
        Returns: (success: bool, output_or_error: str, return_code: int)
        """
        # 1. Enforce strict safety guard
        try:
            binary, clean_args = SafetyGuard.validate_cli_command(cmd_args)
        except SecurityException as e:
            return False, f"SECURITY REJECTION: {str(e)}", 403

        # 2. Use Simulation Profile if on non-Linux or mock requested
        if self.use_mock:
            return self._mock_command_output(binary, clean_args)

        # 3. Live Linux Execution (shell=False, strict timeout)
        try:
            res = subprocess.run(
                [binary] + clean_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=3.0
            )
            output = res.stdout if res.returncode == 0 else (res.stderr or res.stdout)
            return res.returncode == 0, output.strip(), res.returncode
        except subprocess.TimeoutExpired:
            return False, f"Execution timed out after 3.0s for '{binary}'", 124
        except FileNotFoundError:
            return False, f"Tool '{binary}' is not installed on this system.", 127
        except PermissionError:
            return False, f"Permission denied executing '{binary}'.", 126

    def read_safe_fs(self, path: str) -> Tuple[bool, str]:
        """Reads allow-listed procfs or sysfs virtual paths safely."""
        try:
            safe_path = SafetyGuard.validate_fs_path(path)
        except SecurityException as e:
            return False, f"SECURITY REJECTION: {str(e)}"

        if self.use_mock:
            # Map mock sysfs
            key = os.path.basename(path)
            mock_dmi = DELL_XPS_15_PROFILE["sys_dmi"]
            if key in mock_dmi:
                return True, mock_dmi[key]
            return False, f"Mock file {path} not simulated."

        try:
            with open(safe_path, "r", encoding="utf-8") as f:
                return True, f.read().strip()
        except Exception as e:
            return False, f"Could not read {safe_path}: {e}"

    def _mock_command_output(self, binary: str, args: List[str]) -> Tuple[bool, str, int]:
        """Provides realistic Linux laptop command telemetry for testing and Windows/macOS support."""
        if binary == "lscpu":
            return True, DELL_XPS_15_PROFILE["lscpu"], 0
        elif binary == "free":
            return True, DELL_XPS_15_PROFILE["free_m"], 0
        elif binary == "lsblk":
            return True, DELL_XPS_15_PROFILE["lsblk_json"], 0
        elif binary == "lspci":
            return True, DELL_XPS_15_PROFILE["lspci"], 0
        elif binary == "dmidecode":
            # If asking for memory
            if "memory" in args or "17" in args or "16" in args:
                return True, DELL_XPS_15_PROFILE["dmidecode_memory"], 0
            return True, "SMBIOS data simulated for Dell XPS 15 9520", 0
        return False, f"Command {binary} has no mock implementation.", 1
