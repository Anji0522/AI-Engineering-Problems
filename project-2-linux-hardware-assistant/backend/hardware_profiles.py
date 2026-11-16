"""
Hardware simulation presets for testing and cross-platform compatibility.
Allows full validation on Windows, macOS, or unprivileged containers,
mirroring real Linux sysfs, procfs, and command outputs.
"""

from typing import Dict, Any

DELL_XPS_15_PROFILE: Dict[str, str] = {
    "lscpu": """Architecture:             x86_64
  CPU op-mode(s):         32-bit, 64-bit
  Address sizes:          39 bits physical, 48 bits virtual
  Byte Order:             Little Endian
CPU(s):                   20
  On-line CPU(s) list:    0-19
Vendor ID:                GenuineIntel
  Model name:             12th Gen Intel(R) Core(TM) i7-12700H
    CPU family:           6
    Model:                154
    Thread(s) per core:   2
    Core(s) per socket:   14
    Socket(s):            1
    Stepping:             3
    CPU max MHz:          4700.0000
    CPU min MHz:          400.0000
Virtualization features:  
  Virtualization:         VT-x
Caches (sum of all):      
  L1d:                    544 KiB (14 instances)
  L1i:                    704 KiB (14 instances)
  L2:                     11.5 MiB (5 instances)
  L3:                     24 MiB (1 instance)""",

    "free_m": """               total        used        free      shared  buff/cache   available
Mem:           15820        4120        7240         512        4460       11188
Swap:           8192           0        8192""",

    "lsblk_json": """{
   "blockdevices": [
      {
         "name": "nvme0n1",
         "size": "1000204886016",
         "type": "disk",
         "tran": "nvme",
         "model": "Samsung SSD 980 PRO 1TB",
         "rota": false,
         "mountpoint": null,
         "children": [
            {
               "name": "nvme0n1p1",
               "size": "536870912",
               "type": "part",
               "tran": null,
               "model": null,
               "rota": false,
               "mountpoint": "/boot/efi"
            },
            {
               "name": "nvme0n1p2",
               "size": "999666974720",
               "type": "part",
               "tran": null,
               "model": null,
               "rota": false,
               "mountpoint": "/"
            }
         ]
      }
   ]
}""",

    "lspci": """00:00.0 Host bridge: Intel Corporation 12th Gen Core Processor Host Bridge/DRAM Registers (rev 02)
00:01.0 PCI bridge: Intel Corporation 12th Gen Core Processor PCI Express x16 Controller (rev 02)
00:02.0 VGA compatible controller: Intel Corporation Alder Lake-P Integrated Graphics Controller (rev 0c)
01:00.0 3D controller: NVIDIA Corporation GA107M [GeForce RTX 3050 Ti Mobile] (rev a1)
02:00.0 Non-Volatile memory controller: Samsung Electronics Co Ltd NVMe SSD Controller PM9A1/980PRO
00:14.3 Network controller: Intel Corporation Alder Lake-P PCH CNVi WiFi (rev 01)""",

    "dmidecode_memory": """# dmidecode 3.4
Getting SMBIOS data from sysfs.
SMBIOS 3.4.0 present.

Handle 0x002B, DMI type 16, 23 bytes
Physical Memory Array
	Location: System Board
	Use: System Memory
	Error Correction Type: None
	Maximum Capacity: 64 GB
	Error Information Handle: Not Provided
	Number Of Devices: 2

Handle 0x002C, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x002B
	Error Information Handle: Not Provided
	Total Width: 64 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: SODIMM
	Set: None
	Locator: ChannelA-DIMM0
	Bank Locator: BANK 0
	Type: DDR5
	Type Detail: Synchronous Unbuffered (Unregistered)
	Speed: 4800 MT/s
	Manufacturer: Micron
	Serial Number: 2A3B4C5D
	Asset Tag: 9876543210
	Part Number: MTC8C1084S1SC48BA1   
	Rank: 1
	Configured Memory Speed: 4800 MT/s
	Minimum Voltage: 1.1 V
	Maximum Voltage: 1.1 V
	Configured Voltage: 1.1 V

Handle 0x002D, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x002B
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: SODIMM
	Set: None
	Locator: ChannelB-DIMM0
	Bank Locator: BANK 1
	Type: Unknown
	Type Detail: None
	Speed: Unknown
	Manufacturer: Not Specified""",

    "sys_dmi": {
        "sys_vendor": "Dell Inc.",
        "product_name": "XPS 15 9520",
        "bios_version": "1.14.0",
        "board_vendor": "Dell Inc.",
        "board_name": "0HNDT3"
    }
}
