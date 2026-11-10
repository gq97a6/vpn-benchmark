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
        "desc": "Control: no tc at all (raw wire speed)"
    },
    "control_netem": {
        "mask": {"impair": True, "bandwidth": 0},
        "cols": ["vpn"],
        "desc": "Control: netem only, zero impairment"
    },
    "lan_10g": {
        "mask": {"bandwidth": 10000},
        "cols": ["vpn"],
        "desc": "Strong on LAN 10G"
    },
    "fiber_1g": {
        "mask": {"bandwidth": 1000, "delay": 5, "core_count": 4},
        "cols": ["vpn"],
        "desc": "Strong on fiber 1G"
    },
    "5g": {
        "mask": {"bandwidth": 200, "core_count": 4},
        "cols": ["vpn"],
        "desc": "Strong on 5G"
    },
    "5g_weak": {
        "mask": {"bandwidth": 200, "core_count": 2},
        "cols": ["vpn"],
        "desc": "Weak (2c/2GHz) on 5G"
    },
    "fiber_1g_weak": {
        "mask": {"bandwidth": 1000, "delay": 5, "core_count": 2},
        "cols": ["vpn"],
        "desc": "Weak (2c/2GHz) on fiber 1G"
    },
    "fiber_1g_starved": {
        "mask": {"bandwidth": 1000, "delay": 5, "core_count": 1},
        "cols": ["vpn"],
        "desc": "Starved (1c/1.5GHz) on fiber 1G"
    },
    "long_haul": {
        "mask": {"bandwidth": 1000, "delay": 100},
        "cols": ["vpn"],
        "desc": "Strong on long-haul 100ms"
    },
}