import matplotlib.pyplot as plt
import os
import pandas as pd
import xml.etree.ElementTree as ET


previous_day_path = '../data/changed/rchg_2024-10-28'  # der Pfad zu dem Verzeichnis mit den Änderungen für den Vortag
target_day_path = '../data/changed/rchg_2024-10-29'  # der Pfad zu dem Verzeichnis mit den Änderungen für den Zieltag


def main() -> None:
    ids: set[str] = set()  # in dieser Menge werden IDs gespeichert, damit Änderungen nicht doppelt gezählt werden
    filenames = sorted(os.listdir(previous_day_path))  # die Dateinamen in dem Verzeichnis mit den Änderungen für den Vortag (sortiert)
    for fn in filenames:  # durch alle Dateinamen iterieren
        full_fn = os.path.join(previous_day_path, fn)  # der volle Dateiname
        tree = ET.parse(full_fn)  # den XML-Baum parsen
        root = tree.getroot()  # die Wurzel des XML-Baums
        for stop in root.findall('s'):  # alle Halte durchgehen
            ids.add(stop.attrib['id'])  # die ID des Halts der Menge hinzufügen
    filenames = sorted(os.listdir(target_day_path))  # die Dateinamen in dem Verzeichnis mit den Änderungen für den Zieltag (sortiert)
    timestrs: list[str] = []  # eine Liste für Zeitstempel
    ns_changes: list[int] = []  # eine Liste für die Anzahlen von Änderungen
    for fn in filenames:  # durch alle Dateinamen iterieren
        hour = fn[5:7]  # die Stunde aus dem Dateinamen ausschneiden
        minute = fn[8:10]  # die Minute aus dem Dateinamen ausschneiden
        second = fn[11:13]  # die Sekunde aus dem Dateinamen ausschneiden
        timestr = f'{hour}:{minute}:{second}'  # die Uhrzeit der Änderung als String
        full_fn = os.path.join(target_day_path, fn)  # der volle Dateiname
        tree = ET.parse(full_fn)  # den XML-Baum parsen
        root = tree.getroot()  # die Wurzel des XML-Baums
        n_changes = 0  # die Anzahl der Änderungen
        for stop in root.findall('s'):  # alle Halte durchgehen
            id = stop.attrib['id']  # die ID des Halts
            if id not in ids:
                n_changes += 1  # wenn die ID nicht in der ID-Menge ist, die Anzahl der Änderungen um 1 erhöhen
                ids.add(id)  # die ID der ID-Menge hinzufügen
        timestrs.append(timestr)  # den Zeitstring der Liste von Zeitstrings hinzufügen
        ns_changes.append(n_changes)  # die Anzahl der Änderungen der Liste von Anzahlen von Änderungen hinzufügen
    plot(timestrs, ns_changes)  # die kompilierten Daten plotten


# Diese Funktion nimmt eine Liste von Zeitstrings und eine Liste von Anzahlen von Änderungen entgegen und plottet diese Daten:
def plot(timestrs: list[str], ns_changes: list[int]) -> None:
    df = pd.DataFrame({'Uhrzeit': pd.to_datetime(timestrs, format='%H:%M:%S'), 'Änderungen': ns_changes})  # aus den Daten ein pandas.DataFrame-Objekt erzeugen
    plt.figure(figsize=(9, 6))  # 900 mal 600 Pixel groß
    plt.plot(df['Uhrzeit'], df['Änderungen'], color='r', linewidth=1, label='Änderungen')  # die Daten plotten
    plt.title('Anzahl der Fahrplanänderungen im Verlauf des Tages')  # dem Plot einen Titel geben
    plt.xlabel('Uhrzeit')  # das Label an der x-Achse
    plt.ylabel('Anzahl der Änderungen')  # das Label an der y-Achse
    plt.xticks(rotation=45)  # die x-Ticks drehen
    plt.yticks(range(10))  # die y-Ticks gehen von 0 bis 9 mit einem Intervall von 1
    plt.ylim(0, 10)  # eine Grenze für y-Werte setzen
    plt.grid(True)  # das Gitter aktivieren
    plt.legend()
    plt.tight_layout()
    plt.show()  # den Plot anzeigen


if __name__ == '__main__':
    main()