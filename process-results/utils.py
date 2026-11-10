import json
import pandas as pd
from pathlib import Path
from static import *
import csv
import io


def parse_sar(exp_dir):
    sar_df = pd.read_csv(exp_dir / "cpu.csv", sep=None, engine="python")
    return (100.0 - pd.to_numeric(sar_df["%idle"], errors="coerce")).mean()


def parse_iperf(exp_dir, filename):
    data = json.loads((exp_dir / filename).read_text())
    end = data["end"]
    # sum_received = goodput of the receiving side; present for both -c and -R
    block = end.get("sum_received") or end["sum_sent"]
    return block["bits_per_second"] / 1_000_000


def parse_iperf_series(exp_dir, filename):
    data = json.loads((exp_dir / filename).read_text())
    return pd.Series([i["sum"]["bits_per_second"] / 1_000_000 for i in data.get("intervals", [])])

def process_experiment(exp_dir: Path, exp_meta: dict) -> tuple[dict, dict]:
    header = {
        "vpn": exp_meta.get("vpn"),
        "impair": exp_meta.get("impair", True),
        "bandwidth": exp_meta.get("bandwidth", "0"),
        "burst": exp_meta.get("burst", "10mbit"),
        "delay": exp_meta.get("delay"),
        "jitter": exp_meta.get("jitter"),
        "loss": exp_meta.get("loss"),
        "cpu_freq": exp_meta.get("cpu_freq"),
        "core_count": exp_meta.get("core_count", 0),
    }

    row = {
        **header,
        "cpu": parse_sar(exp_dir),
        "down": parse_iperf(exp_dir, "iperf_down.json"),
        "up": parse_iperf(exp_dir, "iperf_up.json"),
    }

    row_series = {
        **header,
        "down": parse_iperf_series(exp_dir, "iperf_down.json"),
        "up": parse_iperf_series(exp_dir, "iperf_up.json"),
    }

    return row, row_series


def parse_benchmark_to_dataframe(results_dir: Path):
    # Get experiment metadata
    with (results_dir / "metadata.json").open("r") as f:
        meta_list = json.load(f)

    # Parse results
    rows, rows_series = [], []
    for idx, meta in enumerate(meta_list):
        row, series_row = process_experiment(results_dir / str(idx), meta)
        rows.append(row)
        rows_series.append(series_row)

    # Create dataframes
    df = pd.DataFrame(rows)
    df_series = pd.DataFrame(rows_series)

    # Clean strings to numbers
    for adf in df, df_series:
        adf["bandwidth"] = adf["bandwidth"].astype(str).str.replace("mbit", "", regex=False).astype(int)
        adf["burst"] = adf["burst"].astype(str).str.replace("mbit", "", regex=False).astype(int)
        adf["delay"] = adf["delay"].astype(str).str.replace("ms", "", regex=False).astype(int)
        adf["jitter"] = adf["jitter"].astype(str).str.replace("ms", "", regex=False).astype(int)
        adf["loss"] = adf["loss"].astype(str).str.replace("%", "", regex=False).astype(float)
        adf["cpu_freq"] = adf["cpu_freq"].astype(str).str.replace("GHz", "", regex=False).astype(float)

    # Enhance
    df["efficiency"] = (df["down"] + df["up"]) / df["cpu"]

    # Group reruns of same experiment
    grouped = df.groupby(key_cols)

    # Aggregate reruns
    df_mean = grouped.mean()
    df_sd = grouped.std()
    df_rsd = (df_sd / df_mean).round(4)
    df_combined = (
        df_mean.join(df_sd, lsuffix="_mean", rsuffix="_sd")
        .join(df_rsd.add_suffix("_rsd"))
        .reset_index()
    )

    return (
        df,
        df_mean.reset_index(),
        df_sd.reset_index(),
        df_rsd.reset_index(),
        df_combined,
        df_series,
    )

def df_combined_to_markdown(
    df_combined: pd.DataFrame,
    group_cols: list[str] = key_cols,
    units: dict[str, str] = {},
    precision: int = 1,
    sd_thresholds: dict[str, float] = {},
    rsd_threshold: float = 0.15,
) -> str:
    metrics = [c[:-5] for c in df_combined.columns if c.endswith("_mean")]

    headers = list(group_cols)
    for m in metrics:
        headers += [m, "", ""]

    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]

    for _, r in df_combined.iterrows():
        cells = [str(r[g]) for g in group_cols]
        for m in metrics:
            mean, sd, rsd = r.get(f"{m}_mean"), r.get(f"{m}_sd"), r.get(f"{m}_rsd")
            unit = units.get(m, "")
            if pd.isna(mean):
                cells += ["—", "", ""]
                continue

            mean_s = f"{mean:.{precision}f}{unit}"
            #sd_s = "—" if pd.isna(sd) else f"± {sd:.{precision}f}"
            sd_s = "—" if pd.isna(sd) else f"{sd:.{precision}f}"
            rsd_s = "—" if pd.isna(rsd) else f"{rsd * 100:.0f}%"

            sd_bad = (m in sd_thresholds and not pd.isna(sd) and sd > sd_thresholds[m])
            rsd_bad = not pd.isna(rsd) and rsd > rsd_threshold

            if sd_bad and rsd_bad:
                mean_s = f"🔴 {mean_s}"
            else:
                mean_s = f"🟢 {mean_s}"

            cells += [mean_s, sd_s, rsd_s]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)

def df_combined_to_csv(
    df_combined: pd.DataFrame,
    group_cols: list[str] = key_cols,
    units: dict[str, str] = {},
    precision: int = 1
) -> str:
    metrics = [c[:-5] for c in df_combined.columns if c.endswith("_mean")]

    headers = list(group_cols)
    for m in metrics:
        headers += [f"{m}_mean", f"{m}_sd", f"{m}_rsd"]

    output = io.StringIO()
    # Delimiter set to semicolon
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    writer.writerow(headers)

    for _, r in df_combined.iterrows():
        cells = [str(r[g]) for g in group_cols]
        for m in metrics:
            mean, sd, rsd = (
                r.get(f"{m}_mean"),
                r.get(f"{m}_sd"),
                r.get(f"{m}_rsd"),
            )

            if pd.isna(mean):
                cells += ["—", "", ""]
                continue

            mean_s = f"{mean:.{precision}f}{units.get(m, '')}"
            sd_s = "—" if pd.isna(sd) else f"{sd:.{precision}f}"
            rsd_s = "—" if pd.isna(rsd) else f"{rsd * 100:.0f}%"

            cells += [mean_s, sd_s, rsd_s]

        writer.writerow(cells)

    return output.getvalue()

def filter_by_mask(df, mask: dict):
    m = pd.Series(True, index=df.index)
    for col, val in mask.items():
        m &= (df[col] == val)
    return df[m]