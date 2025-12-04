import requests

def convert_currency(amount_and_currencies: str) -> str:
    """
    Converts currency using real-time exchange rates.
    Input format must be 'AMOUNT FROM_CURRENCY TO_CURRENCY' (e.g., '100 USD EUR').
    Supported currencies: USD, EUR, JPY, GBP, AUD, CAD, CHF, CNY, INR.
    """
    try:
        parts = amount_and_currencies.split()
        if len(parts) != 3:
            return "Error: Input must be 'AMOUNT FROM TO' (e.g., '100 USD EUR')"
        
        amount, base_currency, target_currency = parts
        base_currency = base_currency.upper()
        target_currency = target_currency.upper()

        # Frankfurter API endpoint (No key required)
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={base_currency}&to={target_currency}"
        
        response = requests.get(url)
        data = response.json()

        if "rates" in data:
            converted_amount = data["rates"][target_currency]
            return f"{amount} {base_currency} is currently {converted_amount} {target_currency}."
        else:
            return f"Error: Could not convert {base_currency} to {target_currency}. Check currency codes."

    except Exception as e:
        return f"Currency API Error: {str(e)}"