import os

from binance.client import Client


def get_client():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret or api_key == "your_key" or api_secret == "your_secret":
        raise RuntimeError(
            "Missing/placeholder BINANCE_API_KEY or BINANCE_API_SECRET. "
            "Set real values in .env (see .env.example for the required keys)."
        )
    return Client(api_key, api_secret)


def get_total_wallet_balance_usdt(client):
    wallets = client.margin_v1_get_asset_wallet_balance()
    total_btc = sum(float(w["balance"]) for w in wallets)
    btc_price = float(client.get_symbol_ticker(symbol="BTCUSDT")["price"])
    return total_btc * btc_price
