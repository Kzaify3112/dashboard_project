import os
import pandas as pd
import numpy as np

# ── Dataset path & auto-download ───────────────────────
FILE_ID   = "1g7CP9-eYivJHRXvJePwzVPkm9DnNFH-R"
DATA_PATH = "data/household_power_consumption.txt"

def download_dataset():
    """Download dataset from Google Drive if not present locally."""
    if not os.path.exists(DATA_PATH):
        print("Dataset not found locally. Downloading from Google Drive...")
        os.makedirs("data", exist_ok=True)
        url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
        
        # Use requests to handle large file download
        import requests
        session = requests.Session()
        response = session.get(url, stream=True)
        
        # Handle Google Drive virus scan warning for large files
        token = None
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value
                break

        if token:
            response = session.get(
                url, params={"confirm": token}, stream=True
            )

        # Save file
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

    # Read the file
    df = pd.read_csv(
        filepath,
        sep=";",
        na_values="?",
    )

    # Combine Date and Time into one column
    df["Datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        dayfirst=True
    )

    # Drop old separate columns
    df.drop(columns=["Date", "Time"], inplace=True)

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