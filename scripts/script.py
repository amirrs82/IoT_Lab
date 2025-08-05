import time
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_ict_chart(candles, fvg=[], order_blocks=[], sweeps=[]):
    times = [datetime.utcfromtimestamp(c["timestamp"]) for c in candles]
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
    for f in fvg:
        t = times[f["index"]]
        ax.axhspan(f["fvg_low"], f["fvg_high"], alpha=0.3,
                   color='blue' if f["type"] == "bullish" else 'orange',
                   label=f"{f['type'].capitalize()} FVG" if f["index"] == fvg[0]["index"] else "")

    # Plot Order Blocks
    for ob in order_blocks:
        start_time = times[ob["index"]]
        ax.hlines(ob["price_range"][0], start_time, times[-1], colors='purple',
                  linestyle='--', linewidth=1, label="Order Block" if ob == order_blocks[0] else "")

    # Plot Liquidity Sweeps
    for s in sweeps:
        t = times[s["index"]]
        level = s["level"]
        color = 'black' if s["type"] == "sell-side" else 'gold'
        ax.plot(t, level, marker='o', color=color, label=s["type"].capitalize() if s == sweeps[0] else "")

    # Formatting
    ax.set_title("ICT Chart: Candles + FVG + Order Blocks + Sweeps")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.legend(loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def get_current_price_and_daily_change(coin_name, currency="usd"):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": currency.lower(),
        "ids": coin_name.lower(),
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None

        price = data[0]["current_price"]
        change_percentage = data[0]["price_change_percentage_24h"]

        return {
            "price": price,
            "change_percentage": change_percentage
        }
    except requests.RequestException as e:
        return {"error": str(e)}


def get_historical_price_data(coin_name, start_time, end_time, step_seconds, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_name.lower()}/market_chart/range"

    prices = []
    try:
        params = {
            "vs_currency": currency.lower(),
            "from": int(start_time),
            "to": int(end_time)
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        raw_prices = data.get("prices", [])  # list of [timestamp, price]

        # Step-based aggregation
        interval_start = start_time
        while interval_start < end_time:
            interval_end = interval_start + step_seconds
            segment = [
                price for timestamp, price in raw_prices
                if interval_start * 1000 <= timestamp < interval_end * 1000
            ]

            if segment:
                min_price = min(segment)
                max_price = max(segment)
                open_price = segment[0]
                close_price = segment[-1]
            else:
                min_price = max_price = open_price = close_price = None

            prices.append({
                "start_time": interval_start,
                "end_time": interval_end,
                "min": min_price,
                "max": max_price,
                "open": open_price,
                "close": close_price
            })

            interval_start = interval_end

        return prices

    except requests.RequestException as e:
        return {"error": str(e)}



def detect_fvg(candles):
    """
    Detect Fair Value Gaps (FVG) in OHLCV data.
    :param candles: list of dicts with keys: ['open', 'high', 'low', 'close']
    :return: List of FVG entries: {'index': i, 'fvg_high': x, 'fvg_low': y}
    """
    fvg_list = []
    for i in range(2, len(candles)):
        prev2 = candles[i - 2]
        prev1 = candles[i - 1]
        current = candles[i]

        # Bullish FVG: low of current > high of two candles ago
        if current["low"] > prev2["high"]:
            fvg_list.append({
                "index": i,
                "type": "bullish",
                "fvg_low": prev2["high"],
                "fvg_high": current["low"]
            })

        # Bearish FVG: high of current < low of two candles ago
        elif current["high"] < prev2["low"]:
            fvg_list.append({
                "index": i,
                "type": "bearish",
                "fvg_high": prev2["low"],
                "fvg_low": current["high"]
            })

    return fvg_list


def detect_order_blocks(candles, threshold=1.5):
    """
    Detects bullish/bearish order blocks based on momentum.
    """
    order_blocks = []
    for i in range(len(candles) - 1):
        curr = candles[i]
        next_candle = candles[i + 1]
        body_size = abs(curr["close"] - curr["open"])
        move_size = abs(next_candle["close"] - curr["close"])
        if move_size > body_size * threshold:
            block_type = "bullish" if next_candle["close"] > curr["close"] else "bearish"
            order_blocks.append({
                "index": i,
                "type": block_type,
                "price_range": (min(curr["open"], curr["close"]), max(curr["open"], curr["close"]))
            })
    return order_blocks


def detect_liquidity_sweeps(candles, lookback=5):
    """
    Detect wicks that sweep recent highs/lows.
    """
    sweeps = []
    for i in range(lookback, len(candles)):
        prev_highs = [c["high"] for c in candles[i - lookback:i]]
        prev_lows = [c["low"] for c in candles[i - lookback:i]]
        current = candles[i]
        if current["high"] > max(prev_highs):
            sweeps.append({"index": i, "type": "buy-side", "level": max(prev_highs)})
        elif current["low"] < min(prev_lows):
            sweeps.append({"index": i, "type": "sell-side", "level": min(prev_lows)})
    return sweeps


def calculate_equilibrium(high, low):
    return (high + low) / 2


def detect_structure_breaks(candles):
    structure = []
    for i in range(2, len(candles)):
        if (candles[i-2]["high"] < candles[i-1]["high"] and 
            candles[i]["high"] > candles[i-1]["high"]):
            structure.append({"index": i, "type": "bullish_BOS", "level": candles[i]["high"]})
        elif (candles[i-2]["low"] > candles[i-1]["low"] and 
              candles[i]["low"] < candles[i-1]["low"]):
            structure.append({"index": i, "type": "bearish_BOS", "level": candles[i]["low"]})
    return structure


def is_in_session(timestamp, session="london"):
    dt = datetime.utcfromtimestamp(timestamp)
    hour = dt.hour
    if session == "london":
        return 7 <= hour < 11
    elif session == "new_york":
        return 12 <= hour < 16
    elif session == "asia":
        return 0 <= hour < 5
    return False


def main():
    import pprint

    coin = input("Enter coin name (e.g., bitcoin): ").strip()
    duration = int(input("Enter duration in seconds (e.g., 3600): ").strip())
    step = int(input("Enter step size in seconds (e.g., 300): ").strip())
    
    end_time = int(time.time())
    start_time = end_time - duration

    print("\nFetching historical data...")
    ohlcv_data = get_historical_price_data(coin, start_time, end_time, step)

    if "error" in ohlcv_data:
        print("Error fetching price data:", ohlcv_data["error"])
        return

    # Filter out empty/None entries and convert to OHLCV-like structure
    candles = []
    for item in ohlcv_data:
        if all(v is not None for v in [item["open"], item["close"], item["min"], item["max"]]):
            candles.append({
                "timestamp": item["start_time"],
                "open": item["open"],
                "high": item["max"],
                "low": item["min"],
                "close": item["close"]
            })

    if not candles:
        print("No valid candle data found.")
        return

    print(f"Processed {len(candles)} candles.")

    # Detect ICT signals
    fvg = detect_fvg(candles)
    order_blocks = detect_order_blocks(candles)
    sweeps = detect_liquidity_sweeps(candles)
    structure = detect_structure_breaks(candles)

    # Get current price & change
    print("\nCurrent Price Info:")
    price_info = get_current_price_and_daily_change(coin)
    if "error" in price_info:
        print("Error:", price_info["error"])
    else:
        print(f"Current Price: {price_info['price']} {coin.upper()}")
        print(f"24h Change: {price_info['change_percentage']}%")

    # Show results
    print("\n--- Fair Value Gaps (FVG) ---")
    pprint.pprint(fvg[:5])  # Print first 5 only for brevity

    print("\n--- Order Blocks ---")
    pprint.pprint(order_blocks[:5])

    print("\n--- Liquidity Sweeps ---")
    pprint.pprint(sweeps[:5])

    print("\n--- Structure Breaks ---")
    pprint.pprint(structure[:5])

    print("\n--- Session Info ---")
    for c in candles[-5:]:  # check session for last 5 candles
        session_flags = {
            "London": is_in_session(c["timestamp"], "london"),
            "New York": is_in_session(c["timestamp"], "new_york"),
            "Asia": is_in_session(c["timestamp"], "asia")
        }
        print(datetime.utcfromtimestamp(c["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"), session_flags)
        
    print("\nPlotting chart...")
    plot_ict_chart(candles, fvg, order_blocks, sweeps)



if __name__ == "__main__":
    main()