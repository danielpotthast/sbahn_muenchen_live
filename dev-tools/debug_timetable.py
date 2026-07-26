#!/usr/bin/env python3
"""Debug timetable command"""

import asyncio
import websockets
import json
import ssl
import certifi

async def debug():
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
    uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    print("Testing timetable command...")

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        # Test verschiedene Kommandos
        commands = [
            "GET timetable_8004167",  # München Flughafen Besucherpark
            "GET station_8004167",
        ]

        for cmd in commands:
            print(f"\n{'='*70}")
            print(f"Testing: {cmd}")
            print('='*70)

            await ws.send(cmd)
            print(f"✅ Command sent: {cmd}")

            # Warte auf mehrere Antworten
            for i in range(5):
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=3.0)
                    data = json.loads(resp)

                    print(f"\n--- Response {i+1} ---")
                    print(f"Source: {data.get('source', 'N/A')}")
                    print(f"Keys: {list(data.keys())}")

                    # Zeige Content-Struktur
                    content = data.get('content')
                    if content:
                        print(f"Content type: {type(content)}")
                        if isinstance(content, list) and len(content) > 0:
                            print(f"Content length: {len(content)}")
                            print(f"First item keys: {list(content[0].keys())}")
                            print(f"First item sample:")
                            print(json.dumps(content[0], indent=2, ensure_ascii=False)[:500])
                        elif isinstance(content, dict):
                            print(f"Content keys: {list(content.keys())}")

                except asyncio.TimeoutError:
                    print(f"⏱️ Timeout after {i+1} responses")
                    break

if __name__ == "__main__":
    asyncio.run(debug())
