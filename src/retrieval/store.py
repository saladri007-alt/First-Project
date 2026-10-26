"""Data access layer and DuckDB database connection manager."""

import logging
from typing import Any

import duckdb

from src.config import settings

logger = logging.getLogger(__name__)


class RestaurantStore:
    """Manages DuckDB connections and basic table queries."""

    def __init__(self, db_path: str | None = None):
        self.db_path = str(db_path or settings.DUCKDB_PATH)

    def get_connection(self, read_only: bool = True) -> duckdb.DuckDBPyConnection:
        """Returns a DuckDB connection."""
        return duckdb.connect(self.db_path, read_only=read_only)

    def get_all_localities(self) -> list[str]:
        """Returns list of unique localities sorted alphabetically."""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT DISTINCT locality FROM restaurants WHERE locality IS NOT NULL AND locality != '' ORDER BY locality"
            ).fetchall()
            return [row[0] for row in result]

    def get_all_cuisines(self) -> list[str]:
        """Returns list of all unique cuisines sorted by frequency."""
        with self.get_connection() as conn:
            # Unnest or query cuisines
            df = conn.execute("SELECT cuisines_str FROM restaurants").df()
            cuisine_counts: dict[str, int] = {}
            for row in df["cuisines_str"].dropna():
                for c in str(row).split(","):
                    c_clean = c.strip().title()
                    if c_clean:
                        cuisine_counts[c_clean] = cuisine_counts.get(c_clean, 0) + 1
            sorted_cuisines = sorted(cuisine_counts.keys(), key=lambda k: cuisine_counts[k], reverse=True)
            return sorted_cuisines

    def get_restaurant_by_id(self, restaurant_id: str) -> dict[str, Any] | None:
        """Retrieves a single restaurant by ID."""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT * FROM restaurants WHERE restaurant_id = ?", [restaurant_id]
            ).fetchdf()
            if result.empty:
                return None
            return result.iloc[0].to_dict()

    def get_stats(self) -> dict[str, Any]:
        """Returns dataset statistics."""
        with self.get_connection() as conn:
            total_count = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
            avg_rating = conn.execute("SELECT AVG(rating) FROM restaurants").fetchone()[0]
            avg_cost = conn.execute("SELECT AVG(cost_for_two) FROM restaurants").fetchone()[0]
            return {
                "total_restaurants": total_count,
                "average_rating": round(avg_rating, 2) if avg_rating else 0.0,
                "average_cost_for_two": round(avg_cost, 0) if avg_cost else 0,
            }


# Default singleton instance
store = RestaurantStore()
