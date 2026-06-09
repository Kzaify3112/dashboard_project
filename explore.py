import pandas as pd

df = pd.read_csv(
    "data/household_power_consumption.txt",
    sep=";",
    na_values="?"
)

print("shape:",df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values per column:")
print(df.isnull().sum())
