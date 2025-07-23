import time
import requests

def get_price(coin_name, currency="usd"):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_name.lower(), "vs_currencies": currency.lower()}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get(coin_name.lower(), {}).get(currency.lower())
    except requests.RequestException as e:
        return f"Error: {e}"

def sample_prices(coin_name, total_seconds):
    interval = total_seconds / 100  # 100 points
    prices = []

    print(f"Sampling 100 points over {total_seconds} seconds every {interval:.2f} seconds.")
    
    for i in range(100):
        price = get_price(coin_name)
        timestamp = time.time()
        prices.append({"time": timestamp, "price": price})
        print(f"{i+1}/100 - {coin_name} at {timestamp:.0f}: {price}")
        time.sleep(interval)

    return prices

if name == "main":
    coin = input("Enter coin name (e.g., bitcoin): ").strip()
    duration = int(input("Enter duration in seconds (e.g., 3600): ").strip())
    result = sample_prices(coin, duration)
    print("\nSampled Prices:")
    for point in result:
        print(point)
