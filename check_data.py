import pandas as pd

# Load dataset
df = pd.read_csv("gas_data.csv.xls")

print("=" * 60)
print("1. DATASET OVERVIEW")
print("=" * 60)

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df.head(10))

print("\nData types:")
print(df.dtypes)


print("\n" + "=" * 60)
print("2. MISSING VALUES")
print("=" * 60)

print(df.isnull().sum())


print("\n" + "=" * 60)
print("3. DUPLICATE ROWS")
print("=" * 60)

duplicates = df.duplicated().sum()
print("Duplicate rows:", duplicates)


print("\n" + "=" * 60)
print("4. EXPOSURE LABELS")
print("=" * 60)

print(df["exposure"].value_counts(dropna=False))

print("\nPercentage:")
print(df["exposure"].value_counts(normalize=True) * 100)


print("\n" + "=" * 60)
print("5. NUMERICAL STATISTICS")
print("=" * 60)

print(
    df[
        [
            "time_ms",
            "raw",
            "baseline",
            "temp_c",
            "hum_pct",
            "exposure"
        ]
    ].describe()
)


print("\n" + "=" * 60)
print("6. INVALID VALUES")
print("=" * 60)

print("raw < 0:", (df["raw"] < 0).sum())
print("baseline < 0:", (df["baseline"] < 0).sum())

print(
    "Temperature outside -20 to 80 C:",
    ((df["temp_c"] < -20) | (df["temp_c"] > 80)).sum()
)

print(
    "Humidity outside 0-100%:",
    ((df["hum_pct"] < 0) | (df["hum_pct"] > 100)).sum()
)

print(
    "Exposure values other than 0 or 1:",
    (~df["exposure"].isin([0, 1])).sum()
)


print("\n" + "=" * 60)
print("7. GAS SENSOR DIFFERENCE")
print("=" * 60)

df["gas_delta"] = df["raw"] - df["baseline"]

print(df["gas_delta"].describe())

print("\nNegative gas_delta values:")
print((df["gas_delta"] < 0).sum())


print("\n" + "=" * 60)
print("8. VALUES BY EXPOSURE CLASS")
print("=" * 60)

print(
    df.groupby("exposure")[
        ["raw", "baseline", "gas_delta", "temp_c", "hum_pct"]
    ].mean()
)


print("\n" + "=" * 60)
print("9. SESSION DISTRIBUTION")
print("=" * 60)

print(df["session_id"].value_counts().sort_index())


print("\n" + "=" * 60)
print("10. EXPOSURE PER SESSION")
print("=" * 60)

print(
    pd.crosstab(
        df["session_id"],
        df["exposure"]
    )
)


print("\n" + "=" * 60)
print("DATA CHECK COMPLETE")
print("=" * 60)