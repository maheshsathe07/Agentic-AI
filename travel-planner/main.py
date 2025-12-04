import os
import re
from dotenv import load_dotenv

# Import our custom tools from separate files
from weather_tool import get_real_weather
from currency_tool import convert_currency
from attractions_tool import search_wikipedia_attractions

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ Warning: GOOGLE_API_KEY is not set. LLM features are disabled.")

if not OPENWEATHER_API_KEY:
    print("⚠️ Warning: OPENWEATHER_API_KEY is missing. Weather tool may fail.")


def _extract_city(text: str) -> str:
    """Try to extract a city name from user input using simple heuristics."""
    # Look for patterns like 'in Paris' or 'weather Paris' or 'Paris, France'
    m = re.search(r"in\s+([A-Za-z \-]+)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # If input is like 'weather Paris' or 'Paris attractions'
    tokens = text.split()
    if len(tokens) == 1:
        return tokens[0]

    # fallback: last token if looks like a word
    last = tokens[-1].strip() if tokens else ""
    return last


def _is_currency_query(text: str) -> bool:
    # Patterns: '100 USD EUR' or 'convert 100 USD to EUR'
    if re.search(r"\bconvert\b", text, re.IGNORECASE) and re.search(r"[A-Za-z]{3}\b", text):
        return True
    parts = text.split()
    return len(parts) == 3 and _looks_like_amount(parts[0]) and parts[1].isalpha() and parts[2].isalpha()


def _looks_like_amount(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False


def main():
    print("--- 🌍 Simple Travel Assistant (no LangChain agent) ---")
    print("Type 'quit' to exit.")

    while True:
        user_input = input("\nWhere do you want to go? (or ask about currency/weather/attractions): ")
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            break

        try:
            text = user_input.strip()

            # Currency queries
            if _is_currency_query(text):
                # Allow inputs like 'convert 100 USD to EUR' -> extract numeric and currency codes
                m = re.search(r"([0-9]+(\.[0-9]+)?)\s*([A-Za-z]{3})\b.*([A-Za-z]{3})", text)
                if m:
                    amt = m.group(1)
                    frm = m.group(3).upper()
                    to = m.group(4).upper()
                    query = f"{amt} {frm} {to}"
                else:
                    query = text
                print("\n🔁 Converting currency...")
                result = convert_currency(query)
                print(f"\n✅ Result: {result}")
                continue

            # Weather queries
            if re.search(r"weather|temperature|rain|forecast", text, re.IGNORECASE):
                city = _extract_city(text)
                print(f"\n🔁 Fetching weather for {city}...")
                result = get_real_weather(city)
                print(f"\n✅ Result: {result}")
                continue

            # Attractions / things to do
            if re.search(r"attraction|attractions|things to do|sights|visit", text, re.IGNORECASE):
                city = _extract_city(text)
                print(f"\n🔁 Searching attractions for {city}...")
                result = search_wikipedia_attractions(city)
                print(f"\n✅ Result: {result}")
                continue

            # Default: try attractions for single-word inputs (city names)
            if len(text.split()) <= 3:
                city = _extract_city(text)
                print(f"\n🔁 Looking up general information for {city}...")
                result = search_wikipedia_attractions(city)
                print(f"\n✅ Result: {result}")
                continue

            print("I couldn't determine intent. Try: '100 USD EUR', 'weather in Tokyo', or 'attractions in Paris'.")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()