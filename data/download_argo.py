from argopy import DataFetcher as ArgoDataFetcher


print("Fetching ARGO data...")


ds = (
    ArgoDataFetcher()
    .region([
        60,
        90,
        -10,
        20,
        0,
        1000,
        "2025-01",
        "2025-02"
    ])
    .to_xarray()
)


print("ARGO data downloaded successfully.")

print(ds)


# Save dataset as NetCDF

ds.to_netcdf(
    "data/argo_indian_ocean.nc"
)


print(
    "Saved to: data/argo_indian_ocean.nc"
)