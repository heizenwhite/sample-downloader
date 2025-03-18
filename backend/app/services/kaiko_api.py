# services/kaiko_api.py

import requests
from typing import List

KAIKO_API_URL = "https://reference-data-api.kaiko.io/v1/instruments"

async def validate_combinations(combinations: List[tuple]):
    """
    Validates a list of (exchange, class, code) combinations against Kaiko's reference data API.
    
    Args:
        combinations (List[tuple]): List of (exchange_code, instrument_class, instrument_code) tuples.

    Returns:
        dict: Valid and invalid combinations.
    """
    # Fetch instrument reference data from Kaiko API
    response = requests.get(KAIKO_API_URL)
    if response.status_code != 200:
        raise Exception(f"Kaiko API Error: {response.status_code} - {response.text}")

    # Extract valid combinations from API response
    data = response.json()
    valid_entries = {
        (item["exchange_code"], item["class"], item["code"]) for item in data["data"]
    }

    valid = []
    invalid = []

    for combo in combinations:
        if combo in valid_entries:
            valid.append(combo)
        else:
            invalid.append(combo)

    return {
        "valid_combinations": valid,
        "invalid_combinations": invalid
    }
