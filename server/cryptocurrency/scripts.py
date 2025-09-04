import requests
import time
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_current_price_and_daily_change(coin_name, currency="usd"):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": currency.lower(), "ids": coin_name.lower()}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        price = data[0]["current_price"]
        change = data[0]["price_change_percentage_24h"]
        return {"price": price, "change_percentage": change}
    except requests.RequestException as e:
        return {"error": str(e)}


def get_multiple_currencies_prices(coin_ids, currency="usd"):
    """
    Get prices for multiple cryptocurrencies in a single API call to avoid rate limiting
    
    Args:
        coin_ids: List of CoinGecko coin IDs
        currency: vs_currency parameter (default: usd)
    
    Returns:
        Dictionary mapping coin_id to price data or error
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    # CoinGecko allows up to 250 coins per request, but we'll use smaller batches
    batch_size = 50
    results = {}

    # Split coin_ids into batches
    for i in range(0, len(coin_ids), batch_size):
        batch = coin_ids[i:i + batch_size]
        ids_param = ",".join(batch)

        params = {
            "vs_currency": currency.lower(),
            "ids": ids_param,
            "order": "id",
            "per_page": batch_size,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }

        max_retries = 3
        retry_delay = 5  # Start with 5 seconds

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params)

                if response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        print(f"Rate limited, waiting {retry_delay} seconds before retry {attempt + 1}")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise requests.HTTPError(f"Rate limit exceeded after {max_retries} attempts")

                response.raise_for_status()
                data = response.json()

                # Process each coin in the response
                for coin_data in data:
                    coin_id = coin_data.get("id")
                    if coin_id:
                        results[coin_id] = {
                            "price": coin_data.get("current_price"),
                            "change_percentage": coin_data.get("price_change_percentage_24h")
                        }

                # Add entries for coins that weren't found in the response
                response_coin_ids = {coin_data.get("id") for coin_data in data}
                for coin_id in batch:
                    if coin_id not in response_coin_ids:
                        results[coin_id] = {"error": f"Coin '{coin_id}' not found"}

                break  # Success, break out of retry loop

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Request failed, retrying in {retry_delay} seconds: {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    # If all retries failed, mark all coins in batch as errors
                    for coin_id in batch:
                        results[coin_id] = {"error": str(e)}

        # Add longer delay between batch requests for rate limiting
        if i + batch_size < len(coin_ids):
            time.sleep(10)  # 10 second delay between batches

    return results


def get_historical_price_data(coin_name, start_time, end_time, step_seconds, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_name.lower()}/market_chart/range"
    prices = []
    try:
        params = {"vs_currency": currency.lower(), "from": int(start_time), "to": int(end_time)}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        raw_prices = data.get("prices", [])
        interval_start = start_time
        while interval_start < end_time:
            interval_end = interval_start + step_seconds
            segment = [price for ts, price in raw_prices if interval_start * 1000 <= ts < interval_end * 1000]
            if segment:
                o, c = segment[0], segment[-1]
                mn, mx = min(segment), max(segment)
            else:
                o = c = mn = mx = None
            prices.append({"start_time": interval_start, "end_time": interval_end,
                           "min": mn, "max": mx, "open": o, "close": c})
            interval_start = interval_end
        return prices
    except requests.RequestException as e:
        return {"error": str(e)}


def plot_ict_chart(candles, time_format, fvg=[], turtle_signals=[]):
    times = [datetime.fromtimestamp(c["timestamp"], timezone.utc) for c in candles]
    opens = [c["open"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]

    fig, ax = plt.subplots(figsize=(14, 6))

    # Plot candle wicks and bodies
    for i in range(len(candles)):
        color = "green" if closes[i] >= opens[i] else "red"
        ax.plot([times[i], times[i]], [lows[i], highs[i]], color=color, linewidth=1)
        ax.plot([times[i], times[i]], [opens[i], closes[i]], color=color, linewidth=4)

    # Plot FVGs
    for idx, f in enumerate(fvg):
        ax.axhspan(f["fvg_low"], f["fvg_high"], alpha=0.3,
                   color='blue' if f["type"] == "bullish" else 'orange')

    # Plot Turtle Soup signals
    for ts in turtle_signals:
        t = times[ts["index"]]
        lvl = ts["level"]
        if ts["type"] == "bearish_turtle_soup":
            ax.plot(t, lvl, marker='x', markersize=10, color='magenta')
        else:
            ax.plot(t, lvl, marker='x', markersize=10, color='gray')

    if fvg:
        strategy = 'Fair Value Gaps'
    else:
        strategy = 'Turtle Soup'

    # Formatting
    ax.set_title(f"ICT Chart with {strategy} strategy")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter(time_format))
    plt.grid(True)
    plt.tight_layout()
    return plt


def detect_fvg(candles):
    fvg_list = []
    for i in range(2, len(candles)):
        p2, cur = candles[i - 2], candles[i]
        if cur["low"] > p2["high"]:
            fvg_list.append({"index": i, "type": "bullish", "fvg_low": p2["high"], "fvg_high": cur["low"]})
        elif cur["high"] < p2["low"]:
            fvg_list.append({"index": i, "type": "bearish", "fvg_high": p2["low"], "fvg_low": cur["high"]})
    return fvg_list


def detect_turtle_soup(candles, lookback=5):
    signals = []
    for i in range(lookback, len(candles)):
        highs = [c["high"] for c in candles[i - lookback:i]]
        prev_high = max(highs)
        if candles[i]["high"] > prev_high and candles[i]["close"] < prev_high:
            signals.append({"index": i, "type": "bearish_turtle_soup", "level": prev_high})
        lows = [c["low"] for c in candles[i - lookback:i]]
        prev_low = min(lows)
        if candles[i]["low"] < prev_low and candles[i]["close"] > prev_low:
            signals.append({"index": i, "type": "bullish_turtle_soup", "level": prev_low})
    return signals


def get_candles(raw):
    candles = [
        {"timestamp": itm["start_time"], "open": itm["open"], "high": itm["max"],
         "low": itm["min"], "close": itm["close"]}
        for itm in raw if all(v is not None for v in [itm["open"], itm["close"], itm["min"], itm["max"]])
    ]
    return candles

def get_time_format(duration):
    if duration <= 604800:
        return "%H:%M" #time
    else:
        return "%m/%d" #day and month
