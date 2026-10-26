"""Data Ingestion Module: Downloads and caches the Zomato restaurant dataset."""

import logging

import pandas as pd

from src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def ingest_raw_data(force_download: bool = False) -> pd.DataFrame:
    """
    Downloads raw Zomato dataset from Hugging Face Hub or loads from local cache.

    Args:
        force_download: If True, re-downloads even if cached parquet exists.

    Returns:
        pd.DataFrame containing raw restaurant records.
    """
    raw_path = settings.RAW_DATA_PATH
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    if raw_path.exists() and not force_download:
        logger.info(f"Loading cached raw dataset from {raw_path}")
        df = pd.read_parquet(raw_path)
        logger.info(f"Loaded {len(df):,} raw records from local cache.")
        return df

    logger.info(f"Fetching dataset '{settings.HF_DATASET_ID}' from Hugging Face Hub...")
    try:
        from datasets import load_dataset

        dataset = load_dataset(settings.HF_DATASET_ID, split="train")
        df = dataset.to_pandas()
        logger.info(f"Downloaded {len(df):,} raw records. Saving cache to {raw_path}...")
        df.to_parquet(raw_path, index=False)
        logger.info(f"Cached raw dataset successfully at {raw_path}.")
        return df
    except Exception as e:
        logger.error(f"Failed to download dataset from Hugging Face: {e}")
        if raw_path.exists():
            logger.warning("Attempting fallback to existing local cache...")
            return pd.read_parquet(raw_path)
        raise RuntimeError(
            f"Could not download dataset '{settings.HF_DATASET_ID}' and no local cache was found."
        ) from e


if __name__ == "__main__":
    ingest_raw_data(force_download=True)
