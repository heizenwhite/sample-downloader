import requests

KAIKO_API_URL = "https://reference-data-api.kaiko.io/v1/instruments"

def validate_instruments(request):
    params = {
        "exchange_code": request.exchange_code,
        "class": request.instrument_class,
    }

    for code in request.instrument_code:
        params["code"] = code

    response = requests.get(KAIKO_API_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Kaiko API Error: {response.text}")

    data = response.json()
    valid_codes = [item["code"] for item in data["data"]]
    invalid_codes = [code for code in request.instrument_code if code not in valid_codes]

    return {"valid_codes": valid_codes, "invalid_codes": invalid_codes}
