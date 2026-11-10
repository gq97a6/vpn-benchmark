# Automated VPN benchmark

A highly reproducible, KVM-based testbed for benchmarking VPN protocols (Wireguard, Nebula, OpenVPN) under simulated hardware and network constraints. It uses custom Debian Live ISOs, strict CPU pinning, tc network degradation, and cpupower frequency capping to generate isolated metrics.

- Programming language - `Python`
- Tested protocols - `Wireguard`, `Nebula`, `OpenVPN`
- Used benchmark - `iperf3`
- Hypervisor - `KVM/QEMU`, `virsh`
- Network conditions degrading - `tc`
- CPU Clock rate capping - `cpupower`
- Live ISO - `live-build`

## Infrastructure

#### Virtual machines

- `Client`  ⇄ `Router` ⇄ `Server`

#### QEMU Networks

- ``mgmt0`` - Management network for remote control over SSH
- ``lan0`` - LAN network between server and router
- ``lan1`` - LAN network between client and router

| Bridge     | Host interface | Guest interface | IP Address   | MAC Address       |
|------------|----------------|-----------------|--------------|-------------------|
| `br-mgmt0` | →              | →               | 10.0.0.1     | *auto-generated*  |
| →          | `router-mgmt0` | `mgmt0`         | 10.0.0.2     | 52:54:00:00:00:01 |
| →          | `server-mgmt0` | `mgmt0`         | 10.0.0.3     | 52:54:00:00:00:02 |
| →          | `client-mgmt0` | `mgmt0`         | 10.0.0.4     | 52:54:00:00:00:03 |
| `br-lan0`  | →              | →               | *not routed* | *auto-generated*  |
| →          | `router-lan0`  | `lan0`          | 10.0.10.1    | 52:54:00:10:00:01 |
| →          | `server-lan0`  | `lan0`          | 10.0.10.2    | 52:54:00:10:00:02 |
| `br-lan1`  | →              | →               | *not routed* | *auto-generated*  |
| →          | `router-lan1`  | `lan1`          | 10.0.20.1    | 52:54:00:20:00:01 |
| →          | `client-lan1`  | `lan1`          | 10.0.20.2    | 52:54:00:20:00:02 |

#### VPN Networks

| VPN         | Interface | Owner  | IP Address |
|-------------|-----------|--------|------------|
| `Wireguard` |           |        |            |
| →           | `wg0`     | Server | 10.10.0.1  |
| →           | `wg0`     | Client | 10.10.0.2  |
| `Nebula`    |           |        |            |
| →           | `neb0`    | Server | 10.20.0.1  |
| →           | `neb0`    | Client | 10.20.0.2  |
| `OpenVPN`   |           |        |            |
| →           | `tun0`    | Server | 10.30.0.1  |
| →           | `tun0`    | Client | 10.30.0.2  |

#### Precautions

* Diskless system (toram)
* Core pinning for QEMU emulation
* Core isolation for QEMU guests
* CPU performance and frequency scaling disabled
* Randomized list of experiments to avoid thermal carryover
* TCP congestion control set to `bbr` for guests
* Per socket TCP buffers increased for guests
* Client and server virtual machines recreated from scratch for every experiment
* iperf3 runs 4 parallel streams in both directions (forward + reverse), 30 s each, omitting the first 10 s (slow-start) from each average
* Each VPN configured with 1420 MTU

## Experiments

An experiment is a fully defined **link** (rate, burst, delay, jitter, loss) plus the **machine profile** it runs on. Every field is explicit — there is no "unlimited" or undefined state, so each result is measured against a stated condition.

```python
class Experiment:
    vpn: str = BASELINE["vpn"]
    impair: bool = True              # False = no tc at all (raw wire speed)
    bandwidth: str = BASELINE["bandwidth"]
    burst: str = BASELINE["burst"]   # token bucket, ~10ms of the rate
    delay: str = BASELINE["delay"]
    jitter: str = BASELINE["jitter"]
    loss: str = BASELINE["loss"]
    cpu_freq: str = BASELINE["cpu_freq"]
    core_count: int = BASELINE["core_count"]
```

Each experiment is repeated for every protocol (`none`, `wireguard`, `nebula`, `openvpn`) `REPEAT_COUNT` (25) times, in shuffled order.

**Machine profiles**

| Profile | Cores | Frequency |
|---------|-------|-----------|
| strong  | 4     | 4.0 GHz   |
| weak    | 2     | 2.0 GHz   |
| starved | 1     | 1.5 GHz   |

**Links**

| Link      | Rate       | Delay  | Jitter | Loss  | Burst    |
|-----------|------------|--------|--------|-------|----------|
| LAN 10G   | 10000 mbit | 0 ms   | 0 ms   | 0%    | 100 mbit |
| Fiber 1G  | 1000 mbit  | 5 ms   | 1 ms   | 0.01% | 10 mbit  |
| 5G        | 200 mbit   | 30 ms  | 15 ms  | 0.5%  | 2 mbit   |
| Long-haul | 1000 mbit  | 100 ms | 1 ms   | 0.1%  | 10 mbit  |

