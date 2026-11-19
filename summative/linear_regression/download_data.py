
from pathlib import Path

import pandas as pd
import requests

# Years covered by our dataset
START_YEAR = 2000
END_YEAR = 2024

# African countries (ISO3 codes)
AFRICAN_COUNTRIES = """
DZA AGO BEN BWA BFA BDI CPV CMR CAF TCD COM COD COG
CIV DJI EGY GNQ ERI SWZ ETH GAB GMB GHA GIN GNB
KEN LSO LBR LBY MDG MWI MLI MRT MUS MAR MOZ NAM
NER NGA RWA STP SEN SYC SLE SOM ZAF SSD SDN TZA
TGO TUN UGA ZMB ZWE
""".split()

# World Bank indicators we want to collect
INDICATORS = {
    "youth_unemployment_rate": "SL.UEM.1524.ZS",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "inflation": "FP.CPI.TOTL.ZG",
    "secondary_enrollment": "SE.SEC.ENRR",
    "education_expenditure": "SE.XPD.TOTL.GD.ZS",
    "urban_population_pct": "SP.URB.TOTL.IN.ZS",
    "population_growth": "SP.POP.GROW",
    "agriculture_employment": "SL.AGR.EMPL.ZS",
    "industry_employment": "SL.IND.EMPL.ZS",
    "female_labor_participation": "SL.TLF.CACT.FE.ZS",
}

BASE_URL = "https://api.worldbank.org/v2"
OUTPUT = Path(__file__).resolve().parent / "data"
OUTPUT.mkdir(parents=True, exist_ok=True)

session = requests.Session()


def get_all_pages(url, params=None):
    """Download every page of an API response."""
    params = dict(params or {})
    params.update({"format": "json", "per_page": 20000})

    records = []
    page = 1

    while True:
        response = session.get(
            url,
            params={**params, "page": page},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError(f"Unexpected API response: {payload}")

        metadata, observations = payload
        records.extend(observations or [])

        if page >= int(metadata["pages"]):
            break

        page += 1

    return records


def get_countries():
    """Retrieve metadata for African countries."""
    print("Downloading country information...")

    countries = get_all_pages(f"{BASE_URL}/country")

    rows = []

    for country in countries:
        code = country["id"]

        if code not in AFRICAN_COUNTRIES:
            continue

        rows.append({
            "country_code": code,
            "country": country["name"],
            "region": country["region"]["value"],
            "income_group": country["incomeLevel"]["value"],
        })

    return pd.DataFrame(rows)


def get_indicator(column, indicator_code):
    """Retrieve one World Bank indicator."""
    print(f"Downloading {column}...")

    observations = get_all_pages(
        f"{BASE_URL}/country/all/indicator/{indicator_code}",
        {
            "date": f"{START_YEAR}:{END_YEAR}",
            "source": 2,
        },
    )

    rows = []

    for item in observations:
        code = item["countryiso3code"]

        if code not in AFRICAN_COUNTRIES:
            continue

        rows.append({
            "country_code": code,
            "year": int(item["date"]),
            column: item["value"],
        })

    return pd.DataFrame(rows)


def main():
    countries = get_countries()

    years = pd.DataFrame({
        "year": range(START_YEAR, END_YEAR + 1)
    })

    # One row per country and year
    dataset = countries.merge(years, how="cross")

    # Add each economic and education indicator
    for column, code in INDICATORS.items():
        indicator_data = get_indicator(column, code)

        dataset = dataset.merge(
            indicator_data,
            on=["country_code", "year"],
            how="left",
            validate="one_to_one",
        )

    dataset = dataset.sort_values(
        ["country", "year"]
    ).reset_index(drop=True)

    # Save dataset as CSV
    csv_path = OUTPUT / "africa_youth_unemployment.csv"
    dataset.to_csv(csv_path, index=False)

    # Calculate missing values
    missing = (
        dataset.isna().mean() * 100
    ).sort_values(ascending=False)

    complete = dataset.dropna(
        subset=list(INDICATORS)
    )

    print("\nDATASET SUMMARY")
    print("=" * 40)
    print(f"Total rows: {len(dataset)}")
    print(f"Countries: {dataset['country_code'].nunique()}")
    print(f"Columns: {len(dataset.columns)}")
    print(f"Complete indicator rows: {len(complete)}")

    print("\nMISSING VALUES (%)")
    print(missing.round(2).to_string())

    print("\nFIRST FIVE ROWS")
    print(dataset.head().to_string(index=False))

    missing.to_csv(
        OUTPUT / "missing_values.csv",
        header=["missing_pct"],
    )

    print(f"\nDataset saved to: {csv_path}")


if __name__ == "__main__":
    main()
