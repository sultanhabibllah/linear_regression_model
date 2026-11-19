
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

START_YEAR = 2000
END_YEAR = 2024

# ISO3 codes for 54 African countries
AFRICAN_COUNTRIES = """
DZA AGO BEN BWA BFA BDI CPV CMR CAF TCD COM COD COG
CIV DJI EGY GNQ ERI SWZ ETH GAB GMB GHA GIN GNB
KEN LSO LBR LBY MDG MWI MLI MRT MUS MAR MOZ NAM
NER NGA RWA STP SEN SYC SLE SOM ZAF SSD SDN TZA
TGO TUN UGA ZMB ZWE
""".split()

# Target and candidate predictor variables
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

TARGET = "youth_unemployment_rate"
FEATURES = [name for name in INDICATORS if name != TARGET]

BASE_URL = "https://api.worldbank.org/v2"

OUTPUT = Path(__file__).resolve().parent / "data"
OUTPUT.mkdir(parents=True, exist_ok=True)

session = requests.Session()


# --------------------------------------------------
# WORLD BANK API
# --------------------------------------------------

def get_all_pages(url, params=None):
    """Retrieve all pages of a World Bank API response."""
    params = dict(params or {})
    params.update({
        "format": "json",
        "per_page": 20000,
    })

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
            raise ValueError(
                f"Unexpected World Bank response: {payload}"
            )

        metadata, observations = payload
        records.extend(observations or [])

        if page >= int(metadata["pages"]):
            break

        page += 1

    return records


def get_countries():
    """Retrieve African country names and metadata."""
    print("Downloading African country information...")

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

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError("No African countries found.")

    missing_codes = set(AFRICAN_COUNTRIES) - set(
        df["country_code"]
    )

    if missing_codes:
        print(
            "Country metadata unavailable for:",
            sorted(missing_codes),
        )

    print(f"African countries found: {len(df)}")
    return df


def get_indicator(column, indicator_code):
    """Download one World Bank indicator."""
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

    df = pd.DataFrame(
        rows,
        columns=["country_code", "year", column],
    )

    if df.empty:
        raise ValueError(
            f"No African observations for {column}"
        )

    return df


# --------------------------------------------------
# DATASET CREATION
# --------------------------------------------------

def build_dataset():
    """Combine all indicators by country and year."""
    countries = get_countries()

    years = pd.DataFrame({
        "year": range(START_YEAR, END_YEAR + 1)
    })

    dataset = countries.merge(years, how="cross")

    for column, code in INDICATORS.items():
        indicator_data = get_indicator(column, code)

        dataset = dataset.merge(
            indicator_data,
            on=["country_code", "year"],
            how="left",
            validate="one_to_one",
        )

    return dataset.sort_values(
        ["country", "year"]
    ).reset_index(drop=True)


# --------------------------------------------------
# DATASET QUALITY ANALYSIS
# --------------------------------------------------

def analyze_dataset(dataset):
    """Report dataset dimensions and missing values."""
    print("\nDATASET SUMMARY")
    print("=" * 50)

    print(f"Total rows: {len(dataset)}")
    print(f"Countries: {dataset['country_code'].nunique()}")
    print(f"Columns: {len(dataset.columns)}")
    print(
        f"Year range: {dataset['year'].min()}-"
        f"{dataset['year'].max()}"
    )

    duplicates = dataset.duplicated(
        ["country_code", "year"]
    ).sum()

    print(f"Duplicate country-year rows: {duplicates}")

    missing = (
        dataset.isna().mean() * 100
    ).sort_values(ascending=False)

    print("\nMISSING VALUES (%)")
    print("=" * 50)
    print(missing.round(2).to_string())

    missing.rename("missing_pct").to_csv(
        OUTPUT / "missing_values.csv",
        header=True,
    )

    known_target = dataset[TARGET].notna()

    complete_rows = dataset.dropna(
        subset=[TARGET] + FEATURES
    )

    print("\nMODELLING READINESS")
    print("=" * 50)

    print(f"Rows with known target: {known_target.sum()}")
    print(f"Complete numeric rows: {len(complete_rows)}")

    print(
        "Countries with target data:",
        dataset.loc[
            known_target, "country_code"
        ].nunique(),
    )

    print(f"Candidate numeric features: {len(FEATURES)}")
    print("Categorical features: region, income_group")

    if len(complete_rows) >= 1000:
        print(
            "Complete-case row count meets "
            "the 1,000-row requirement."
        )
    else:
        print(
            "Complete-case row count is below 1,000. "
            "Feature selection or missing-data "
            "handling requires further investigation."
        )


