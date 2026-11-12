import os
import pandas as pd


def recommend_places(selected_city, budget, travel_types=None, interests=None):

    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "places.csv"
    )

    places = pd.read_csv(file_path)

    places.columns = places.columns.str.strip().str.lower()

    places = places.dropna(subset=["name", "city"]).copy()

    places["city"] = places["city"].astype(str).str.strip()

    city = str(selected_city).strip().lower()

    city_aliases = {
        "bengaluru": "bangalore",
        "bangalore": "bangalore",
        "mysuru": "mysore",
        "mysore": "mysore"
    }

    selected_city = city_aliases.get(city, city)

    places["_city"] = places["city"].str.lower().map(
        lambda x: city_aliases.get(x, x)
    )

    result = places[places["_city"] == selected_city].copy()

    if result.empty:
        return result

    # Budget filtering
    if "budget" in result.columns:

        budget_values = result["budget"].astype(str).str.strip().str.lower()

        budget_mapping = {
            "low": 500,
            "medium": 1000,
            "high": 2000
        }

        numeric_values = pd.to_numeric(
            result["budget"], errors="coerce"
        )

        mapped_values = budget_values.map(budget_mapping)

        result["_estimated_budget"] = numeric_values.fillna(mapped_values)

        result = result[
            result["_estimated_budget"].notna()
            & (result["_estimated_budget"] <= budget)
        ].copy()

    else:
        result["_estimated_budget"] = 0

    if result.empty:
        return result

    # Recognize common true values in the dataset.
    def is_selected(value):
        return str(value).strip().lower() in [
            "1", "1.0", "true", "yes"
        ]

    # Filter by travel type when matching columns exist.
    if travel_types:

        selected_columns = [
            item.lower()
            for item in travel_types
            if item.lower() in result.columns
        ]

        if selected_columns:
            mask = result[selected_columns].apply(
                lambda row: any(is_selected(value) for value in row),
                axis=1
            )

            result = result[mask].copy()

    if result.empty:
        return result

    # Filter by interests when matching columns exist.
    if interests:

        selected_columns = [
            item.lower()
            for item in interests
            if item.lower() in result.columns
        ]

        if selected_columns:
            mask = result[selected_columns].apply(
                lambda row: any(is_selected(value) for value in row),
                axis=1
            )

            result = result[mask].copy()

    # Sort by rating.
    if "rating" in result.columns:
        result["rating"] = pd.to_numeric(
            result["rating"], errors="coerce"
        )

        result = result.sort_values(
            "rating",
            ascending=False,
            na_position="last"
        )

    result["estimated_budget"] = result["_estimated_budget"]

    return result.drop(
        columns=["_city", "_estimated_budget"],
        errors="ignore"
    ).reset_index(drop=True)