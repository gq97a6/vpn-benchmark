from dataclasses import dataclass, replace
from configuration import BASELINE
import random

@dataclass
class Experiment:
    vpn: str = BASELINE["vpn"]
    impair: bool = True
    bandwidth: str = BASELINE["bandwidth"]
    burst: str = BASELINE["burst"]
    delay: str = BASELINE["delay"]
    jitter: str = BASELINE["jitter"]
    loss: str = BASELINE["loss"]
    cpu_freq: str = BASELINE["cpu_freq"]
    core_count: int = BASELINE["core_count"]

def map_experiments(experiments: list[Experiment], repeat_count: int) -> list[Experiment]:
    exps = [
        replace(exp, vpn=vpn)
        for exp in experiments
        for _ in range(repeat_count)
        for vpn in ["none", "wireguard", "nebula", "openvpn"]
    ]

    random.shuffle(exps)
    return exps

flat_experiments = [
    # no tc, no netem - raw wire speed
    Experiment(impair=False),
    # netem only, zero impairment - tc overhead
    Experiment(impair=True),

    # strong box on LAN 10G - max VPN throughput
    Experiment(bandwidth="10000mbit", burst="100mbit", delay="0ms", jitter="0ms", loss="0%"),

    # strong box on fiber 1G - throughput on a good link
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="5ms", jitter="1ms", loss="0.01%"),

    # strong box on 5G - throughput and stability on a lossy mobile link
    Experiment(bandwidth="200mbit", burst="2mbit", delay="30ms", jitter="15ms", loss="0.5%"),

    # weak box on 5G - does weak hardware degrade worse on a lossy link
    Experiment(bandwidth="200mbit", burst="2mbit", delay="30ms", jitter="15ms", loss="0.5%", core_count=2, cpu_freq="2.0GHz"),

    # weak box on fiber 1G - can a weak box fill a good link
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="5ms", jitter="1ms", loss="0.01%", core_count=2, cpu_freq="2.0GHz"),

    # starved box on fiber 1G - compute floor
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="5ms", jitter="1ms", loss="0.01%", core_count=1, cpu_freq="1.5GHz"),

    # strong box on long-haul 100ms - high-latency throughput
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="100ms", jitter="1ms", loss="0.1%"),
]