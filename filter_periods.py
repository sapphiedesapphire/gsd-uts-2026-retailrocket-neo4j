import os

import pandas as pd

SOURCE = "data"
P1_START, P1_END = "2015-06-23", "2015-07-01"  # training period (inclusive)
P2_START, P2_END = "2015-07-02", "2015-07-10"  # testing period (inclusive)


def filter_period(df, start, end):
    # timestamp is Unix epoch in milliseconds (UTC); the end date is included until 23:59:59
    start_ms = int(pd.Timestamp(start).timestamp() * 1000)
    end_ms = int((pd.Timestamp(end) + pd.Timedelta(days=1)).timestamp() * 1000)
    return df[(df["timestamp"] >= start_ms) & (df["timestamp"] < end_ms)]


df = pd.read_csv(os.path.join(SOURCE, "events.csv"))

for name, (start, end) in {"p1": (P1_START, P1_END), "p2": (P2_START, P2_END)}.items():
    period = filter_period(df, start, end)
    path = os.path.join(SOURCE, f"events_{name}.csv")
    period.to_csv(path, index=False)
    print(f"{name.upper()} {start} to {end}: {len(period):,} rows, "
          f"{period['visitorid'].nunique():,} visitors, {period['itemid'].nunique():,} items -> {path}")