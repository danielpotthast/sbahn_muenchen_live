#!/usr/bin/env python3
"""
Debug-Skript: Zeigt alle empfangenen Stationsnamen
"""

import asyncio
import websockets
import json
import ssl
import certifi

async def debug_stations():
    """Sammle alle Stationsnamen aus dem Stream"""
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
    uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    print("🔍 Sammle alle Stationsnamen aus dem Stream...")
    print("=" * 70)

    stations = set()
    message_count = 0

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        # BBOX senden
        bbox_cmd = "BBOX 2391006 2098479 5282852 3928367 5 tenant=sbm channel_prefix=schematic"
        await ws.send(bbox_cmd)
        print(f"📤 BBOX gesendet: {bbox_cmd}\n")

        try:
            while message_count < 50:  # Erste 50 Nachrichten
                response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                message_count += 1

                try:
                    data = json.loads(response)

                    # Status überspringen
                    if "content" in data and "status" in data.get("content", {}):
                        continue

                    # Haltestellensequenzen
                    if "calls" in data:
                        props = data.get("properties", {})
                        line = props.get("line", {}).get("name", "?")
                        destination = props.get("destination", "?")

                        for call in data["calls"]:
                            stop_name = call.get("stop", {}).get("name", "")
                            if stop_name:
                                stations.add(stop_name)
                                planned = call.get("plannedDepartureTime", "?")
                                print(f"📍 {stop_name:50s} | {line:10s} → {destination}")

                except json.JSONDecodeError:
                    pass

        except asyncio.TimeoutError:
            pass

    print("\n" + "=" * 70)
    print(f"📊 Insgesamt {len(stations)} verschiedene Stationen gefunden:")
    print("=" * 70)

    for station in sorted(stations):
        print(f"  • {station}")

    print("\n💡 Suche nach 'Flughafen' oder 'München':")
    print("-" * 70)
    for station in sorted(stations):
        if "flughafen" in station.lower() or "münchen" in station.lower():
            print(f"  ✅ {station}")

if __name__ == "__main__":
    try:
        asyncio.run(debug_stations())
    except KeyboardInterrupt:
        print("\n⚠️ Abgebrochen")
