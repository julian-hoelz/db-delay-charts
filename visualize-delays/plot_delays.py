import matplotlib.pyplot as plt
import os
import pandas as pd

from datetime import date, datetime, timedelta
from functools import total_ordering
from typing import Sequence
from xml.etree import ElementTree as ET


# Diese Klasse stellt eine Abfahrt mit der geplanten und der geänderten Zeit dar:
@total_ordering
class Departure:

    def __init__(self) -> None:
        self.planned: datetime | None = None
        self.changed: datetime | None = None


    # Diese Methode gibt die Verspätung (den Zeitunterschied zwischen der geplanten und der tatsächlichen Abfahrtszeit) zurück:
    def delay(self) -> int:
        if self.changed is None:
            return 0  # wenn keine Änderung vorhanden ist, 0 Minuten Verspätung
        return int((self.changed - self.planned).total_seconds()) // 60  # die Verspätung ist immer ein Vielfaches von 60 Sekunden


    def __str__(self) -> str:
        return f'planned: {self.planned}, changed: {self.changed}'
    
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Departure):
            return self.planned == value.planned  # Departure-Objekte werden mit der geplanten Abfahrtszeit verglichen
        raise TypeError
    
    
    def __lt__(self, value: object) -> bool:
        if isinstance(value, Departure):
            return self.planned < value.planned  # Departure-Objekte werden mit der geplanten Abfahrtszeit verglichen
        raise TypeError


PATH_PLANNED = '../data/planned'  # der Pfad zu dem Verzeichnis mit den geplanten Daten
PATH_CHANGED = '../data/changed'  # der Pfad zu dem Verzeichnis mit den geänderten Daten
TARGET_DAY = date(2024, 10, 31)  # vom 29.10. bis zum 04.11.2024 möglich


def main() -> None:
    departures_with_ids = load_planned_departures()  # die geplanten Abfahrtszeiten als Dictionary mit den zugehörigen Halt-IDs
    load_changed_departures(departures_with_ids)  # die geänderten Abfahrtszeiten den Abfahrten in dem Dictionary hinzufügen
    departures = sorted(departures_with_ids.values())  # die sortierten Abfahrten ohne die Halt-IDs
    to_plot = to_plottable_data(departures)  # die Abfahrten in plottbare Daten umwandeln
    plot(to_plot)  # die zu plottenden Daten plotten


# Diese Funktion lädt die geplanten Abfahrtszeiten als Dictionary mit den zugehörigen Halt-IDs:
def load_planned_departures() -> dict[str, Departure]:
    departures: dict[str, Departure] = {}
    path = os.path.join(PATH_PLANNED, f'plan_{TARGET_DAY.strftime('%Y-%m-%d')}')  # der Pfad zu dem Ordner mit den Daten des Zieltages
    filenames = sorted(os.listdir(path))  # die Dateinamen in diesem Ordner
    for fn in filenames:  # durch alle Dateinamen iterieren
        full_fn = os.path.join(path, fn)  # der volle Dateiname
        tree = ET.parse(full_fn)  # XML-Baum parsen
        root = tree.getroot()  # die Wurzel des XML-Baums
        for stopelem in root.findall('s'):  # durch alle Halt-Elemente in dem XML-Baum iterieren
            stop_id = stopelem.attrib['id']
            dp = stopelem.find('dp')  # das Abfahrt-Element in dem Halt-Element
            if dp is None:  # wenn keine Abfahrtszeit in dem Tag angegeben ist
                continue
            departure = departures.get(stop_id, None)  # die Abfahrt mit der ID aus dem Dictionary holen (None, wenn es keine gibt)
            if departure is None:  # wenn es keine Abfahrt mit der ID gibt
                departure = Departure()  # neue Abfahrt anlegen
                departures[stop_id] = departure  # die Abfahrt mit der ID im Dictionary anlegen
            pt = timestamp_to_datetime(dp.attrib['pt'])  # planned time
            departure.planned = pt  # die geplante Abfahrtszeit in dem Departure-Objekt speichern
    return departures  # das Dictionary zurückgeben


