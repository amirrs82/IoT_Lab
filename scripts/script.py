import time
import requests
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_ict_chart(candles, fvg=[], order_blocks=[], sweeps=[], turtle_signals=[], ote_zones=[]):
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

    # Plot Order Blocks
    for ob in order_blocks:
        start_time = times[ob["index"]]
        ax.hlines(ob["price_range"][0], start_time, times[-1], colors='purple',
                  linestyle='--', linewidth=1)

    # Plot Liquidity Sweeps
    for s in sweeps:
        t = times[s["index"]]
        level = s["level"]
        color = 'black' if s["type"] == "sell-side" else 'gold'
        ax.plot(t, level, marker='o', color=color)

    # Plot Turtle Soup signals
    for ts in turtle_signals:
        t = times[ts["index"]]
        lvl = ts["level"]
        ax.plot(t, lvl, marker='x', markersize=10, color='magenta')

    # Plot OTE zones
    for ote in ote_zones:
        idx = ote["index"]
        swing = ote.get("swing_low", ote.get("swing_high"))
        entry = ote["entry"]
        ax.axhspan(min(swing, entry), max(swing, entry), alpha=0.2, color='cyan')

    # Formatting
    ax.set_title("ICT Chart: Complete Toolkit + Strategies")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("ict_chart.png")
    print("Chart saved as ict_chart.png. You can open it from Windows.")


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
            segment = [price for ts, price in raw_prices if interval_start*1000 <= ts < interval_end*1000]
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


def detect_fvg(candles):
    fvg_list = []
    for i in range(2, len(candles)):
        p2, p1, cur = candles[i-2], candles[i-1], candles[i]
        if cur["low"] > p2["high"]:
            fvg_list.append({"index": i, "type": "bullish", "fvg_low": p2["high"], "fvg_high": cur["low"]})
        elif cur["high"] < p2["low"]:
            fvg_list.append({"index": i, "type": "bearish", "fvg_high": p2["low"], "fvg_low": cur["high"]})
    return fvg_list


def detect_order_blocks(candles, threshold=1.5):
    obs = []
    for i in range(len(candles)-1):
        curr, nxt = candles[i], candles[i+1]
        body = abs(curr["close"] - curr["open"])
        move = abs(nxt["close"] - curr["close"])
        if move > body*threshold:
            t = "bullish" if nxt["close"] > curr["close"] else "bearish"
            obs.append({"index": i, "type": t,
                        "price_range": (min(curr["open"], curr["close"]), max(curr["open"], curr["close"]))})
    return obs


def detect_liquidity_sweeps(candles, lookback=5):
    sweeps = []
    for i in range(lookback, len(candles)):
        high_lvl, low_lvl = max(c["high"] for c in candles[i-lookback:i]), min(c["low"] for c in candles[i-lookback:i])
        cur = candles[i]
        if cur["high"] > high_lvl:
            sweeps.append({"index": i, "type": "buy-side", "level": high_lvl})
        elif cur["low"] < low_lvl:
            sweeps.append({"index": i, "type": "sell-side", "level": low_lvl})
    return sweeps


def detect_structure_breaks(candles):
    structure = []
    for i in range(2, len(candles)):
        if candles[i-2]["high"] < candles[i-1]["high"] < candles[i]["high"]:
            structure.append({"index": i, "type": "bullish_BOS", "level": candles[i]["high"]})
        elif candles[i-2]["low"] > candles[i-1]["low"] > candles[i]["low"]:
            structure.append({"index": i, "type": "bearish_BOS", "level": candles[i]["low"]})
    return structure


def calculate_equilibrium(high, low):
    return (high + low) / 2


def is_in_session(timestamp, session="london"):
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    h = dt.hour
    if session == "london": return 7 <= h < 11
    if session == "new_york": return 12 <= h < 16
    if session == "asia": return 0 <= h < 5
    return False


