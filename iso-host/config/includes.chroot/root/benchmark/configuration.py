REPEAT_COUNT = 25
RESULTS_FOLDER = "/benchmark-results"

ROUTER_SERVER_LAN_INTERFACE = "lan0"
ROUTER_CLIENT_LAN_INTERFACE = "lan1"

# Cores pinned for client and server
GUEST_CAPPED_CORES = "8-15"

ROUTER_SSH = "router"
SERVER_SSH = "server"
CLIENT_SSH = "client"

IP_SERVER = {
    "wireguard": "10.10.0.1",
    "nebula": "10.20.0.1",
    "openvpn": "10.30.0.1",
    "none": "10.0.10.2",
}

IP_CLIENT = {
    "wireguard": "10.10.0.2",
    "nebula": "10.20.0.2",
    "openvpn": "10.30.0.2",
    "none": "10.0.20.2",
}

BASELINE = {
    "vpn": "none",
    "bandwidth": "0", # unlimited
    "burst": "10mbit",
    "delay": "0ms",
    "jitter": "0ms",
    "loss": "0%",
    "cpu_freq": "4.0GHz",
    "core_count": 4,
}
