# services/prefix_generator.py

from datetime import datetime, timedelta
from typing import List


def generate_prefixes(
    product: str,
    exchange_code: List[str],
    instrument_class: List[str] = None,
    instrument_code: List[str] = None,
    index_code: List[str] = None,
    granularity: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
) -> List[str]:
    """
    Generate bucket prefixes dynamically based on the product and input parameters.
    Returns a list of prefixes for download.

    Args:
        product (str): Product type (e.g., Trades, OHLCV, Indices, etc.)
        exchange_code (List[str]): Exchange codes.
        instrument_class (List[str]): Instrument classes.
        instrument_code (List[str]): Instrument codes.
        index_code (List[str]): Index codes for Indices products.
        granularity (str): Time granularity for some products.
        start_date (datetime): Start date.
        end_date (datetime): End date.

    Returns:
        List[str]: List of bucket prefixes.
    """
    prefixes = []
    date_range = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((end_date - start_date).days + 1)
    ]

    # For Index and Index Multi-Asset (Wasabi bucket)
    if product in ["Index", "Index Multi-Asset"]:
        for date in date_range:
            for index in index_code:
                pt = "PT5S"
                if any(x in index.upper() for x in ["LDN", "NYC", "SGP"]):
                    pt = "PT24H"
                elif "1S" in index.upper():
                    pt = "PT1S"
                elif "RT" in index.upper():
                    pt = "PT1H"

                index_type = "index_fixing" if any(x in index.upper() for x in ["LDN", "NYC", "SGP"]) else "real_time"
                date_part = date[:7] if pt in ["PT24H", "PT1H"] else date

                prefixes.append(
                    f"indices-backfill/index_v1/v1/extensive/{index.lower()}/{index_type}/{pt}/{index.lower()}_{index_type}_vwm_twap_100_{date_part}.csv.gz"
                )

    # For S3-based products like Trades, Order Book Snapshots, etc.
    elif product in ["Order Book Snapshots", "Full Order Book", "Top Of Book", "Trades", "Derivatives"]:
        for date in date_range:
            year_month = date[:7]
            for exch in exchange_code:
                for instr_class in instrument_class:
                    for instr_code in instrument_code:
                        prefixes.append(
                            f"{product.lower().replace(' ', '_')}/{exch}/{instr_class}/{instr_code}/{year_month}/{product.lower().replace(' ', '_')}_{exch}_{instr_class}_{instr_code}_{date}.csv.gz"
                        )

    # For OHLCV / VWAP products requiring granularity
    elif product in ["COHLCVVWAP", "OHLCV", "VWAP"]:
        if not granularity:
            raise ValueError("Granularity must be specified for this product.")
        for date in date_range:
            year_folder = date[:4] if granularity in ["1d_per_year", "4h_per_year", "1h_per_year"] else date[:7]
            for exch in exchange_code:
                for instr_class in instrument_class:
                    for instr_code in instrument_code:
                        prefixes.append(
                            f"{product.lower()}/{granularity}/{exch}/{instr_class}/{instr_code}/{year_folder}/{product.lower().replace(' ', '_')}_{exch}_{instr_class}_{instr_code}_{date}.csv.gz"
                        )
    else:
        raise ValueError(f"Unsupported product type: {product}")

    return prefixes
