import pandas as pd

# Load original dataset
df = pd.read_csv("gas_data.csv.xls")

print("Original shape:", df.shape)

# Create gas_delta
df["gas_delta"] = df["raw"] - df["baseline"]

# Keep only useful modelling columns
clean_df = df[
    [
        "raw",
        "baseline",
        "gas_delta",
        "temp_c",
        "hum_pct",
        "exposure"
    ]
].copy()

# Remove exact duplicates if any appear after selecting columns
clean_df = clean_df.drop_duplicates()

# Remove rows with missing values
clean_df = clean_df.dropna()

# Keep valid labels only
clean_df = clean_df[
    clean_df["exposure"].isin([0, 1])
]

# Basic physical validation
clean_df = clean_df[
    (clean_df["raw"] >= 0)
    & (clean_df["baseline"] >= 0)
    & (clean_df["hum_pct"].between(0, 100))
    & (clean_df["temp_c"].between(-20, 80))
]

print("\nCleaned shape:", clean_df.shape)

print("\nExposure distribution:")
print(clean_df["exposure"].value_counts())

print("\nGas delta statistics:")
print(clean_df["gas_delta"].describe())

print("\nMean values by exposure:")
print(
    clean_df.groupby("exposure")[
        ["raw", "baseline", "gas_delta", "temp_c", "hum_pct"]
    ].mean()
)

# Save cleaned dataset
clean_df.to_csv(
    "gas_data_clean.csv",
    index=False
)

print("\nSaved as gas_data_clean.csv")