def detect_turtle_soup(candles, lookback=5):
    signals = []
    for i in range(lookback, len(candles)):
        highs = [c["high"] for c in candles[i-lookback:i]]
        prev_high = max(highs)
        if candles[i]["high"] > prev_high and candles[i]["close"] < prev_high:
            signals.append({"index": i, "type": "bearish_turtle_soup", "level": prev_high})
        lows = [c["low"] for c in candles[i-lookback:i]]
        prev_low = min(lows)
        if candles[i]["low"] < prev_low and candles[i]["close"] > prev_low:
            signals.append({"index": i, "type": "bullish_turtle_soup", "level": prev_low})
    return signals


def detect_ote(candles, structure, fib_ratio=0.618):
    ote_zones = []
    for s in structure:
        i = s["index"]
        if s["type"] == "bullish_BOS" and i >= 2:
            swing_low = candles[i-2]["low"]
            high_lvl = candles[i]["high"]
            entry = high_lvl - (high_lvl - swing_low) * fib_ratio
            ote_zones.append({"index": i, "type": "bullish_ote", "entry": entry,
                              "swing_low": swing_low, "break_level": high_lvl})
        elif s["type"] == "bearish_BOS" and i >= 2:
            swing_high = candles[i-2]["high"]
            low_lvl = candles[i]["low"]
            entry = low_lvl + (swing_high - low_lvl) * fib_ratio
            ote_zones.append({"index": i, "type": "bearish_ote", "entry": entry,
                              "swing_high": swing_high, "break_level": low_lvl})
    return ote_zones


def main():
    import pprint

    coin = input("Enter coin name (e.g., bitcoin): ").strip()
    duration = int(input("Enter duration in seconds (e.g., 3600): ").strip())
    step = int(input("Enter step size in seconds (e.g., 300): ").strip())
    end_time = int(time.time())
    start_time = end_time - duration

    print("\nFetching historical data...")
    raw = get_historical_price_data(coin, start_time, end_time, step)
    if "error" in raw:
        print("Error fetching price data:", raw["error"])
        return

    candles = [
        {"timestamp": itm["start_time"], "open": itm["open"], "high": itm["max"],
         "low": itm["min"], "close": itm["close"]}
        for itm in raw if all(v is not None for v in [itm["open"], itm["close"], itm["min"], itm["max"]])
    ]
    if not candles:
        print("No valid candle data found.")
        return

    print(f"Processed {len(candles)} candles.")

    fvg = detect_fvg(candles)
    obs = detect_order_blocks(candles)
    sweeps = detect_liquidity_sweeps(candles)
    structure = detect_structure_breaks(candles)
    turtle = detect_turtle_soup(candles)
    ote = detect_ote(candles, structure)

    print("\nCurrent Price Info:")
    price_info = get_current_price_and_daily_change(coin)
    if "error" in price_info:
        print("Error:", price_info["error"])
    else:
        print(f"Current Price: {price_info['price']} {coin.upper()}")
        print(f"24h Change: {price_info['change_percentage']}%")

    print("\n--- Fair Value Gaps (FVG) ---")
    pprint.pprint(fvg[:5])
    print("\n--- Order Blocks ---")
    pprint.pprint(obs[:5])
    print("\n--- Liquidity Sweeps ---")
    pprint.pprint(sweeps[:5])
    print("\n--- Structure Breaks ---")
    pprint.pprint(structure[:5])
    print("\n--- Turtle Soup Signals ---")
    pprint.pprint(turtle[:5])
    print("\n--- OTE Zones ---")
    pprint.pprint(ote[:5])

    print("\n--- Session Info (Last 5 Candles) ---")
    for c in candles[-5:]:
        flags = {sess: is_in_session(c['timestamp'], sess) for sess in ['london', 'new_york', 'asia']}
        print(datetime.fromtimestamp(c['timestamp'], timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), flags)

    print("\nPlotting chart...")
    plot_ict_chart(candles, fvg, obs, sweeps, turtle, ote)


if __name__ == "__main__":
    main()
