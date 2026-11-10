import seaborn as sns
import matplotlib.pyplot as plt
from utils import parse_benchmark_to_dataframe
from utils import filter_by_mask
from utils import df_combined_to_markdown
from utils import df_combined_to_csv
from static import *

df, df_mean, df_sd, df_rsd, df_combined, df_series = parse_benchmark_to_dataframe(project_dir / "results")

for filename, meta in experiment_groups.items():
    sdf = filter_by_mask(df_series, meta["mask"])

    # Group by vpn to identify rows
    vpn_groups = sdf.groupby('vpn')
    vpn_list = list(vpn_groups.groups.keys())
    num_vpns = len(vpn_list)

    # Grid: one row per VPN, one column per rerun
    rows = max(num_vpns, 1)
    cols = max((len(vpn_groups.get_group(v)) for v in vpn_list), default=1)

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(max(10, cols), max(3, rows * 3)),
        constrained_layout=True,
        squeeze=False,
    )

    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]
            
            # Check if we have a vpn group for this row index
            # If you have fewer than 4 VPNs, this logic needs to be adjusted.
            # Assuming exactly 4 VPNs as per your "4 rows, each row is a vpn" requirement.
            if r < num_vpns:
                vpn_val = vpn_list[r]
                # Get all rows for this VPN
                vpn_data = vpn_groups.get_group(vpn_val)
                
                # If you want each subplot to be a specific index/experiment within that VPN:
                # This logic assumes the 10 columns represent the 10 experiments/runs per VPN
                if c < len(vpn_data):
                    row_idx = vpn_data.index[c]
                    series_data1 = vpn_data.loc[row_idx, "down"]
                    series_data2 = vpn_data.loc[row_idx, "up"]
                    
                    ax.plot(series_data1)
                    ax.plot(series_data2)
                    ax.set_title(f"V: {vpn_val}", fontsize=8)
                    ax.tick_params(labelsize=6)
                else:
                    ax.axis('off')
            else:
                ax.axis('off')
            
            # Hide axes for empty cells if rows < 4
            if r >= num_vpns:
                ax.axis('off')

    plt.suptitle(f"{meta['desc']}", fontsize=16)
    plt.savefig(project_dir / "outputs" / "graphs" / f"{filename}_grid.png", dpi=300, bbox_inches="tight")
    plt.close()