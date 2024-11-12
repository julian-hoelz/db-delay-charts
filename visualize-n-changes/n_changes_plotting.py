import matplotlib.pyplot as plt
import os
import pandas as pd
import xml.etree.ElementTree as ET


path = '../data/changed/rchg_2024-10-29'  # der Pfad zu dem Verzeichnis mit den kürzlichen Änderungen


def main() -> None:
    filenames = sorted(os.listdir(path))  # die Dateinamen in dem Verzeichnis mit den Änderungen für den Vortag (sortiert)
    timestrs: list[str] = []  # eine Liste für Zeitstempel
    ns_changes: list[int] = []  # eine Liste für die Anzahlen von Änderungen
    for fn in filenames:  # durch alle Dateinamen iterieren
        hour = fn[5:7]  # die Stunde aus dem Dateinamen ausschneiden
        minute = fn[8:10]  # die Minute aus dem Dateinamen ausschneiden
        second = fn[11:13]  # die Sekunde aus dem Dateinamen ausschneiden
        timestr = f'{hour}:{minute}:{second}'  # die Uhrzeit der Änderung als String
        full_fn = os.path.join(path, fn)  # der volle Dateiname
        tree = ET.parse(full_fn)  # den XML-Baum parsen
        root = tree.getroot()  # die Wurzel des XML-Baums
        n_changes = len(root.findall('s'))  # die Anzahl der Halte ist die Anzahl der Änderungen
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
    plt.grid(True)  # das Gitter aktivieren
    plt.legend()
    plt.tight_layout()
    plt.show()  # den Plot anzeigen


if __name__ == '__main__':
    main()