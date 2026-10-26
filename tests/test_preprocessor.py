"""Unit tests for data preprocessing and edge case sanitization."""

import pandas as pd

from src.data.preprocessor import (
    assign_budget_tier,
    clean_and_preprocess_dataset,
    parse_cost,
    parse_cuisines,
    parse_rating,
)


def test_parse_rating_standard():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("3.8 /5") == 3.8
    assert parse_rating("4.5") == 4.5
    assert parse_rating("5.0/5") == 5.0


def test_parse_rating_edge_cases():
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None
    assert parse_rating("Opening Soon") is None
    assert parse_rating(None) is None
    assert parse_rating("") is None


def test_parse_cost_standard():
    assert parse_cost("800") == 800
    assert parse_cost("1,200") == 1200
    assert parse_cost("2,500") == 2500
    assert parse_cost("₹500") == 500


def test_parse_cost_edge_cases():
    assert parse_cost("Free") is None
    assert parse_cost(None) is None
    assert parse_cost("0") is None
    assert parse_cost("") is None


def test_parse_cuisines():
    assert parse_cuisines("North Indian, Chinese, Italian ") == ["north indian", "chinese", "italian"]
    assert parse_cuisines("") == ["general dining"]
    assert parse_cuisines(None) == ["general dining"]


def test_assign_budget_tier():
    assert assign_budget_tier(300) == "low"
    assert assign_budget_tier(400) == "medium"
    assert assign_budget_tier(800) == "medium"
    assert assign_budget_tier(1200) == "medium"
    assert assign_budget_tier(1500) == "high"
    assert assign_budget_tier(None) == "medium"


def test_clean_and_preprocess_dataset_mock():
    mock_raw = pd.DataFrame(
        [
            {
                "url": "https://zomato.com/1",
                "address": "123 Indiranagar, Bangalore",
                "name": "Pasta Paradise",
                "online_order": "Yes",
                "book_table": "No",
                "rate": "4.2/5",
                "votes": "150",
                "location": "Indiranagar",
                "rest_type": "Cafe",
                "dish_liked": "Pizza, Ravioli",
                "cuisines": "Italian, Continental",
                "approx_cost(for two people)": "900",
            },
            {
                "url": "https://zomato.com/2",
                "address": "456 BTM, Bangalore",
                "name": "Dosa Corner",
                "online_order": "No",
                "book_table": "No",
                "rate": "NEW",
                "votes": "10",
                "location": "BTM",
                "rest_type": "Quick Bites",
                "dish_liked": "",
                "cuisines": "South Indian",
                "approx_cost(for two people)": "250",
            },
            {
                # Duplicate entry with lower votes
                "url": "https://zomato.com/3",
                "address": "123 Indiranagar, Bangalore",
                "name": "Pasta Paradise",
                "online_order": "Yes",
                "book_table": "No",
                "rate": "4.2/5",
                "votes": "50",
                "location": "Indiranagar",
                "rest_type": "Cafe",
                "dish_liked": "Pizza",
                "cuisines": "Italian",
                "approx_cost(for two people)": "900",
            },
        ]
    )

    cleaned = clean_and_preprocess_dataset(mock_raw)

    # Verifications
    assert len(cleaned) == 2  # Deduplicated from 3 to 2
    assert "restaurant_id" in cleaned.columns
    assert cleaned.iloc[0]["restaurant_id"] == "ZOM_00001"

    pasta_row = cleaned[cleaned["name"] == "Pasta Paradise"].iloc[0]
    assert pasta_row["rating"] == 4.2
    assert pasta_row["cost_for_two"] == 900
    assert pasta_row["budget_tier"] == "medium"
    assert pasta_row["online_order"] == True
    assert "italian" in pasta_row["cuisines_list"]

    dosa_row = cleaned[cleaned["name"] == "Dosa Corner"].iloc[0]
    assert dosa_row["cost_for_two"] == 250
    assert dosa_row["budget_tier"] == "low"
    assert dosa_row["rating"] > 0.0  # Imputed median rating
