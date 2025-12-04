import os
import re
from dotenv import load_dotenv
import json
from typing import Tuple, Optional
from jsonschema import validate, ValidationError

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


# --- Optional LLM decision-maker ---
llm = None
LLM_AVAILABLE = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    if GOOGLE_API_KEY:
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5", temperature=0)
            LLM_AVAILABLE = True
        except Exception:
            # If the class exists but instantiation fails, keep fallback
            LLM_AVAILABLE = False
    else:
        LLM_AVAILABLE = False
except Exception:
    LLM_AVAILABLE = False


def _call_llm_for_action(text: str) -> Tuple[str, str]:
    """Ask the LLM which action to take and return (action, action_input).
    Returns action='none' if LLM cannot decide. This function is best-effort
    and will return ('none','') on failure so the caller can fallback to heuristics.
    """
    if not LLM_AVAILABLE or llm is None:
        return "none", ""

    prompt = (
        "You are a tool selector. Available tools:\n"
        "1) weather - input should be a city name (e.g., 'Tokyo')\n"
        "2) currency - input must be 'AMOUNT FROM TO' (e.g., '100 USD EUR')\n"
        "3) attractions - input should be a city name to fetch attractions from Wikipedia\n\n"
        "Given the user's request, choose exactly one action and provide the action input.\n"
        "Return only a JSON object with keys: action and input.\n"
        "action must be one of: 'weather','currency','attractions','none'.\n\n"
        "User request: \n" + text + "\n\n"
        "Respond with only JSON. Example: {\"action\": \"weather\", \"input\": \"Paris\"}"
    )

    # Try a few common call patterns for ChatGoogleGenerativeAI
    llm_response_text = None
    try:
        if hasattr(llm, "predict"):
            llm_response_text = llm.predict(prompt)
        else:
            # Many LangChain LLM wrappers support __call__
            llm_response_text = llm(prompt)
    except Exception:
        try:
            # Last-resort: try a generate style call
            resp = llm.generate([prompt])
            # Attempt to extract text from common shapes
            if hasattr(resp, "generations") and resp.generations:
                gen = resp.generations[0]
                if isinstance(gen, list) and gen:
                    llm_response_text = getattr(gen[0], "text", None) or getattr(gen[0], "message", None)
                else:
                    llm_response_text = getattr(gen, "text", None) or getattr(gen, "message", None)
        except Exception:
            llm_response_text = None

    if not llm_response_text:
        return "none", ""

    # Use schema-validated parser to extract JSON safely
    try:
        return parse_llm_json(llm_response_text)
    except Exception:
        return "none", ""


ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["weather","currency","attractions","none"]},
        "input": {"type": "string"}
    },
    "required": ["action","input"]
}


def parse_llm_json(text: str) -> Tuple[str,str]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return "none", ""
    try:
        parsed = json.loads(text[start:end+1])
        validate(parsed, ACTION_SCHEMA)
        return parsed["action"], parsed["input"]
    except (json.JSONDecodeError, ValidationError, TypeError):
        return "none", ""


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

            # If LLM is available, ask it which tool to call. Otherwise use heuristics.
            action = "none"
            action_input = ""
            if LLM_AVAILABLE:
                action, action_input = _call_llm_for_action(text)

            # If LLM didn't decide, fall back to heuristics
            if action == "none":
                # Currency queries
                if _is_currency_query(text):
                    action = "currency"
                    m = re.search(r"([0-9]+(\.[0-9]+)?)\s*([A-Za-z]{3})\b.*([A-Za-z]{3})", text)
                    if m:
                        amt = m.group(1)
                        frm = m.group(3).upper()
                        to = m.group(4).upper()
                        action_input = f"{amt} {frm} {to}"
                    else:
                        action_input = text
                # Weather queries
                elif re.search(r"weather|temperature|rain|forecast", text, re.IGNORECASE):
                    action = "weather"
                    action_input = _extract_city(text)
                # Attractions / things to do
                elif re.search(r"attraction|attractions|things to do|sights|visit", text, re.IGNORECASE):
                    action = "attractions"
                    action_input = _extract_city(text)
                # Default: short inputs -> treat as attractions/city lookup
                elif len(text.split()) <= 3:
                    action = "attractions"
                    action_input = _extract_city(text)
                else:
                    action = "none"

            # Execute the chosen action
            if action == "currency":
                print("\n🔁 Converting currency...")
                result = convert_currency(action_input)
                print(f"\n✅ Result: {result}")
                continue

            if action == "weather":
                city = action_input or _extract_city(text)
                print(f"\n🔁 Fetching weather for {city}...")
                result = get_real_weather(city)
                print(f"\n✅ Result: {result}")
                continue

            if action == "attractions":
                city = action_input or _extract_city(text)
                print(f"\n🔁 Searching attractions for {city}...")
                result = search_wikipedia_attractions(city)
                print(f"\n✅ Result: {result}")
                continue

            print("I couldn't determine intent. Try: '100 USD EUR', 'weather in Tokyo', or 'attractions in Paris'.")
            

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()