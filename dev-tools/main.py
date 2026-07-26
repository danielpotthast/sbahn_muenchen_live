import asyncio
import websockets
import json
import ssl
import certifi
from datetime import datetime

async def listen(station_filter=None):
    """Hauptfunktion zum Abhören der WebSocket-API

    Args:
        station_filter: Optional - Name der Station zum Filtern (z.B. "München Flughafen Besucherpark")
    """
    # API-Key
    api_key = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"

    # Korrekter Endpunkt (getestet und funktionierend)
    uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"

    # SSL-Kontext mit certifi-Zertifikaten (behebt macOS SSL-Problem)
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    print(f"🔄 Verbinde zu geOps Realtime API...")

    try:
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print(f"✅ Verbindung hergestellt!\n")
            await handle_connection(websocket, station_filter)
    except Exception as e:
        print(f"❌ Verbindungsfehler: {type(e).__name__}: {e}")
        print("\n💡 Kontakt: support@geops.io")

async def handle_connection(websocket, station_filter=None):
    """Verarbeitet die WebSocket-Verbindung und empfängt Nachrichten

    Args:
        websocket: WebSocket-Verbindung
        station_filter: Optional - Name der Station zum Filtern (z.B. "München Flughafen")
    """
    # Sende BBOX-Befehl (Web Mercator EPSG:3857 Koordinaten)
    bbox_message = "BBOX 3581557 2692590 4092769 3304087 8 tenant=sbm channel_prefix=schematic"
    print(f"📤 Sende BBOX: {bbox_message}")
    await websocket.send(bbox_message)

    if station_filter:
        print(f"🔍 Filtere nach Station: {station_filter}\n")

    print("⏳ Warte auf Fahrzeuge und Haltestellendaten...\n")

    message_count = 0
    departures_by_station = {}  # Sammle Abfahrten pro Station
    subscribed_trains = set()  # Bereits abonnierte Züge

    try:
        while True:
            # Warte auf Nachricht mit Timeout
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            message_count += 1

            try:
                data = json.loads(response)

                # Status-Nachricht
                if "content" in data and "status" in data.get("content", {}):
                    status = data["content"]["status"]
                    connection_id = data["content"].get("id", "unknown")
                    print(f"✅ Status: {status} (ID: {connection_id})")
                    continue

                # Trajectory-Nachricht mit Fahrzeugdaten
                if "content" in data and data.get("source") == "trajectory":
                    content = data["content"]
                    if content.get("type") == "Feature":
                        props = content.get("properties", {})
                        train_id = props.get("train_id")

                        # Abonniere Haltestellensequenz für diesen Zug
                        if train_id and train_id not in subscribed_trains:
                            subscribe_cmd = f"GET stopsequence_{train_id}"
                            await websocket.send(subscribe_cmd)
                            subscribed_trains.add(train_id)

                            line = props.get("line", {}).get("name", "?")
                            print(f"🚂 Neuer Zug gefunden: {line} (ID: {train_id[:20]}...)")
                            print(f"   📨 Haltestellendaten angefordert")

                # Stopsequence-Nachricht (enthält Haltestelleninformationen!)
                if "stopsequence" in data.get("source", ""):
                    content = data["content"]

                    # Content ist eine Liste mit einem Element
                    if isinstance(content, list) and len(content) > 0:
                        journey = content[0]

                        # Zuginfo
                        line_name = journey.get("line", {}).get("name", "?")
                        destination = journey.get("destination", "?")
                        train_id = journey.get("id", "?")

                        # Stationen
                        stations = journey.get("stations", [])

                    if stations:
                        print(f"\n🚉 Haltestellensequenz für {line_name} → {destination}")

                        for station in stations:
                            stop_name = station.get("stationName", "?")

                            # Zeitstempel in Millisekunden -> Sekunden -> lesbare Zeit
                            from datetime import datetime

                            departure_time_ms = station.get("departureTime")
                            arrival_time_ms = station.get("arrivalTime")
                            aimed_dep_ms = station.get("aimedDepartureTime")
                            aimed_arr_ms = station.get("aimedArrivalTime")

                            # Konvertiere zu lesbaren Zeiten
                            if departure_time_ms:
                                departure_time = datetime.fromtimestamp(departure_time_ms / 1000).strftime("%H:%M:%S")
                            else:
                                departure_time = None

                            if arrival_time_ms:
                                arrival_time = datetime.fromtimestamp(arrival_time_ms / 1000).strftime("%H:%M:%S")
                            else:
                                arrival_time = None

                            if aimed_dep_ms:
                                aimed_departure = datetime.fromtimestamp(aimed_dep_ms / 1000).strftime("%H:%M:%S")
                            else:
                                aimed_departure = None

                            if aimed_arr_ms:
                                aimed_arrival = datetime.fromtimestamp(aimed_arr_ms / 1000).strftime("%H:%M:%S")
                            else:
                                aimed_arrival = None

                            # Verspätungen in Millisekunden -> Minuten
                            departure_delay_ms = station.get("departureDelay", 0)
                            arrival_delay_ms = station.get("arrivalDelay", 0)

                            departure_delay = round(departure_delay_ms / 60000) if departure_delay_ms else 0
                            arrival_delay = round(arrival_delay_ms / 60000) if arrival_delay_ms else 0

                            platform = station.get("platform", "?")

                            # Wenn Station gefiltert werden soll
                            if station_filter and station_filter.lower() not in stop_name.lower():
                                continue

                            # Speichere Abfahrt
                            if stop_name not in departures_by_station:
                                departures_by_station[stop_name] = []

                            departure_info = {
                                "line": line_name,
                                "destination": destination,
                                "arrival_time": arrival_time,
                                "departure_time": departure_time,
                                "arrival_delay": arrival_delay,
                                "departure_delay": departure_delay,
                                "platform": platform,
                                "train_id": train_id
                            }
                            departures_by_station[stop_name].append(departure_info)

                            # Ausgabe
                            delay_str = f"+{departure_delay} min" if departure_delay > 0 else "pünktlich"
                            print(f"   {stop_name:40s} | Abf: {departure_time} (geplant: {aimed_departure}) | Gl. {platform} | {delay_str}")

                    continue

                # Alte Fahrzeugdaten-Verarbeitung (für Kompatibilität)
                if "type" in data and data["type"] == "Feature":
                    props = data.get("properties", {})
                    geometry = data.get("geometry", {})

                    # Fahrzeuginformationen
                    vehicle_id = props.get("id", "?")
                    line = props.get("line", {}).get("name", "?")
                    destination = props.get("destination", "?")
                    delay = props.get("delay", 0)

                    print(f"🚌 {line} → {destination}")
                    print(f"   ID: {vehicle_id}, Verspätung: {delay} min")

                    # Koordinaten
                    if geometry.get("type") == "Point":
                        coords = geometry.get("coordinates", [])
                        if coords:
                            print(f"   Position: {coords}")

                # Haltestellensequenz (enthält Abfahrtzeiten!)
                elif "calls" in data:
                    # Extrahiere Fahrzeug-/Linien-Info
                    vehicle_line = data.get("properties", {}).get("line", {}).get("name", "?")
                    vehicle_destination = data.get("properties", {}).get("destination", "?")

                    for call in data["calls"]:
                        stop_name = call.get("stop", {}).get("name", "?")
                        planned_dep = call.get("plannedDepartureTime")
                        actual_dep = call.get("actualDepartureTime")
                        planned_arr = call.get("plannedArrivalTime")
                        actual_arr = call.get("actualArrivalTime")
                        delay = call.get("delay", 0)

                        # Wenn Station gefiltert werden soll
                        if station_filter and station_filter.lower() not in stop_name.lower():
                            continue

                        # Speichere Abfahrt für diese Station
                        if stop_name not in departures_by_station:
                            departures_by_station[stop_name] = []

                        departure_info = {
                            "line": vehicle_line,
                            "destination": vehicle_destination,
                            "planned_departure": planned_dep,
                            "actual_departure": actual_dep,
                            "planned_arrival": planned_arr,
                            "actual_arrival": actual_arr,
                            "delay": delay
                        }
                        departures_by_station[stop_name].append(departure_info)

                        # Ausgabe
                        print(f"🚉 {stop_name}")
                        print(f"   Linie: {vehicle_line} → {vehicle_destination}")
                        print(f"   Ankunft:  geplant {planned_arr}, aktuell {actual_arr}")
                        print(f"   Abfahrt:  geplant {planned_dep}, aktuell {actual_dep}")
                        print(f"   Verspätung: {delay} min\n")

                # Andere Nachrichtentypen
                else:
                    print(f"📨 Nachricht #{message_count}: {list(data.keys())}")
                    print(f"   {response[:200]}...")

            except json.JSONDecodeError:
                print(f"⚠️  Keine JSON-Antwort: {response[:100]}")

    except asyncio.TimeoutError:
        print(f"\n⏱️  Keine weiteren Nachrichten nach 30s (Total: {message_count})")

        # Zusammenfassung der gesammelten Abfahrten
        if departures_by_station:
            print(f"\n{'='*70}")
            print(f"📊 ZUSAMMENFASSUNG: {len(departures_by_station)} Stationen, "
                  f"{sum(len(d) for d in departures_by_station.values())} Abfahrten")
            print(f"{'='*70}\n")

            for station, deps in sorted(departures_by_station.items()):
                print(f"🚉 {station} ({len(deps)} Abfahrten):")
                for dep in sorted(deps, key=lambda x: x.get('departure_time') or ''):
                    line = dep['line']
                    dest = dep['destination']
                    time = dep['departure_time']
                    platform = dep.get('platform', '?')
                    delay = dep.get('departure_delay', 0)
                    delay_str = f"+{delay} min" if delay > 0 else "pünktlich"
                    print(f"   {time} Gl.{platform:3s} | {line:10s} → {dest:30s} | {delay_str}")
                print()
        elif message_count == 1:
            print("\n💡 Tipps:")
            print("   - Eventuell sind keine Fahrzeuge im BBOX-Bereich")
            print("   - BBOX-Koordinaten überprüfen (Web Mercator EPSG:3857)")
            print("   - Tenant 'sbm' eventuell nicht korrekt")

    except websockets.exceptions.ConnectionClosed:
        print(f"\n🔌 Verbindung geschlossen nach {message_count} Nachrichten")

if __name__ == "__main__":
    import sys

    # Optional: Station als Kommandozeilenargument
    # Beispiel: python3 main.py "München Flughafen Besucherpark"
    station = sys.argv[1] if len(sys.argv) > 1 else None

    if station:
        print(f"🎯 Filter aktiviert für Station: {station}\n")

    asyncio.run(listen(station))