# --------------------------------------------------
# COUNTRY-LEVEL COMPLETENESS
# --------------------------------------------------

def analyze_countries(dataset):
    """Examine data availability for each country."""
    print("\nCOUNTRY COMPLETENESS ANALYSIS")
    print("=" * 50)

    rows = []

    for (code, country), group in dataset.groupby(
        ["country_code", "country"]
    ):
        target_rows = group[TARGET].notna().sum()

        complete_rows = group[
            [TARGET] + FEATURES
        ].notna().all(axis=1).sum()

        feature_availability = (
            group[FEATURES].notna().mean().mean() * 100
        )

        rows.append({
            "country_code": code,
            "country": country,
            "total_years": len(group),
            "years_with_target": int(target_rows),
            "complete_rows": int(complete_rows),
            "feature_availability_pct": round(
                feature_availability, 2
            ),
        })

    report = pd.DataFrame(rows)

    report = report.sort_values(
        ["complete_rows", "feature_availability_pct"],
        ascending=False,
    ).reset_index(drop=True)

    report.to_csv(
        OUTPUT / "country_completeness.csv",
        index=False,
    )

    print("\nTOP 10 COUNTRIES BY COMPLETE RECORDS")
    print(
        report.head(10).to_string(index=False)
    )

    print("\nBOTTOM 10 COUNTRIES BY COMPLETE RECORDS")
    print(
        report.tail(10).to_string(index=False)
    )

    print("\nCOUNTRY COVERAGE SUMMARY")
    print("=" * 50)

    print(
        "Countries with 20+ complete years:",
        (report["complete_rows"] >= 20).sum(),
    )

    print(
        "Countries with 10+ complete years:",
        (report["complete_rows"] >= 10).sum(),
    )

    print(
        "Countries with no complete years:",
        (report["complete_rows"] == 0).sum(),
    )

    return report


# --------------------------------------------------
# FEATURE AVAILABILITY
# --------------------------------------------------

def analyze_features(dataset):
    """Evaluate availability of candidate predictors."""
    print("\nFEATURE AVAILABILITY")
    print("=" * 50)

    # Only count rows where the target is known.
    eligible = dataset[dataset[TARGET].notna()]

    rows = []

    for feature in FEATURES:
        available = eligible[feature].notna().sum()

        availability_pct = (
            100 * available / len(eligible)
            if len(eligible) > 0 else 0
        )

        rows.append({
            "feature": feature,
            "available_rows": int(available),
            "availability_pct": round(
                availability_pct, 2
            ),
        })

    report = pd.DataFrame(rows).sort_values(
        "availability_pct",
        ascending=False,
    )

    report.to_csv(
        OUTPUT / "feature_availability.csv",
        index=False,
    )

    print(report.to_string(index=False))

    # Diagnostic only: not a final feature selection.
    weak_features = report.loc[
        report["availability_pct"] < 70,
        "feature",
    ].tolist()

    print("\nFEATURES BELOW 70% AVAILABILITY")
    print(
        weak_features if weak_features else "None"
    )

    print(
        "\nThese features need investigation before "
        "we decide whether to retain or drop them."
    )


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

def main():
    print("=" * 50)
    print("AFRICAN YOUTH UNEMPLOYMENT DATA COLLECTION")
    print("=" * 50)

    dataset = build_dataset()

    dataset_path = (
        OUTPUT / "africa_youth_unemployment.csv"
    )

    dataset.to_csv(dataset_path, index=False)

    analyze_dataset(dataset)
    analyze_countries(dataset)
    analyze_features(dataset)

    print("\nFIRST FIVE DATASET ROWS")
    print("=" * 50)
    print(dataset.head().to_string(index=False))

    print("\nGENERATED FILES")
    print("=" * 50)

    for filename in [
        "africa_youth_unemployment.csv",
        "missing_values.csv",
        "country_completeness.csv",
        "feature_availability.csv",
    ]:
        print(OUTPUT / filename)

    print("\nData collection and audit completed.")


if __name__ == "__main__":
    main()
