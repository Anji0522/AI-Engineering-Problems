"""
Security and Safety Guard for Linux Hardware Assistant.
Enforces strict allow-listing, read-only guarantees, argument sanitization,
and eliminates any possibility of arbitrary shell execution.
"""

import os
import re
from typing import List, Tuple, Set, Optional

# Strictly allowed commands and their authorized flags
ALLOWED_COMMANDS = {
    "lscpu": {
        "allowed_flags": {"-J", "--json", "-e", "-p", "-x"},
        "max_args": 2
    },
    "lsblk": {
        "allowed_flags": {"-J", "--json", "-d", "-o", "NAME,SIZE,TYPE,TRAN,MODEL,ROTA,MOUNTPOINT", "-b", "-m"},
        "max_args": 5
    },
    "free": {
        "allowed_flags": {"-b", "-m", "-g", "-h", "--mega", "--giga", "-w"},
        "max_args": 2
    },
    "lspci": {
        "allowed_flags": {"-nn", "-mm", "-k", "-v", "-vmm"},
        "max_args": 3
    },
    "dmidecode": {
        "allowed_flags": {"-t", "memory", "bios", "system", "baseboard", "processor", "chassis", "16", "17", "2", "4"},
        "max_args": 4
    }
}

# Permitted read-only virtual filesystem paths (procfs & sysfs)
ALLOWED_FS_PATHS: Set[str] = {
    "/proc/cpuinfo",
    "/proc/meminfo",
    "/proc/version",
    "/sys/class/dmi/id/sys_vendor",
    "/sys/class/dmi/id/product_name",
    "/sys/class/dmi/id/product_version",
    "/sys/class/dmi/id/bios_version",
    "/sys/class/dmi/id/board_vendor",
    "/sys/class/dmi/id/board_name"
}

DISALLOWED_CHARACTERS = re.compile(r"[;&|><`$\\\'\"\(\)\{\}\n\r\t]")

class SecurityException(Exception):
    pass

class SafetyGuard:
    @staticmethod
    def validate_cli_command(cmd_args: List[str]) -> Tuple[str, List[str]]:
        """
        Validates that the command arguments strictly match the allow-list.
        Returns the sanitized (binary, clean_args) tuple.
        Raises SecurityException on any violation.
        """
        if not cmd_args or not isinstance(cmd_args, list):
            raise SecurityException("Command must be a non-empty list of string tokens.")

        # Check for banned shell characters in any argument
        for token in cmd_args:
            if DISALLOWED_CHARACTERS.search(token):
                raise SecurityException(f"Illegal character detected in argument: {token}")

        binary = os.path.basename(cmd_args[0]).lower()

        if binary not in ALLOWED_COMMANDS:
            raise SecurityException(f"Command '{binary}' is not permitted. Only read-only hardware inspection tools are allow-listed.")

        spec = ALLOWED_COMMANDS[binary]
        flags = cmd_args[1:]

        if len(flags) > spec["max_args"]:
            raise SecurityException(f"Too many arguments for '{binary}'. Maximum allowed: {spec['max_args']}")

        for flag in flags:
            if flag not in spec["allowed_flags"]:
                raise SecurityException(f"Argument '{flag}' is not in the strict allow-list for '{binary}'.")

        return binary, flags

    @staticmethod
    def validate_fs_path(path: str) -> str:
        """
        Validates that the file path is an approved read-only procfs/sysfs path.
        Rejects directory traversal (..) or arbitrary files.
        """
        # Normalize and resolve path
        norm_path = os.path.normpath(path)
        if ".." in norm_path:
            raise SecurityException("Directory traversal (..) is strictly prohibited.")

        if norm_path not in ALLOWED_FS_PATHS:
            raise SecurityException(f"Direct reading of path '{path}' is not allow-listed. Only safe hardware telemetry paths permitted.")

        return norm_path