**Experiment set**

```python
flat_experiments = [
    Experiment(impair=False),  # control: no tc at all (raw wire speed)
    Experiment(impair=True),   # control: netem only, zero impairment

    # strong on LAN 10G - max VPN throughput
    Experiment(bandwidth="10000mbit", burst="100mbit", delay="0ms", jitter="0ms", loss="0%"),
    # strong on fiber 1G - throughput on a good link
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="5ms", jitter="1ms", loss="0.01%"),
    # strong on 5G - lossy mobile link
    Experiment(bandwidth="200mbit", burst="2mbit", delay="30ms", jitter="15ms", loss="0.5%"),
    # weak on 5G - does weak hardware degrade worse on a lossy link
    Experiment(bandwidth="200mbit", burst="2mbit", delay="30ms", jitter="15ms", loss="0.5%", core_count=2, cpu_freq="2.0GHz"),
    # weak on fiber 1G - can a weak box fill a good link
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="5ms", jitter="1ms", loss="0.01%", core_count=2, cpu_freq="2.0GHz"),
    # starved on fiber 1G - compute floor
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="5ms", jitter="1ms", loss="0.01%", core_count=1, cpu_freq="1.5GHz"),
    # strong on long-haul 100ms - high-latency throughput
    Experiment(bandwidth="1000mbit", burst="10mbit", delay="100ms", jitter="1ms", loss="0.1%"),
]
```

## Impairments

Applied on the router's `lan0`/`lan1` interfaces (egress), in two layers:

- **TBF** (root) — emulates the link rate and its buffer.
- **netem** (child, `parent 1:1`) — emulates propagation delay, jitter and packet loss.

```bash
# No bandwidth limit: netem only
tc qdisc add dev {interface} root handle 1: netem delay {delay} {jitter} loss {loss} limit 20000

# Bandwidth limit: TBF (rate) -> netem (delay/jitter/loss)
tc qdisc add dev {interface} root handle 1: tbf rate {bandwidth} burst {burst} latency 50ms
tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay} {jitter} loss {loss} limit 20000
```

CPU impairments (executed on host while nodes are destroyed):
```bash
# Core count
virsh setvcpus client {count} --config

# Frequency
cpupower -c {GUEST_CAPPED_CORES} frequency-set --min {freq}
```

## Methodology

#### 0. Initial steps

Variant A
1. Executing `test.sh`
1. QEMU networks and domains defining and starting

Variant B
1. Booting `host.iso`
1. Isolating cores dedicated for VMs
1. Autostarting QEMU networks and domains

#### 1. Core script initial steps

1. Executing `main.py`.
1. Attempt to disable CPU Boost and to lock CPU governor to performance.
1. Generate list of experiments and dump metadata to root results directory.

#### 2. Steps executed for every experiment

1. Configure core count assigned to VMs
1. Setup specific VPN
1. Configure CPU frequency of cores dedicated to client and server VMs
1. Configure network conditions
1. Begin `sar` monitoring
1. Run benchmarks
1. Stop `sar` monitoring
1. Extract results from client VM to host

## Results format

```txt
root_results_folder/
├── 0/
│   ├── cpu.csv
│   ├── iperf_down.json
│   └── iperf_up.json
├── 1/
│   ├── cpu.csv
│   ├── iperf_down.json
│   └── iperf_up.json
└── metadata.json
```

## Requirements

#### Hardware
- Hardware virtualization
- 20 CPU cores
    - 4 for the host (cores 0–3)
    - 12 for the VMs (cores 4–15, 4 per VM)
    - 4 for QEMU emulator threads (cores 16–19)

> [!TIP]
> To lower CPU core count requirement edit following
> - Core pinning in domain XML configurations
> - Host core isolation configuration in boot parameters in `build.sh` for host ISO
> - `GUEST_CAPPED_CORES` and `BASELINE` in `configuration.py`
> - Experiments in `generate.py`

> [!TIP]
> If you are test running ISO using `Hyper-V` you have to enable nested virtualization
> ```ps
> Set-VMProcessor -VMName <vm> -ExposeVirtualizationExtensions $true
> ```

#### For building the ISO
```bash
apt update && apt install -y live-build
```
1. Build `host.iso` with `build.sh`
1. Boot `host.iso`
1. Run `/root/benchmark/main.py`

#### For testing on current system
```bash
apt update && apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager python3
```
1. Build `guest.iso` with `iso-guest/build.sh` and place it in `/qemu/guest.iso`
1. Clone SSH configuration from `iso-host/config/includes.chroot/root/.ssh`
1. Run `test.sh`

## Manual control

Setup python REPL
```bash
cd benchmark
python3 -i -c "from infrastructure import *; from execute import *; from generate import *; from configuration import *; from shell import *"
```

