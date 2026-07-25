import os
import time
import base64
from dotenv import load_dotenv
from urllib.parse import urlparse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import websockets
import asyncio
import json

load_dotenv()
KEY_ID = os.getenv("KALSHI_KEY_ID")
PRIVATE_KEY_PATH = os.getenv('KALSHI_PRIVATE_KEY_PATH')

WS_URL = "wss://external-api-ws.kalshi.com/trade-api/ws/v2"

private_key = serialization.load_pem_private_key(open(PRIVATE_KEY_PATH, 'rb').read(), password=None)

def auth_headers():
    ts = str(int(time.time() * 1000))
    path = "/trade-api/ws/v2"
    msg = (ts + "GET" + path).encode()
    sig = private_key.sign(
        msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256(),
    )

    return [
        ("KALSHI-ACCESS-KEY", KEY_ID),
        ("KALSHI-ACCESS-TIMESTAMP", ts),
        ("KALSHI-ACCESS-SIGNATURE", base64.b64encode(sig).decode())
    ]


async def main():
    async with websockets.connect(WS_URL, additional_headers=auth_headers()) as ws:
        await ws.send(json.dumps({
            "id": 1,
            "cmd": "subscribe",
            "params": {
                "channels": ["ticker", "trade"],
                "market_tickers": ["KXMLBGAME-26JUL25"]
            }
        }))

        async for raw_message in ws:
            msg = json.loads(raw_message)

            if msg.get("type") == "ticker":
                print("Ticker: ", msg["msg"])

            elif msg.get("type") == "trade":
                print("Trade: ", msg["msg"])

            elif msg.get("type") == "subscribed":
                print("subscription: ", msg["msg"])
            
            elif msg.get("type") == "error":
                print("error: ", msg["msg"])


asyncio.run(main())