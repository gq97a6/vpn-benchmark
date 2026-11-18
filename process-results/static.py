"""Static definitions, thresholds, column keys, and scenario groupings for results processing."""

from pathlib import Path

project_dir = Path(__file__).resolve().parent

thresholds = {
    "down": 10,
    "up": 10,
    "cpu": 5,
}

key_cols = ["vpn", "impair", "bandwidth", "burst", "delay", "jitter", "loss", "cpu_freq", "core_count"]

data_cols = [
    col + suf
    for col in ["down", "up", "cpu", "efficiency"]
    for suf in ["_mean", "_rsd", "_sd"]
]

cols_to_keep = key_cols + data_cols

# Each group selects experiments by a subset of key fields.
experiment_groups = {
    "control_no_tc": {
        "mask": {"impair": False},
        "cols": ["vpn"],
        "desc": "control without tc"
    },
    "control_tc": {
        "mask": {"impair": True, "bandwidth": 0},
        "cols": ["vpn"],
        "desc": "control with tc"
    },
    "lan10": {
        "mask": {"bandwidth": 10000},
        "cols": ["vpn"],
        "desc": "LAN 10G"
    },
    "wan1": {
        "mask": {"bandwidth": 1000, "delay": 5, "core_count": 4},
        "cols": ["vpn"],
        "desc": "WAN 1G"
    },
    "wwan200": {
        "mask": {"bandwidth": 200, "core_count": 4},
        "cols": ["vpn"],
        "desc": "WWAN 200mbit"
    },
    "wwan200_weak": {
        "mask": {"bandwidth": 200, "core_count": 2},
        "cols": ["vpn"],
        "desc": "WWAN 200mbit | Dual-Core Compute-Restricted"
    },
    "wan1_weak": {
        "mask": {"bandwidth": 1000, "delay": 5, "core_count": 2},
        "cols": ["vpn"],
        "desc": "WAN 1G | Dual-Core Compute-Restricted"
    },
    "wan1_starved": {
        "mask": {"bandwidth": 1000, "delay": 5, "core_count": 1},
        "cols": ["vpn"],
        "desc": "WAN 1G | Single-Core Compute-Restricted"
    },
    "lfn1": {
        "mask": {"bandwidth": 1000, "delay": 100},
        "cols": ["vpn"],
        "desc": "LFN 1G"
    },
}