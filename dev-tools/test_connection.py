#!/usr/bin/env python3
"""Test-Skript für geOps WebSocket API"""

import asyncio
import websockets
import ssl
import certifi

async def test_connection():
    """Teste verschiedene WebSocket-Endpunkte"""
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"

    # SSL-Kontext
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Verschiedene Endpunkt-Varianten
    endpoints = {
        "tracker-ws mit key": f"wss://api.geops.io/tracker-ws/v1/?key={api_key}",
        "realtime-ws mit key": f"wss://api.geops.io/realtime-ws/v1/?key={api_key}",
        "tracker-ws mit apiKey": f"wss://api.geops.io/tracker-ws/v1/?apiKey={api_key}",
    }

    print("🧪 Teste geOps WebSocket API-Endpunkte\n")
    print("=" * 70)

    for name, uri in endpoints.items():
        print(f"\n📍 {name}")
        print(f"   URL: {uri[:50]}...")

        try:
            # Kurzer Timeout für schnelles Testen
            async with websockets.connect(
                uri,
                ssl=ssl_context,
                open_timeout=5,
                close_timeout=2
            ) as ws:
                print(f"   ✅ Verbindung erfolgreich!")

                # Versuche eine Nachricht zu senden
                test_msg = "BBOX 3461470 2236822 4212388 3790024 7 tenant=sbm"
                await ws.send(test_msg)
                print(f"   ✅ Nachricht gesendet: {test_msg}")

                # Warte auf Antwort (max 5 Sekunden)
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    print(f"   ✅ Antwort empfangen: {len(response)} Zeichen")
                    print(f"   📄 Erste 200 Zeichen: {response[:200]}")
                    return True, name, uri
                except asyncio.TimeoutError:
                    print(f"   ⏱️ Timeout beim Warten auf Antwort")

        except websockets.exceptions.InvalidStatus as e:
            status_code = str(e).split()[-1] if 'HTTP' in str(e) else 'unbekannt'
            print(f"   ❌ HTTP Status: {status_code}")
        except Exception as e:
            print(f"   ❌ Fehler: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)
    print("\n⚠️  Keine erfolgreiche Verbindung möglich!")
    print("\n💡 Mögliche Lösungen:")
    print("   1. API-Key überprüfen (support@geops.io)")
    print("   2. Dokumentation checken: https://developer.geops.io/apis/realtime")
    print("   3. Alternative: REST API verwenden statt WebSocket")

    return False, None, None

if __name__ == "__main__":
    try:
        success, name, uri = asyncio.run(test_connection())
        if success:
            print(f"\n✅ Funktionierender Endpunkt gefunden: {name}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Abgebrochen durch Benutzer")
