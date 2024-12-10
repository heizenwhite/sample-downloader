import requests
from typing import List

KAIKO_API_URL = "https://reference-data-api.kaiko.io/v1/instruments"

async def validate_combinations(combinations: List[tuple]):
    # Collect all valid instruments from the Kaiko API
    response = requests.get(KAIKO_API_URL)
    if response.status_code != 200:
        raise Exception(f"Kaiko API Error: {response.text}")
    
    # Parse valid instruments from API response
    data = response.json()
    valid_entries = {
        (item["exchange_code"], item["class"], item["code"]) for item in data["data"]
    }
    
    # Classify combinations as valid or invalid
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