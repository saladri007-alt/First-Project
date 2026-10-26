"""Data Preprocessing Module: Cleans, normalizes, and enriches restaurant records."""

import logging
import re

import duckdb
import pandas as pd

from src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_rating(val: str | None) -> float | None:
    """
    Parses messy rating strings like '4.1/5', '3.8 /5', 'NEW', '-', None into a clean float.
    """
    if val is None or pd.isna(val):
        return None
    val_str = str(val).strip()
    if val_str in ["NEW", "-", "Opening Soon", ""]:
        return None
    match = re.search(r"(\d+\.?\d*)\s*/\s*5", val_str)
    if match:
        try:
            rating = float(match.group(1))
            if 0.0 <= rating <= 5.0:
                return round(rating, 1)
        except ValueError:
            return None
    try:
        # Check if float directly
        rating = float(val_str)
        if 0.0 <= rating <= 5.0:
            return round(rating, 1)
    except ValueError:
        pass
    return None


def parse_cost(val: str | None) -> int | None:
    """
    Parses messy cost strings like '800', '1,200', '₹ 500' into a clean integer.
    """
    if val is None or pd.isna(val):
        return None
    digits_only = re.sub(r"[^\d]", "", str(val))
    if not digits_only:
        return None
    try:
        cost = int(digits_only)
        return cost if cost > 0 else None
    except ValueError:
        return None


def parse_cuisines(val: str | None) -> list[str]:
    """
    Parses comma-separated cuisine string into a list of normalized, trimmed lowercase strings.
    """
    if val is None or pd.isna(val):
        return ["general dining"]
    items = [c.strip().lower() for c in str(val).split(",") if c.strip()]
    return items if items else ["general dining"]


def assign_budget_tier(cost: int | None) -> str:
    """
    Maps numerical cost for two to discrete budget categories:
    - Low: < ₹400
    - Medium: ₹400 - ₹1200
    - High: > ₹1200
    """
    if cost is None:
        return "medium"
    if cost < 400:
        return "low"
    elif cost <= 1200:
        return "medium"
    else:
        return "high"


def clean_and_preprocess_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw Hugging Face Zomato dataframe into a cleaned, production-ready schema.
    """
    logger.info(f"Starting preprocessing on {len(df_raw):,} raw records...")
    df = df_raw.copy()

    # Drop rows without restaurant name
    df = df.dropna(subset=["name"])
    df["name"] = df["name"].astype(str).str.strip()

    # Parse numerical ratings
    df["rating"] = df["rate"].apply(parse_rating)
    # Calculate median rating for imputing unrated places
    median_rating = df["rating"].dropna().median()
    if pd.isna(median_rating):
        median_rating = 3.7
    df["rating_clean"] = df["rating"].fillna(round(median_rating, 1))

    # Parse votes
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)

    # Parse cost for two
    cost_col = "approx_cost(for two people)" if "approx_cost(for two people)" in df.columns else "cost"
    df["cost_for_two"] = df[cost_col].apply(parse_cost)
    median_cost = df["cost_for_two"].dropna().median()
    if pd.isna(median_cost):
        median_cost = 600
    df["cost_for_two_clean"] = df["cost_for_two"].fillna(int(median_cost)).astype(int)

    # Assign budget tier
    df["budget_tier"] = df["cost_for_two_clean"].apply(assign_budget_tier)

    # Parse and normalize cuisines
    df["cuisines_list"] = df["cuisines"].apply(parse_cuisines)
    df["cuisines_str"] = df["cuisines_list"].apply(lambda x: ", ".join([c.title() for c in x]))

    # Location normalization
    df["locality"] = df["location"].fillna(df.get("listed_in(city)", "Bangalore")).astype(str).str.strip()
    df["city"] = "Bangalore"  # Canonical city for this dataset

    # Address & rest_type
    df["address"] = df["address"].fillna("").astype(str).str.strip()
    df["rest_type"] = df["rest_type"].fillna("Casual Dining").astype(str).str.strip()
    df["dish_liked"] = df["dish_liked"].fillna("").astype(str).str.strip()
    df["online_order"] = df["online_order"].astype(str).str.lower() == "yes"
    df["book_table"] = df["book_table"].astype(str).str.lower() == "yes"
    df["url"] = df["url"].fillna("").astype(str).str.strip()

    # Deduplication: Keep highest vote entry per (name, locality)
    df = df.sort_values(by="votes", ascending=False)
    df = df.drop_duplicates(subset=["name", "locality"], keep="first")

    # Generate sequential unique restaurant IDs
    df = df.reset_index(drop=True)
    df["restaurant_id"] = [f"ZOM_{i+1:05d}" for i in range(len(df))]

    # Searchable text blob for keyword / vibe search
    df["search_text"] = (
        df["name"].str.lower() + " " +
        df["locality"].str.lower() + " " +
        df["cuisines_str"].str.lower() + " " +
        df["rest_type"].str.lower() + " " +
        df["dish_liked"].str.lower()
    )

    # Final selected columns
    output_columns = [
        "restaurant_id",
        "name",
        "city",
        "locality",
        "address",
        "rating_clean",
        "votes",
        "cost_for_two_clean",
        "budget_tier",
        "cuisines_list",
        "cuisines_str",
        "rest_type",
        "dish_liked",
        "online_order",
        "book_table",
        "url",
        "search_text",
    ]

    clean_df = df[output_columns].rename(
        columns={
            "rating_clean": "rating",
            "cost_for_two_clean": "cost_for_two",
        }
    )

    logger.info(f"Preprocessing completed! Retained {len(clean_df):,} high-quality unique restaurants.")
    return clean_df


def process_and_save_data(force: bool = False) -> pd.DataFrame:
    """
    Orchestrates ingestion, preprocessing, Parquet persistence, and DuckDB table creation.
    """
    processed_path = settings.PROCESSED_DATA_PATH
    duckdb_path = settings.DUCKDB_PATH

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    if processed_path.exists() and duckdb_path.exists() and not force:
        logger.info(f"Loading already processed data from {processed_path}")
        return pd.read_parquet(processed_path)

    from src.data.ingest import ingest_raw_data

    raw_df = ingest_raw_data()
    clean_df = clean_and_preprocess_dataset(raw_df)

    # Save to Parquet
    logger.info(f"Saving processed dataframe to {processed_path}...")
    clean_df.to_parquet(processed_path, index=False)

    # Initialize DuckDB database & table
    logger.info(f"Populating DuckDB database at {duckdb_path}...")
    conn = duckdb.connect(str(duckdb_path))
    conn.execute("DROP TABLE IF EXISTS restaurants")
    
    # Store list as string representation or native DuckDB list
    # For DuckDB compatibility, create table from clean_df
    conn.execute("CREATE TABLE restaurants AS SELECT * FROM clean_df")
    
    # Create indexes on high-frequency filter columns
    conn.execute("CREATE INDEX IF NOT EXISTS idx_city ON restaurants(city)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_locality ON restaurants(locality)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_budget ON restaurants(budget_tier)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rating ON restaurants(rating)")
    conn.close()

    logger.info(f"DuckDB tables and indexes created successfully in {duckdb_path}!")
    return clean_df


if __name__ == "__main__":
    process_and_save_data(force=True)
