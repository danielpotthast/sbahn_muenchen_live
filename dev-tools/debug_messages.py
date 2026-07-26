#!/usr/bin/env python3
"""
Debug-Skript: Zeigt alle empfangenen Nachrichtenstrukturen
"""

import asyncio
import websockets
import json
import ssl
import certifi

async def debug_messages():
    """Analysiere alle empfangenen Nachrichten"""
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
    uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    print("🔍 Analysiere empfangene Nachrichten...")
    print("=" * 70)

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        # BBOX senden
        bbox_cmd = "BBOX 2391006 2098479 5282852 3928367 5 tenant=sbm channel_prefix=schematic"
        await ws.send(bbox_cmd)
        print(f"📤 BBOX: {bbox_cmd}\n")

        message_count = 0

        try:
            while message_count < 10:  # Erste 10 Nachrichten analysieren
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                message_count += 1

                print(f"\n{'='*70}")
                print(f"📨 NACHRICHT #{message_count}")
                print(f"{'='*70}")

                try:
                    data = json.loads(response)

                    # Zeige Top-Level Keys
                    print(f"\n🔑 Top-Level Keys: {list(data.keys())}")

                    # Zeige komplette Struktur (max 2000 Zeichen)
                    formatted = json.dumps(data, indent=2, ensure_ascii=False)
                    if len(formatted) > 2000:
                        print(f"\n📄 Erste 2000 Zeichen:")
                        print(formatted[:2000] + "\n... (gekürzt)")
                    else:
                        print(f"\n📄 Komplette Nachricht:")
                        print(formatted)

                    # Spezielle Analysen
                    if "type" in data:
                        print(f"\n📌 Type: {data['type']}")

                    if "properties" in data:
                        props = data["properties"]
                        print(f"\n📌 Properties Keys: {list(props.keys())}")

                        # Zeige wichtige Properties
                        if "line" in props:
                            print(f"   - Line: {props.get('line')}")
                        if "destination" in props:
                            print(f"   - Destination: {props.get('destination')}")
                        if "state" in props:
                            print(f"   - State: {props.get('state')}")

                    if "calls" in data:
                        print(f"\n📌 CALLS gefunden! Anzahl: {len(data['calls'])}")
                        if data['calls']:
                            print(f"   Erste Call-Keys: {list(data['calls'][0].keys())}")

                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON-Fehler: {e}")
                    print(f"Raw: {response[:500]}")

        except asyncio.TimeoutError:
            print(f"\n⏱️ Timeout nach {message_count} Nachrichten")

    print(f"\n{'='*70}")
    print(f"✅ Analyse abgeschlossen - {message_count} Nachrichten")
    print(f"{'='*70}")

if __name__ == "__main__":
    try:
        asyncio.run(debug_messages())
    except KeyboardInterrupt:
        print("\n⚠️ Abgebrochen")
