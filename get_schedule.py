import requests
from datetime import datetime
from collections import defaultdict

BASE_URL = "https://external-api.kalshi.com/trade-api/v2"
SERIES_TICKER = "KXMLBGAME"

def date_to_ticker_fragment(date_str: str) -> str:
    """'2026-07-25' -> '26JUL25' to match Kalshi's ticker date format."""

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%y%b%d").upper()

def get_all_markets(series_ticker: str, status:str = "open"):
    all_markets = []
    cursor = None

    while True:
        params = {"series_ticker": series_ticker, "limit": 200}
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor

        resp = requests.get(f"{BASE_URL}/markets", params=params)
        resp.raise_for_status()
        data = resp.json()

        all_markets.extend(data.get("markets", []))

        cursor = data.get("cursor")

        if not cursor:
            break


    return all_markets


def get_tickers_for_date(date_str:str) -> list[str]:
    """Return every market ticker (both sides of every game) for a given date."""

    fragment = date_to_ticker_fragment(date_str)
    markets = get_all_markets(SERIES_TICKER, status = "open")
    return [m["ticker"] for m in markets if fragment in m["ticker"]]

def get_games_for_date(date_str: str) -> dict:
    """Same as above, but grouped by game (event_ticker) instead of a flat list."""
    fragment = date_to_ticker_fragment(date_str)
    markets = get_all_markets(SERIES_TICKER, status="open")

    games = defaultdict(list)

    for m in markets:
        if fragment in m["ticker"]:
            event_ticker = m.get("event_ticker", m["ticker"].rsplit("-", 1)[0])
            games[event_ticker].append(m["ticker"])

    return dict(games)

if __name__ == "__main__":
    import sys
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
 
    tickers = get_tickers_for_date(date_str)
    print(f"Found {len(tickers)} market tickers for {date_str}:\n")
    for t in tickers:
        print(t)