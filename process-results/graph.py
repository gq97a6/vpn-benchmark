"""Generates time-series line plots for upload, download, and CPU utilization across experiment groups."""

import pandas as pd
import matplotlib.pyplot as plt
from utils import parse_benchmark_to_dataframe
from utils import filter_by_mask
from static import *

df, df_mean, df_sd, df_rsd, df_combined, df_series = parse_benchmark_to_dataframe(project_dir / "results")

COLOR = {"down": "tab:blue", "up": "tab:orange", "cpu": "tab:green"}
YLABEL = {"down": "Mbit/s", "up": "Mbit/s", "cpu": "CPU [%]"}
VPN_ORDER = ["none", "wireguard", "nebula", "openvpn"]

graphs_dir = project_dir / "outputs" / "graphs"
for metric in ("down", "up", "cpu"):
    (graphs_dir / metric).mkdir(parents=True, exist_ok=True)

for filename, meta in experiment_groups.items():
    sdf = filter_by_mask(df_series, meta["mask"])
    if sdf.empty:
        continue

    r = sdf.iloc[0]
    subtext = (f"{int(r['bandwidth'])} mbit • {int(r['burst'])} mbit • "
               f"{int(r['delay'])} ms ± {int(r['jitter'])} ms • "
               f"{r['loss']:g}% • {int(r['core_count'])} core • {r['cpu_freq']:g} GHz")

    for metric in ("down", "up", "cpu"):
        fig, axes = plt.subplots(len(VPN_ORDER), 1, figsize=(10, 11), sharex=True)

        for ax, vpn in zip(axes, VPN_ORDER):
            sub = sdf[sdf["vpn"] == vpn]
            series = [s for s in sub[metric] if isinstance(s, pd.Series) and len(s)]
            for s in series:
                ax.plot(s.index, s.values, color=COLOR[metric], linewidth=0.8)
            ax.set_title(vpn, fontsize=9, loc="left")
            ax.set_ylabel(YLABEL[metric])
            ax.grid(alpha=0.3)

        axes[-1].set_xlabel("time [s]")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.suptitle(f"{meta['desc']} - {metric}", fontsize=13, y=0.99)
        fig.text(0.5, 0.968, subtext, ha="center", va="top", fontsize=9, color="dimgray")

        fig.savefig(graphs_dir / metric / f"{filename}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)