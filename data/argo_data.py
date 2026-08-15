import xarray as xr
import pandas as pd

DATA_FILE = "data/argo_indian_ocean.nc"


def load_argo_data():
    """Load the local ARGO dataset."""
    return xr.open_dataset(DATA_FILE)


def get_dataframe():
    """Convert ARGO data into a Pandas DataFrame."""
    ds = load_argo_data()

    df = ds[
        [
            "LATITUDE",
            "LONGITUDE",
            "TIME",
            "PRES",
            "TEMP",
            "PSAL",
            "PLATFORM_NUMBER",
        ]
    ].to_dataframe().reset_index()

    return df


def temperature_summary():
    """Return basic temperature statistics."""
    df = get_dataframe()

    temperature = df["TEMP"].dropna()

    return {
        "count": int(temperature.count()),
        "average": round(float(temperature.mean()), 2),
        "minimum": round(float(temperature.min()), 2),
        "maximum": round(float(temperature.max()), 2),
    }


def salinity_summary():
    """Return basic salinity statistics."""
    df = get_dataframe()

    salinity = df["PSAL"].dropna()

    return {
        "count": int(salinity.count()),
        "average": round(float(salinity.mean()), 2),
        "minimum": round(float(salinity.min()), 2),
        "maximum": round(float(salinity.max()), 2),
    }


def dataset_summary():
    """Return general ARGO dataset information."""
    df = get_dataframe()

    return {
        "observations": len(df),
        "floats": int(df["PLATFORM_NUMBER"].nunique()),
        "latitude_min": round(float(df["LATITUDE"].min()), 2),
        "latitude_max": round(float(df["LATITUDE"].max()), 2),
        "longitude_min": round(float(df["LONGITUDE"].min()), 2),
        "longitude_max": round(float(df["LONGITUDE"].max()), 2),
        "depth_min": round(float(df["PRES"].min()), 2),
        "depth_max": round(float(df["PRES"].max()), 2),
    }
