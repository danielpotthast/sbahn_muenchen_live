#!/usr/bin/env python3
"""
Abfahrtstafel für eine spezifische Station
Verwendet direkt das timetable-Kommando
"""

import asyncio
import websockets
import json
import ssl
import certifi
from datetime import datetime


async def get_timetable(station_id, station_name="Station"):
    """
    Holt die Abfahrtstafel für eine Station

    Args:
        station_id: Station-ID (z.B. 8004167 für München Flughafen Besucherpark)
        station_name: Name der Station (für Anzeige)
    """
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
    uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    print(f"🚉 Abfahrtstafel für: {station_name} (ID: {station_id})")
    print("=" * 70)

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        # Fordere Abfahrtstafel an
        command = f"GET timetable_{station_id}"
        print(f"📤 Sende: {command}\n")
        await ws.send(command)

        departures = []

        try:
            # Empfange mehrere Nachrichten (jede ist eine Abfahrt)
            while True:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(response)

                # Prüfe ob es die timetable-Antwort ist
                if f"timetable_{station_id}" in data.get("source", ""):
                    content = data["content"]

                    # Jede Nachricht ist ein dict mit einer Abfahrt
                    if isinstance(content, dict):
                        line = content.get("line", {}).get("name", "?")

                        # Destination kann eine Liste sein
                        destination_raw = content.get("to", "?")
                        if isinstance(destination_raw, list):
                            destination = ", ".join(destination_raw) if destination_raw else "?"
                        else:
                            destination = destination_raw

                        # Zeitstempel konvertieren (departureTime)
                        dep_time_ms = content.get("departureTime") or content.get("time")
                        if dep_time_ms:
                            dep_time = datetime.fromtimestamp(dep_time_ms / 1000).strftime("%H:%M:%S")
                        else:
                            dep_time = "?"

                        # Verspätung
                        delay_ms = content.get("departureDelay", 0)
                        delay_min = round(delay_ms / 60000) if delay_ms else 0

                        # Gleis
                        platform = content.get("platform", "?")

                        # State (z.B. "SCHEDULED", "BOARDING")
                        state = content.get("state", "")

                        departures.append({
                            "time": dep_time,
                            "time_ms": dep_time_ms,
                            "line": line,
                            "destination": destination,
                            "delay": delay_min,
                            "platform": platform,
                            "state": state
                        })

        except asyncio.TimeoutError:
            # Timeout = keine weiteren Abfahrten
            pass

        # Sortiere nach Zeit
        departures.sort(key=lambda x: x.get("time_ms", 0))

        # Ausgabe
        if departures:
            print(f"✅ {len(departures)} Abfahrten gefunden:\n")
            print(f"{'Zeit':8s} | {'Linie':10s} | {'Ziel':40s} | {'Gleis':5s} | Verspätung")
            print("-" * 80)

            for dep in departures:
                delay_str = f"+{dep['delay']} min" if dep['delay'] > 0 else "pünktlich"
                delay_icon = "🔴" if dep['delay'] > 5 else "🟡" if dep['delay'] > 0 else "🟢"

                print(f"{dep['time']:8s} | {dep['line']:10s} | {dep['destination']:40s} | "
                      f"{str(dep['platform']):5s} | {delay_icon} {delay_str}")
        else:
            print("⚠️  Keine Abfahrten gefunden")

        return departures

    return []


async def main():
    """Hauptprogramm"""
    import sys

    # Stationen-IDs (kannst du erweitern)
    STATIONS = {
        "besucherpark": (8004167, "München Flughafen Besucherpark"),
        "flughafen": (8004168, "Flughafen/Airport ✈"),
        "neufahrn": (8004158, "Neufahrn(b München)"),
    }

    # Station aus Kommandozeile oder Default
    if len(sys.argv) > 1:
        station_key = sys.argv[1].lower()
        if station_key in STATIONS:
            station_id, station_name = STATIONS[station_key]
        elif sys.argv[1].isdigit():
            station_id = int(sys.argv[1])
            station_name = f"Station {station_id}"
        else:
            print("Verfügbare Stationen:")
            for key, (sid, name) in STATIONS.items():
                print(f"  {key:15s} -> {name} (ID: {sid})")
            print(f"\nOder direkte Station-ID: python3 timetable.py 8004167")
            return
    else:
        # Default: München Flughafen Besucherpark
        station_id, station_name = STATIONS["besucherpark"]

    await get_timetable(station_id, station_name)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Abgebrochen")
