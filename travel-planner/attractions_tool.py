import requests

def search_wikipedia_attractions(city: str, max_chars: int = 0) -> str:
    """
    Searches Wikipedia for a summary of a city to find attractions.
    Input should be the city name.
    """
    # Wikipedia API Endpoint
    url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,       # Get only the intro
        "explaintext": True,   # Get plain text, not HTML
        "titles": city
    }

    headers = {
        "User-Agent": "Agentic-AI/1.0 (contact: none)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Wikipedia API Error: network error: {e}"

    # Try to parse JSON, if it's not JSON return descriptive error
    try:
        data = response.json()
    except ValueError:
        return "Wikipedia API Error: invalid JSON response from Wikipedia."

    # If a direct title lookup didn't return content, try the search API as a fallback
    pages = data.get("query", {}).get("pages", {})
    page_id = next(iter(pages), None)

    if not pages or page_id == "-1":
        # Fallback to search
        try:
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": city,
                "format": "json",
                "srlimit": 1,
            }
            sresp = requests.get(url, params=search_params, headers=headers, timeout=10)
            sresp.raise_for_status()
            sdata = sresp.json()
            search_results = sdata.get("query", {}).get("search", [])
            if not search_results:
                return f"No Wikipedia page found for {city}."

            title = search_results[0].get("title")
            # Fetch extract for the found title
            params["titles"] = title
            fresp = requests.get(url, params=params, headers=headers, timeout=10)
            fresp.raise_for_status()
            fdata = fresp.json()
            pages = fdata.get("query", {}).get("pages", {})
            page_id = next(iter(pages), None)
        except requests.RequestException as e:
            return f"Wikipedia API Error during search fallback: {e}"
        except ValueError:
            return "Wikipedia API Error: invalid JSON response during search fallback."

    if not pages or page_id is None:
        return f"No Wikipedia page found for {city}."

    extract = pages.get(page_id, {}).get("extract")
    if not extract:
        return f"No extract available for {city} on Wikipedia."

    # If max_chars > 0, return a truncated extract, otherwise return full extract
    if max_chars and isinstance(max_chars, int) and max_chars > 0:
        return f"Wikipedia Summary for {city}: {extract[:max_chars]}..."

    return f"Wikipedia Summary for {city}: {extract}"