import xarray as xr
import pandas as pd


DATA_FILE = "data/argo_indian_ocean.nc"


# ==================================================
# LOAD DATASET
# ==================================================

def load_argo_data():
    """Load the local ARGO NetCDF dataset."""

    return xr.open_dataset(DATA_FILE)


# ==================================================
# DATAFRAME
# ==================================================

def get_dataframe():
    """Convert required ARGO variables to DataFrame."""

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


# ==================================================
# TEMPERATURE
# ==================================================

def temperature_summary():

    df = get_dataframe()

    temperature = df["TEMP"].dropna()

    return {
        "count": int(temperature.count()),
        "average": round(float(temperature.mean()), 2),
        "minimum": round(float(temperature.min()), 2),
        "maximum": round(float(temperature.max()), 2),
    }


# ==================================================
# SALINITY
# ==================================================

def salinity_summary():

    df = get_dataframe()

    salinity = df["PSAL"].dropna()

    return {
        "count": int(salinity.count()),
        "average": round(float(salinity.mean()), 2),
        "minimum": round(float(salinity.min()), 2),
        "maximum": round(float(salinity.max()), 2),
    }


# ==================================================
# DATASET SUMMARY
# ==================================================

def dataset_summary():

    df = get_dataframe()

    return {

        "observations":
            int(len(df)),

        "floats":
            int(df["PLATFORM_NUMBER"].nunique()),

        "latitude_min":
            round(float(df["LATITUDE"].min()), 2),

        "latitude_max":
            round(float(df["LATITUDE"].max()), 2),

        "longitude_min":
            round(float(df["LONGITUDE"].min()), 2),

        "longitude_max":
            round(float(df["LONGITUDE"].max()), 2),

        "pressure_min":
            round(float(df["PRES"].min()), 2),

        "pressure_max":
            round(float(df["PRES"].max()), 2),
    }


# ==================================================
# TEMPERATURE VISUALIZATION DATA
# ==================================================

def temperature_data(limit=1000):

    df = get_dataframe()

    data = (
        df[["PRES", "TEMP"]]
        .dropna()
        .head(limit)
    )

    return {

        "pressure":
            data["PRES"].round(2).tolist(),

        "temperature":
            data["TEMP"].round(2).tolist()
    }


# ==================================================
# SALINITY VISUALIZATION DATA
# ==================================================

def salinity_data(limit=1000):

    df = get_dataframe()

    data = (
        df[["PRES", "PSAL"]]
        .dropna()
        .head(limit)
    )

    return {

        "pressure":
            data["PRES"].round(2).tolist(),

        "salinity":
            data["PSAL"].round(2).tolist()
    }


# ==================================================
# LOCATION VISUALIZATION DATA
# ==================================================

def location_data(limit=1000):

    df = get_dataframe()

    data = (
        df[["LATITUDE", "LONGITUDE"]]
        .dropna()
        .drop_duplicates()
        .head(limit)
    )

    return {

        "latitude":
            data["LATITUDE"].round(4).tolist(),

        "longitude":
            data["LONGITUDE"].round(4).tolist()
    }