"""Static reference data for S-Bahn München stations.

This table was generated once from the geOps realtime API by subscribing to the
`GET station_schematic` websocket command against
`wss://api.geops.io/realtime-ws/v1/` and collecting every station feature it
streams (uic, name, serving lines). The geOps API has no by-name station search
endpoint, so this snapshot is embedded here instead of being looked up live.
"""

from __future__ import annotations

from typing import Any

# uic (station id) -> name and serving S-Bahn lines
STATIONS: dict[int, dict[str, Any]] = {
    8000119: {"name": "Geltendorf", "lines": ["S4"]},
    8000261: {"name": "München Hbf (tief)", "lines": ["S1"]},
    8000262: {"name": "München Ost", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8000524: {"name": "Altenerding", "lines": ["S2"]},
    8000556: {"name": "Altomünster", "lines": ["S2"]},
    8000603: {"name": "Arnbach", "lines": ["S2"]},
    8000653: {"name": "Aufhausen(b Erding)", "lines": ["S2"]},
    8000675: {"name": "Aying", "lines": ["S5"]},
    8000685: {"name": "Bachern", "lines": ["S2"]},
    8000781: {"name": "Baierbrunn", "lines": ["S7"]},
    8000785: {"name": "Baldham", "lines": ["S4", "S6"]},
    8001229: {"name": "Buchenau(Oberbay)", "lines": ["S4"]},
    8001231: {"name": "Buchenhain", "lines": ["S7"]},
    8001354: {"name": "Dachau Bahnhof", "lines": ["S2"]},
    8001355: {"name": "Dachau Stadt", "lines": ["S2"]},
    8001404: {"name": "Deisenhofen", "lines": ["S3"]},
    8001578: {"name": "Dürrnhaar", "lines": ["S5"]},
    8001621: {"name": "Ebenhausen-Schäftlarn", "lines": ["S7"]},
    8001634: {"name": "Ebersberg(Oberbay)", "lines": ["S4", "S6"]},
    8001647: {"name": "Eching", "lines": ["S1"]},
    8001682: {"name": "Eglharting", "lines": ["S4", "S6"]},
    8001702: {"name": "Eichenau(Oberbay)", "lines": ["S4"]},
    8001825: {"name": "Erding", "lines": ["S2"]},
    8001829: {"name": "Erdweg", "lines": ["S2"]},
    8001922: {"name": "Vierkirchen-Esterhofen", "lines": ["S2"]},
    8001963: {"name": "Fasanenpark", "lines": ["S3"]},
    8001970: {"name": "Feldafing", "lines": ["S6"]},
    8001973: {"name": "Feldkirchen(b München)", "lines": ["S2"]},
    8001996: {"name": "Esting", "lines": ["S3"]},
    8002078: {"name": "Freising", "lines": ["S1"]},
    8002141: {"name": "Fürstenfeldbruck", "lines": ["S4"]},
    8002161: {"name": "Furth(b Deisenhofen)", "lines": ["S3"]},
    8002198: {"name": "Gauting", "lines": ["S6"]},
    8002210: {"name": "Geisenbrunn", "lines": ["S5", "S8"]},
    8002247: {"name": "Gernlinden", "lines": ["S3"]},
    8002275: {"name": "Gilching-Argelsried", "lines": ["S5", "S8"]},
    8002339: {"name": "Gräfelfing", "lines": ["S6"]},
    8002347: {"name": "Grafing Bahnhof", "lines": ["S4", "S6"]},
    8002348: {"name": "Grafing Stadt", "lines": ["S4", "S6"]},
    8002351: {"name": "Grafrath", "lines": ["S4"]},
    8002377: {"name": "Gröbenzell", "lines": ["S3"]},
    8002383: {"name": "Gronsdorf", "lines": ["S4", "S6"]},
    8002420: {"name": "Großhelfendorf", "lines": ["S5"]},
    8002422: {"name": "Großhesselohe Isartalbf", "lines": ["S20", "S7"]},
    8002435: {"name": "Grub(Oberbay)", "lines": ["S2"]},
    8002491: {"name": "Haar", "lines": ["S4", "S6"]},
    8002534: {"name": "Hallbergmoos", "lines": ["S8"]},
    8002610: {"name": "Harthaus", "lines": ["S5", "S8"]},
    8002715: {"name": "Heimstetten", "lines": ["S2"]},
    8002792: {"name": "Herrsching", "lines": ["S8"]},
    8002894: {"name": "Höhenkirchen-Siegertsbrunn", "lines": ["S5"]},
    8002899: {"name": "Höllriegelskreuth", "lines": ["S20", "S7"]},
    8002940: {"name": "Hohenbrunn", "lines": ["S5"]},
    8002955: {"name": "Hohenschäftlarn", "lines": ["S7"]},
    8002980: {"name": "Holzkirchen", "lines": ["S3"]},
    8003039: {"name": "Icking", "lines": ["S7"]},
    8003072: {"name": "Markt Indersdorf", "lines": ["S2"]},
    8003092: {"name": "Ismaning", "lines": ["S8"]},
    8003290: {"name": "Kirchseeon", "lines": ["S4", "S6"]},
    8003317: {"name": "Kleinberghofen", "lines": ["S2"]},
    8003438: {"name": "Kreuzstraße", "lines": ["S5"]},
    8003720: {"name": "Lochham", "lines": ["S6"]},
    8003735: {"name": "Lohhof", "lines": ["S1"]},
    8003824: {"name": "Maisach", "lines": ["S3"]},
    8003828: {"name": "Malching(Oberbay)", "lines": ["S3"]},
    8003879: {"name": "Markt Schwaben", "lines": ["S2"]},
    8004128: {"name": "München Donnersbergerbrücke", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]},
    8004129: {"name": "München Hackerbrücke", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]},
    8004130: {"name": "München Harras", "lines": ["S7"]},
    8004131: {"name": "München Isartor", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8004132: {"name": "München Karlsplatz", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8004133: {"name": "München Leienfelsstr.", "lines": ["S4"]},
    8004134: {"name": "München Leuchtenbergring", "lines": ["S1", "S2", "S4", "S5", "S6", "S8"]},
    8004135: {"name": "München Marienplatz", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8004136: {"name": "München Rosenheimer Platz", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8004137: {"name": "München Siemenswerke", "lines": ["S20", "S7"]},
    8004138: {"name": "München St.Martin-Str.", "lines": ["S3", "S5"]},
    8004139: {"name": "München-Untermenzing", "lines": ["S2"]},
    8004140: {"name": "München-Allach", "lines": ["S2"]},
    8004141: {"name": "München-Aubing", "lines": ["S4"]},
    8004142: {"name": "München-Berg am Laim", "lines": ["S2", "S4", "S6"]},
    8004143: {"name": "München-Daglfing", "lines": ["S8"]},
    8004144: {"name": "München-Englschalking", "lines": ["S8"]},
    8004145: {"name": "München-Fasanerie", "lines": ["S1"]},
    8004146: {"name": "München-Fasangarten", "lines": ["S3"]},
    8004147: {"name": "München-Feldmoching", "lines": ["S1"]},
    8004148: {"name": "München-Giesing", "lines": ["S3", "S5"]},
    8004149: {"name": "München-Johanneskirchen", "lines": ["S8"]},
    8004150: {"name": "München-Karlsfeld", "lines": ["S2"]},
    8004151: {"name": "München-Laim", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8004152: {"name": "München-Langwied", "lines": ["S3"]},
    8004153: {"name": "München-Lochhausen", "lines": ["S3"]},
    8004154: {"name": "München-Mittersendling", "lines": ["S20", "S7"]},
    8004155: {"name": "München-Moosach", "lines": ["S1", "S8"]},
    8004156: {"name": "München-Neuaubing", "lines": ["S5", "S8"]},
    8004157: {"name": "München-Obermenzing", "lines": ["S2"]},
    8004158: {"name": "München-Pasing", "lines": ["S20", "S3", "S4", "S5", "S6", "S8"]},
    8004159: {"name": "München-Perlach", "lines": ["S5"]},
    8004160: {"name": "München-Riem", "lines": ["S2"]},
    8004161: {"name": "München-Solln", "lines": ["S20", "S7"]},
    8004162: {"name": "München-Trudering", "lines": ["S4", "S6"]},
    8004163: {"name": "München-Westkreuz", "lines": ["S5", "S6", "S8"]},
    8004167: {"name": "München Flughafen Besucherpark", "lines": ["S1", "S8"]},
    8004168: {"name": "München Flughafen Terminal", "lines": ["S1", "S8"]},
    8004179: {"name": "München Hirschgarten", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]},
    8004181: {"name": "München-Freiham", "lines": ["S5", "S8"]},
    8004204: {"name": "Mammendorf", "lines": ["S3"]},
    8004249: {"name": "Neugilching", "lines": ["S5", "S8"]},
    8004252: {"name": "Neubiberg", "lines": ["S5"]},
    8004279: {"name": "Neufahrn(b Freising)", "lines": ["S1"]},
    8004404: {"name": "Niederroth", "lines": ["S2"]},
    8004580: {"name": "Oberschleißheim", "lines": ["S1"]},
    8004667: {"name": "Olching", "lines": ["S3"]},
    8004723: {"name": "Ottenhofen(Oberbay)", "lines": ["S2"]},
    8004726: {"name": "Otterfing", "lines": ["S3"]},
    8004733: {"name": "Ottobrunn", "lines": ["S5"]},
    8004761: {"name": "Peiß", "lines": ["S5"]},
    8004775: {"name": "Petershausen(Obb)", "lines": ["S2"]},
    8004827: {"name": "Planegg", "lines": ["S6"]},
    8004854: {"name": "Poing", "lines": ["S2"]},
    8004874: {"name": "Possenhofen", "lines": ["S6"]},
    8004893: {"name": "Puchheim", "lines": ["S4"]},
    8004899: {"name": "Pullach", "lines": ["S20", "S7"]},
    8004900: {"name": "Pulling(b Freising)", "lines": ["S1"]},
    8005127: {"name": "Röhrmoos", "lines": ["S2"]},
    8005299: {"name": "Sauerlach", "lines": ["S3"]},
    8005406: {"name": "Schöngeising", "lines": ["S4"]},
    8005419: {"name": "München Heimeranplatz", "lines": ["S2", "S20", "S7"]},
    8005442: {"name": "Schwabhausen(b Dachau)", "lines": ["S2"]},
    8005504: {"name": "Seefeld-Hechendorf", "lines": ["S8"]},
    8005652: {"name": "St Koloman", "lines": ["S2"]},
    8005675: {"name": "Starnberg Nord", "lines": ["S6"]},
    8005676: {"name": "Starnberg", "lines": ["S6"]},
    8005699: {"name": "Steinebach", "lines": ["S8"]},
    8005735: {"name": "Stockdorf", "lines": ["S6"]},
    8005831: {"name": "Taufkirchen", "lines": ["S3"]},
    8005920: {"name": "Türkenfeld", "lines": ["S4"]},
    8005927: {"name": "Tutzing", "lines": ["S6"]},
    8005986: {"name": "Unterföhring", "lines": ["S8"]},
    8005991: {"name": "Unterhaching", "lines": ["S3"]},
    8006006: {"name": "Germering-Unterpfaffenhofen", "lines": ["S5", "S8"]},
    8006059: {"name": "Vaterstetten", "lines": ["S4", "S6"]},
    8006131: {"name": "Wächterhof", "lines": ["S5"]},
    8006189: {"name": "Hebertshausen", "lines": ["S2"]},
    8006359: {"name": "Weßling(Oberbay)", "lines": ["S5", "S8"]},
    8006550: {"name": "Wolfratshausen", "lines": ["S7"]},
    8006671: {"name": "Zorneding", "lines": ["S4", "S6"]},
    8006688: {"name": "Unterschleißheim", "lines": ["S1"]},
    8006696: {"name": "München-Neuperlach Süd", "lines": ["S5"]},
    8098261: {"name": "München Hbf (tief)", "lines": ["S1", "S2", "S3", "S4", "S6", "S7"]},
    8098262: {"name": "München Hbf (tief)", "lines": ["S3", "S7"]},
    8098263: {"name": "München Hbf (tief)", "lines": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]},
}


def station_by_name(station_name: str) -> dict[str, Any] | None:
    """Find a station by exact or fuzzy (substring) name match."""
    for uic, station in STATIONS.items():
        if station["name"] == station_name:
            return {"id": uic, "name": station["name"]}

    lowered = station_name.lower()
    for uic, station in STATIONS.items():
        if lowered in station["name"].lower():
            return {"id": uic, "name": station["name"]}

    return None


def station_options() -> list[dict[str, str]]:
    """Build SelectSelector options for all known stations, sorted by name."""
    return [
        {
            "value": str(uic),
            "label": f"{station['name']} ({', '.join(station['lines'])})"
            if station["lines"]
            else station["name"],
        }
        for uic, station in sorted(STATIONS.items(), key=lambda item: item[1]["name"])
    ]
