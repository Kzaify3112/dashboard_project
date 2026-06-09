import os
import pandas as pd
import numpy as np

# Check if running on Render cloud
is_cloud = os.environ.get("RENDER", False)

# ── Dataset path & auto-download ───────────────────────
FILE_ID   = "1g7CP9-eYivJHRXvJePwzVPkm9DnNFH-R"
DATA_PATH = "data/household_power_consumption.txt"

def download_dataset():
    """Download dataset from Google Drive if not present locally."""
    if not os.path.exists(DATA_PATH):
        print("Downloading dataset from Google Drive...")
        os.makedirs("data", exist_ok=True)

        import requests
        url = "https://drive.usercontent.google.com/download"
        params = {
            "id":      FILE_ID,
            "export":  "download",
            "confirm": "t"
        }

        response = requests.get(url, params=params, stream=True)

        with open(DATA_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)

        print("Download complete!")
    else:
        print("Dataset found locally.")


def load_data(filepath):

    # Download if not exists
    download_dataset()

    # Read the file — sample on cloud to save RAM
    df = pd.read_csv(
        filepath,
        sep=";",
        na_values="?",
        nrows=200000 if is_cloud else None
    )

    # Combine Date and Time if they exist as separate columns
    if "Date" in df.columns and "Time" in df.columns:
        df["Datetime"] = pd.to_datetime(
            df["Date"] + " " + df["Time"],
            dayfirst=True
        )
        df.drop(columns=["Date", "Time"], inplace=True)
    elif "Datetime" not in df.columns:
        df["Datetime"] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)

    # Fix missing values
    cols = [
        "Global_active_power", "Global_reactive_power",
        "Voltage", "Global_intensity",
        "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"
    ]
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    # Add new columns
    df["Hour"]       = df["Datetime"].dt.hour
    df["Month"]      = df["Datetime"].dt.month
    df["Year"]       = df["Datetime"].dt.year
    df["Weekday"]    = df["Datetime"].dt.day_name()
    df["Month_Name"] = df["Datetime"].dt.strftime("%b")

    df["Season"] = df["Month"].map({
        12: "Winter", 1: "Winter",  2: "Winter",
        3:  "Spring", 4: "Spring",  5: "Spring",
        6:  "Summer", 7: "Summer",  8: "Summer",
        9:  "Autumn", 10: "Autumn", 11: "Autumn",
    })

    return df


def apply_filters(df, year_filter=None, season_filter=None,
                  hour_range=None, power_range=None,
                  weekday_filter=None, date_range=None):

    filtered = df.copy()

    if date_range and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            (filtered["Datetime"].dt.date >= start) &
            (filtered["Datetime"].dt.date <= end)
        ]

    if year_filter:
        filtered = filtered[filtered["Year"].isin(year_filter)]

    if season_filter:
        filtered = filtered[filtered["Season"].isin(season_filter)]

    if hour_range:
        filtered = filtered[
            (filtered["Hour"] >= hour_range[0]) &
            (filtered["Hour"] <= hour_range[1])
        ]

    if power_range:
        filtered = filtered[
            (filtered["Global_active_power"] >= power_range[0]) &
            (filtered["Global_active_power"] <= power_range[1])
        ]

    if weekday_filter:
        filtered = filtered[filtered["Weekday"].isin(weekday_filter)]

    return filtered