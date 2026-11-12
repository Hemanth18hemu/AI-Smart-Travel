import streamlit as st
import pandas as pd
import os

from recommendation import recommend_places
from image_utils import get_place_image


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="AI Smart Travel",
    page_icon="✈️",
    layout="wide"
)


# -----------------------------------------
# LOAD DATASET
# -----------------------------------------

@st.cache_data
def load_places():

    file_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "places.csv"
    )

    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    return df


places = load_places()


# -----------------------------------------
# HELPER FUNCTION
# -----------------------------------------

def find_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


# -----------------------------------------
# PAGE TITLE
# -----------------------------------------

st.title("✈️ AI Smart Travel & Place Recommendation System")

st.write(
    "Find the best tourist destinations based on "
    "your budget, travel type, and interests."
)


# -----------------------------------------
# CHECK DATASET
# -----------------------------------------

if places.empty:

    st.error(
        "Dataset not found. Please check data/places.csv."
    )

    st.stop()


city_column = find_column(
    places,
    ["city", "destination", "location"]
)

if city_column is None:

    st.error("City column not found in places.csv.")

    st.stop()


cities = sorted(
    places[city_column]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

if not cities:

    st.error("No destinations found in the dataset.")

    st.stop()


# -----------------------------------------
# LEFT SIDEBAR
# -----------------------------------------

st.sidebar.title("🧳 Plan Your Trip")

st.sidebar.write(
    "Select your travel preferences below."
)


# Destination Selection

selected_city = st.sidebar.selectbox(
    "📍 Select Destination",
    cities,
    key="selected_city"
)


# Budget Selection

budget = st.sidebar.number_input(
    "💰 Your Budget (₹)",
    min_value=0,
    max_value=1000000,
    value=2000,
    step=500,
    key="selected_budget"
)


# Travel Type Selection

travel_type = st.sidebar.selectbox(
    "👥 Travel Type",
    ["Family", "Friends", "Solo", "Couple"],
    key="selected_travel_type"
)


# Interests Selection

interests = st.sidebar.multiselect(
    "❤️ Select Your Interests",
    ["Nature", "Historical", "Adventure", "Shopping", "Food"],
    default=["Nature"],
    key="selected_interests"
)


# -----------------------------------------
# FIND PLACES BUTTON ON LEFT SIDE
# -----------------------------------------

st.sidebar.divider()

find_places = st.sidebar.button(
    "🔍 Find Places",
    type="primary",
    use_container_width=True
)


# Save selections only when the button is clicked.

if find_places:

    st.session_state["search_submitted"] = True

    st.session_state["search_city"] = selected_city

    st.session_state["search_budget"] = budget

    st.session_state["search_travel_type"] = travel_type

    st.session_state["search_interests"] = interests


# -----------------------------------------
# MAIN PAGE
# -----------------------------------------

st.divider()

st.header("🔎 Find Places Based on Your Interests")

st.write(
    "Choose your destination, budget, travel type, "
    "and interests from the left sidebar. "
    "Then click **Find Places** to discover suitable destinations."
)


# -----------------------------------------
# SHOW MESSAGE BEFORE SEARCH
# -----------------------------------------

if not st.session_state.get("search_submitted", False):

    st.info(
        "👈 Select your preferences and click "
        "**Find Places** in the left sidebar."
    )

    st.stop()


# -----------------------------------------
# USE SAVED SELECTIONS
# -----------------------------------------

selected_city = st.session_state["search_city"]

budget = st.session_state["search_budget"]

travel_type = st.session_state["search_travel_type"]

interests = st.session_state["search_interests"]

travel_types = [travel_type]


st.subheader("🌍 Your Recommended Places")

st.write(f"📍 **Destination:** {selected_city}")

st.write(f"💰 **Budget:** ₹{budget:,}")

st.write(f"👥 **Travel Type:** {travel_type}")

st.write(
    "**❤️ Interests:** "
    + (", ".join(interests) if interests else "Any interest")
)


# -----------------------------------------
# GENERATE RECOMMENDATIONS
# -----------------------------------------

try:

    recommended = recommend_places(
        selected_city,
        budget,
        travel_types,
        interests
    )

except Exception as error:

    st.error("Unable to generate recommendations.")

    st.code(str(error))

    st.stop()


if recommended is None:

    st.warning("No recommendations available.")

    st.stop()


if not isinstance(recommended, pd.DataFrame):

    recommended = pd.DataFrame(recommended)


recommended.columns = [
    str(column).strip().lower().replace(" ", "_")
    for column in recommended.columns
]


if recommended.empty:

    st.warning(
        "No matching places found. "
        "Try increasing your budget or changing your interests."
    )

    st.stop()


# -----------------------------------------
# IDENTIFY COLUMNS
# -----------------------------------------

name_column = find_column(
    recommended,
    ["name", "place_name", "place", "attraction"]
)

recommended_city_column = find_column(
    recommended,
    ["city", "destination", "location"]
)

rating_column = find_column(
    recommended,
    ["rating", "ratings", "average_rating"]
)

category_column = find_column(
    recommended,
    ["category", "type", "place_type"]
)

cost_column = find_column(
    recommended,
    [
        "estimated_budget",
        "budget",
        "estimated_cost",
        "cost",
        "price"
    ]
)


if name_column is None:

    st.error(
        "Place name column not found. "
        "Please check recommendation.py and places.csv."
    )

    st.stop()


# -----------------------------------------
# DISPLAY RECOMMENDED PLACE CARDS
# -----------------------------------------

st.success(
    f"Found {len(recommended)} recommended place(s) "
    f"for your preferences!"
)


for start in range(0, len(recommended), 2):

    columns = st.columns(2)

    for offset, column in enumerate(columns):

        index = start + offset

        if index >= len(recommended):
            break

        row = recommended.iloc[index]

        place_name = str(row[name_column])

        if recommended_city_column:

            place_city = str(row[recommended_city_column])

        else:

            place_city = selected_city


        with column:

            with st.container(border=True):

                # PLACE IMAGE

                try:

                    image_url = get_place_image(
                        place_name,
                        place_city
                    )

                    if image_url:

                        st.image(
                            image_url,
                            caption=place_name,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            f"📷 Photo not available for {place_name}"
                        )

                except Exception:

                    st.info(
                        f"📷 Photo not available for {place_name}"
                    )


                # PLACE NAME

                st.subheader(place_name)


                # LOCATION

                st.write(
                    f"📍 **Location:** {place_city}"
                )


                # CATEGORY

                if category_column:

                    category = row[category_column]

                    if pd.notna(category):

                        st.write(
                            f"🏷️ **Category:** {category}"
                        )


                # RATING

                if rating_column:

                    rating = row[rating_column]

                    if pd.notna(rating):

                        st.write(
                            f"⭐ **Rating:** {rating}/5"
                        )


                # ESTIMATED BUDGET

                if cost_column:

                    cost = row[cost_column]

                    if pd.notna(cost):

                        try:

                            st.write(
                                f"💰 **Estimated Budget:** "
                                f"₹{float(cost):,.0f}"
                            )

                        except (ValueError, TypeError):

                            st.write(
                                f"💰 **Estimated Budget:** {cost}"
                            )


                st.caption(
                    "Plan your visit and enjoy your trip!"
                )


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.caption(
    "✈️ AI Smart Travel & Place Recommendation System"
)