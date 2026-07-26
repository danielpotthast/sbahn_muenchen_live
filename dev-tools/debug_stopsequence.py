#!/usr/bin/env python3
"""Debug stopsequence Struktur"""

import asyncio
import websockets
import json
import ssl
import certifi

async def debug():
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
    uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        await ws.send("BBOX 2391006 2098479 5282852 3928367 5 tenant=sbm channel_prefix=schematic")

        subscribed = False

        for i in range(30):
            resp = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(resp)

            # Ersten Zug abonnieren
            if not subscribed and data.get("source") == "trajectory":
                content = data.get("content", {})
                if content.get("type") == "Feature":
                    train_id = content.get("properties", {}).get("train_id")
                    if train_id:
                        await ws.send(f"GET stopsequence_{train_id}")
                        print(f"✅ Abonniert: {train_id}\n")
                        subscribed = True

            # Stopsequence analysieren
            if "stopsequence" in data.get("source", ""):
                print("="*70)
                print("STOPSEQUENCE GEFUNDEN!")
                print("="*70)
                print(f"Source: {data['source']}")
                print(f"\nContent Type: {type(data['content'])}")

                if isinstance(data['content'], list):
                    print(f"Content ist Liste mit {len(data['content'])} Elementen\n")

                    for idx, item in enumerate(data['content']):
                        print(f"\n--- Element {idx} ---")
                        print(f"Keys: {list(item.keys())}")

                        # Zeige wichtige Felder
                        if 'stations' in item:
                            stations = item['stations']
                            print(f"\n✅ STATIONS gefunden! Anzahl: {len(stations)}")

                            # Erste Station im Detail
                            if stations:
                                first_station = stations[0]
                                print(f"\nErste Station:")
                                print(json.dumps(first_station, indent=2, ensure_ascii=False))

                                # Nach München Flughafen suchen
                                for station in stations:
                                    if "flughafen" in station.get("name", "").lower():
                                        print(f"\n🎯 FLUGHAFEN GEFUNDEN!")
                                        print(json.dumps(station, indent=2, ensure_ascii=False))

                break

if __name__ == "__main__":
    asyncio.run(debug())
