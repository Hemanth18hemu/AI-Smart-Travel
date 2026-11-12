import requests
import streamlit as st


@st.cache_data(ttl=86400)
def get_place_image(place_name, city=""):

    api_url = "https://commons.wikimedia.org/w/api.php"

    headers = {
        "User-Agent": "AISmartTravelProject/1.0"
    }

    search_terms = [
        f'"{place_name}" "{city}"',
        f'"{place_name}"',
        f"{place_name} {city} tourism"
    ]

    for search_term in search_terms:

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_term,
            "gsrnamespace": 6,
            "gsrlimit": 10,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 600,
            "format": "json"
        }

        try:
            response = requests.get(
                api_url,
                params=params,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            pages = data.get(
                "query", {}
            ).get("pages", {})

            for page in pages.values():

                image_info = page.get("imageinfo", [])

                if not image_info:
                    continue

                image = image_info[0]

                image_url = image.get("thumburl")

                if image_url:
                    return image_url

                image_url = image.get("url")

                if image_url:
                    return image_url

        except (requests.RequestException, ValueError) as error:
            print("Image search failed:", error)

    return None