Use framework
```python
# Prepare host
preconfigure_host()

# Apply specifc set of network impairments
exp1 = Experiment(bandwidth="200mbit", burst="2mbit", delay="30ms", jitter="15ms", loss="0.5%", core_count=2, cpu_freq="2.0GHz")
apply_network_impairments(exp1)

# Lift all network impairments and traffic shaping
lift_network_impairments()

# Define CPU frequency for domains
set_cpu_freq("2.0GHz")

# Create/Recreate VMs with specifc core count
recreate_domains(4)

# Manage VPNs
manage_vpn(vpn="nebula", up=True)
manage_vpn(vpn="openvpn", up=True)
manage_vpn(vpn="wireguard", up=True)

# Run commands on host or guest
shell_on_host(cmd="ls -al", check=False, capture=True)
shell_on_guest(cmd="ls -al", handle="router", check=False, capture=True)
shell_on_guest(cmd="ls -al", handle="server", check=False, capture=True)
shell_on_guest(cmd="ls -al", handle="client", check=False, capture=True)
```

Direct control
```bash
# Step directly into one of the VMs (creds: root/password)
virsh console router
virsh console server
virsh console client

# Server side emulating network impairments without traffic shaping (run it on router)
tc qdisc add dev lan0 root handle 1: netem delay 10ms 3ms loss 0.5% limit 20000

# Client side emulating network impairments with traffic shaping (run it on router)
tc qdisc add dev lan1 root handle 1: tbf rate 1000mbit burst 10mbit latency 50ms
tc qdisc add dev lan1 parent 1:1 handle 10: netem delay 10ms 3ms loss 0.5% limit 20000

# Lift impairments server side (run it on router)
tc qdisc del dev lan0 root

# Start iperf3 server (run it on server)
iperf3 -s

# Run iperf3 test (run it on client)
iperf3 -c 10.10.0.1 -t 30 -O 10 -P 4 # Wiregurad
iperf3 -c 10.20.0.1 -t 30 -O 10 -P 4 # Nebula
iperf3 -c 10.30.0.1 -t 30 -O 10 -P 4 # OpenVPN
iperf3 -c 10.0.10.2 -t 30 -O 10 -P 4 # Direct
```

Example workflow
``` bash
# Step 1. Configure 4 terminals: on host with REPL and one for each domain using `virsh console XYZ`

# In host terminal configure infrastructure
preconfigure_host()
recreate_domains(4)
manage_vpn(vpn="wireguard", up=True)
set_cpu_freq("2.0GHz")

# In router terminal configure network emulation
tc qdisc add dev lan1 root handle 1: tbf rate 1000mbit burst 10mbit latency 50ms
tc qdisc add dev lan1 parent 1:1 handle 10: netem delay 10ms 3ms loss 0.5% limit 20000

# In server terminal start iperf3 server
iperf3 -s

# In client terminal run iperf3 test
iperf3 -c 10.10.0.1 -t 30 -O 10 -P 4
```

## Project structure
```bash
.
├── build.sh # Builds host.iso into root directory of project
├── test.sh # Runs benchmark localy (via QEMU virtual machines)
├── iso-guest
│   ├── build.sh # Builds guest.iso into iso-guest directory
│   └── config # Live-build configuration
│       ├── hooks
│       │   ├── live
│       │   │   └── 0100-fastboot.hook.binary # Configure bootloaders to enable unattended boot
│       │   └── normal
│       │       ├── 0100-access.hook.chroot # Configure access
│       │       └── 0200-networkd.hook.chroot # Enable networkd and disable wait-online
│       └── includes.chroot
│           ├── etc
│           │   ├── nebula # VPN configuration for both sides
│           │   ├── openvpn # VPN configuration for both sides
│           │   ├── wireguard # VPN configuration for both sides
│           │   ├── sysctl.d # Enable routing, configure congestion control and buffers size
│           │   └── systemd/network # Defines all interfaces with static MAC addresses
│           └── root/.ssh # SSH configuration
├── iso-host
│   ├── build.sh
│   └── config
│       ├── hooks
│       │   ├── live
│       │   │   └── 0100-fastboot.hook.binary # Configure bootloaders to enable unattended boot
│       │   └── normal
│       │       ├── 0100-access.hook.chroot # Configure access
│       │       ├── 0200-networkd.hook.chroot # Enable networkd and disable wait-online
│       │       ├── 0300-virsh.hook.chroot # Configure infrastructure
│       └── includes.chroot
│           ├── qemu
│           │   ├── domain # QEMU domains in XML format
│           │   └── network # QEMU networks in XML format
│           │   └── guest.iso # Live ISO for guests (has to be build)
│           └── root
│               └── benchmark # Benchmark script
│                   ├── configuration.py # Static configuration
│                   ├── execute.py # Core benchmark
│                   ├── generate.py # Generate experiments
│                   ├── infrastructure.py # Control current state of infrastructure
│                   ├── main.py
│                   └── shell.py # Helper functions that execute shell commands on host/guest
└── process-results
    └── graph.py # Analyze results
```
