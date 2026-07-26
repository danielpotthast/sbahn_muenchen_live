#!/usr/bin/env python3
"""
Stationsmonitor - Zeigt S-Bahn Abfahrten für eine spezifische Station
"""

import asyncio
import websockets
import json
import ssl
import certifi
from datetime import datetime
from collections import defaultdict


class StationMonitor:
    """Monitor für S-Bahn Abfahrten an einer Station"""

    def __init__(self, api_key, station_name):
        self.api_key = api_key
        self.station_name = station_name
        self.departures = defaultdict(list)
        self.uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def connect_and_monitor(self, duration=60):
        """Verbinde und sammle Abfahrten für gegebene Dauer (Sekunden)"""
        print(f"🚉 Stationsmonitor für: {self.station_name}")
        print(f"⏱️  Sammelzeit: {duration} Sekunden\n")
        print("=" * 70)

        async with websockets.connect(self.uri, ssl=self.ssl_context) as ws:
            # BBOX senden
            bbox_cmd = "BBOX 2391006 2098479 5282852 3928367 5 tenant=sbm channel_prefix=schematic"
            await ws.send(bbox_cmd)

            start_time = asyncio.get_event_loop().time()

            try:
                while (asyncio.get_event_loop().time() - start_time) < duration:
                    remaining = duration - (asyncio.get_event_loop().time() - start_time)
                    response = await asyncio.wait_for(ws.recv(), timeout=max(5, remaining))

                    data = json.loads(response)

                    # Verarbeite Haltestellensequenzen
                    if "calls" in data:
                        await self._process_calls(data)

            except asyncio.TimeoutError:
                pass

        self._print_summary()

    async def _process_calls(self, data):
        """Verarbeite Haltestellensequenz-Daten"""
        props = data.get("properties", {})
        line_name = props.get("line", {}).get("name", "?")
        destination = props.get("destination", "?")

        for call in data.get("calls", []):
            stop_name = call.get("stop", {}).get("name", "")

            # Nur relevante Station
            if self.station_name.lower() not in stop_name.lower():
                continue

            planned_dep = call.get("plannedDepartureTime")
            actual_dep = call.get("actualDepartureTime")
            delay = call.get("delay", 0)

            if not planned_dep:
                continue

            departure = {
                "line": line_name,
                "destination": destination,
                "planned": planned_dep,
                "actual": actual_dep or planned_dep,
                "delay": delay,
                "stop_name": stop_name
            }

            # Vermeide Duplikate
            key = f"{line_name}_{destination}_{planned_dep}"
            if key not in [f"{d['line']}_{d['destination']}_{d['planned']}"
                           for d in self.departures[stop_name]]:
                self.departures[stop_name].append(departure)
                print(f"✅ {line_name:10s} → {destination:30s} | {planned_dep} | +{delay} min")

    def _print_summary(self):
        """Drucke Zusammenfassung aller gefundenen Abfahrten"""
        print("\n" + "=" * 70)
        print(f"📊 ABFAHRTSTAFEL: {sum(len(d) for d in self.departures.values())} Abfahrten")
        print("=" * 70)

        if not self.departures:
            print("\n⚠️  Keine Abfahrten gefunden!")
            print(f"   Stationsname korrekt? '{self.station_name}'")
            return

        for stop_name, deps in sorted(self.departures.items()):
            print(f"\n🚉 {stop_name}")
            print("-" * 70)

            # Sortiere nach geplanter Abfahrtszeit
            sorted_deps = sorted(deps, key=lambda x: x['planned'])

            for dep in sorted_deps:
                delay_indicator = "🔴" if dep['delay'] > 5 else "🟡" if dep['delay'] > 0 else "🟢"
                delay_str = f"+{dep['delay']} min" if dep['delay'] > 0 else "pünktlich"

                print(f"{delay_indicator} {dep['actual']:8s} | "
                      f"{dep['line']:10s} → {dep['destination']:30s} | "
                      f"{delay_str}")


async def main():
    """Hauptprogramm"""
    import sys

    # API-Key
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"

    # Station aus Kommandozeile oder Default
    if len(sys.argv) > 1:
        station = sys.argv[1]
    else:
        print("Verwendung: python3 station_monitor.py 'Stationsname'")
        print("\nBeispiele:")
        print("  python3 station_monitor.py 'Besucherpark'")
        print("  python3 station_monitor.py 'Flughafen'")
        sys.exit(1)

    # Optional: Dauer in Sekunden (Standard: 60)
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    monitor = StationMonitor(api_key, station)
    await monitor.connect_and_monitor(duration)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Abgebrochen durch Benutzer")
