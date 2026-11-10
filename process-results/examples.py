# import gzip
# import json
# import tabulate
# import pandas as pd
# import numpy as np
# from pathlib import Path
# import seaborn as sns
# import matplotlib.pyplot as plt
# import sqlite3
# import gzip
# import json
# from pathlib import Path
# import pandas as pd
# from parse import parse_benchmark_to_dataframe
# from static import *

# Dump to sqlite
db = sqlite3.connect(project_dir / "outputs" / "results.db")
df_combined.to_sql("test", db, if_exists="replace", index=False)
db.close()

# Dump to .csv
df_sorted = df.round(3).sort_values(by=["vpn", "delay", "jitter", "loss", "cpu_freq", "core_count"], ascending=False)
df_sorted.to_csv(project_dir / "outputs" / "raw.csv", index=False)

# Filtering and sorting
selected_df = df[
    (df['core_count'] == 4) &
    True
].sort_values(by=["efficiency"], ascending=False)

# Grouping
summary = df.groupby(['vpn', 'core_count'])[['throughput', 'cpu_mean']].mean()

# Reload stale imports
%load_ext autoreload
%autoreload 2