# Diese Funktion nimmt ein Dictionary mit Halt-IDs und geplanten Abfahrtszeiten entgegen und fügt die geänderten Abfahrtszeiten hinzu:
def load_changed_departures(departures: dict[str, Departure]) -> None:
    previous_day = TARGET_DAY - timedelta(days=1)  # der Tag vor dem Zieltag
    previous_day_path = os.path.join(PATH_CHANGED, f'rchg_{previous_day.strftime('%Y-%m-%d')}')  # der Pfad zu dem Verzeichnis mit den Daten des vorigen Tages
    target_day_path = os.path.join(PATH_CHANGED, f'rchg_{TARGET_DAY.strftime('%Y-%m-%d')}')  # der Pfad zu dem Verzeichnis mit den Daten des Zieltages
    previous_day_full_filenames = sorted(os.path.join(previous_day_path, fn) for fn in os.listdir(previous_day_path))  # alle vollen Dateinamen in dem Verzeichnis für den vorigen Tag (sortiert)
    target_day_full_filenames = sorted(os.path.join(target_day_path, fn) for fn in os.listdir(target_day_path))  # alle vollen Dateinamen in dem Verzeichnis für den Zieltag (sortiert)
    full_filenames = previous_day_full_filenames + target_day_full_filenames  # alle vollen Namen der Dateien mit zu berücksichtigenden Änderungen
    for ffn in full_filenames:
        tree = ET.parse(ffn)  # den XML-Baum parsen
        root = tree.getroot()  # die Wurzel des XML-Baums
        for stopelem in root.findall('s'):  # durch alle Halt-Elemente in dem XML-Baum iterieren
            stop_id = stopelem.attrib['id']  # die Halt-ID
            departure = departures.get(stop_id, None)  # das Departure-Objekt aus dem Dictionary bekommen
            if departure is None:
                continue  # wenn es kein Departure-Objekt mit der ID gibt, weiter
            dp = stopelem.find('dp')  # das Abfahrt-Element in dem Halt-Element
            if dp is None:
                continue  # wenn das Halt-Element kein Abfahrt-Element hat, weiter
            if 'ct' not in dp.attrib.keys():
                continue  # wenn das Abfahrt-Element kein `ct`-Attribut hat
            ct = timestamp_to_datetime(dp.attrib['ct'])  # die geänderte Abfahrtszeit
            if ct == departure.planned:
                continue  # wenn die geplante und die geänderte Abfahrtszeit gleich sind, weiter
            departure.changed = ct  # die geänderte Abfahrtszeit in dem Departure-Dictionary speichern


# Diese Funktion wandelt einen Zeitstempel im Format JJMMTThhmm“ in ein datetime-Objekt um:
def timestamp_to_datetime(timestamp: str) -> datetime:
    year = int('20' + timestamp[0:2])
    month = int(timestamp[2:4])
    day = int(timestamp[4:6])
    hour = int(timestamp[6:8])
    minute = int(timestamp[8:10])
    return datetime(year, month, day, hour, minute)


# Diese Funktion wandelt Departure-Objekte in ein plottbares Dictionary um: 
def to_plottable_data(departures: Sequence[Departure]) -> dict[str, list[int | datetime]]:
    xaxis = [d.planned for d in departures]  # die x-Achse: die geplanten Abfahrtszeiten
    yaxis = [d.delay() for d in departures]  # die y-Achse: die Verspätungen
    return {'time': xaxis, 'delay': yaxis}


# Diese Funktion plottet die Verspätungsdaten:
def plot(data: dict[str, list[int | datetime]]) -> None:
    df = pd.DataFrame(data)
    plt.figure(figsize=(9, 6))  # 900 mal 600 Pixel groß
    plt.plot(df['time'], df['delay'], color='r', linewidth=1, label='Verspätungen')
    plt.title(f'Alle Verspätungen am {TARGET_DAY.strftime('%d.%m.%Y')}')  # der Titel des Plots
    plt.xlabel('Uhrzeit')  # das Label an der x-Achse
    plt.ylabel('Verspätung in Minuten')  # das Label an der y-Achse
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()