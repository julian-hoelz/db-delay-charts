import os
import requests
import time

from datetime import datetime


path = '/path/to/your/folder'  # der Pfad, wo die Dateien abgelegt werden sollen
url_fchg = 'https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/fchg/8000105'  # die URL zum Abfragen voller Änderungen
url_rchg = 'https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/rchg/8000105'  # die URL zum Abfragen kürzlicher Änderungen

headers = {  # die Header für die Abfrage (erforderlich, um Daten erhalten zu können)
    'DB-Client-Id': '<Your client ID>',  # die ID des Clients
    'DB-Api-Key': '<Your API key>'  # der API-Schlüssel
}


# Diese Funktion holt volle Änderungen und speichert sie:
def fetch_fchg() -> None:
    try:
        response = requests.get(url_fchg, headers=headers)  # eine Abfrage an die API schicken
        strftime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # die aktuelle Zeit als String mit Datum und Uhrzeit
        with open(f'{path}/fchg_{strftime}.xml', 'w', encoding='UTF-8') as file:   # eine neue Datei anlegen und öffnen
                file.write(response.text)  # den Text der Antwort in die Datei schreiben
    except Exception as e:  # wenn irgendetwas schiefläuft
        print('%s — %s' % (datetime.now().strftime('%Y-%m-%d, %H:%M:%S'), type(e)))  # die aktuelle Zeit und den Typ der Ausnahme ausgeben


# Diese Funktion holt kürzliche Änderungen und speichert sie:
def fetch_rchg() -> None:
    try:
        response = requests.get(url_rchg, headers=headers)  # eine Abfrage an die API schicken
        now = datetime.now()  # die aktuelle Zeit
        strfdate = now.strftime('%Y-%m-%d')  # das aktuelle Datum
        strftime = now.strftime('%H-%M-%S')  # die aktuelle Uhrzeit
        os.makedirs(f'{path}/rchg_{strfdate}', exist_ok=True)  # ein Verzeichnis für den aktuellen Tag anlegen; wenn es schon existiert, keine Fehlermeldung
        with open(f'{path}/rchg_{strfdate}/rchg_{strftime}.xml', 'w', encoding='UTF-8') as file:  # eine neue Datei in dem Verzeichnis für den aktuellen Tag anlegen und öffnen
            file.write(response.text)  # den Text der Antwort in die Datei schreiben
    except Exception as e:  # wenn irgendetwas schiefläuft
        print('%s — %s' % (datetime.now().strftime('%Y-%m-%d, %H:%M:%S'), type(e)))  # die aktuelle Zeit und den Typ der Ausnahme ausgeben
        

fetch_fchg()  # zu Beginn der Ausführung `fetch_fchg()` aufrufen
next_run = time.time()  # die aktuelle Zeit
while True:  # Dauerschleife
    fetch_rchg()  # solange das Skript läuft, `fetch_rchg()` aufrufen
    next_run += 30
    sleep_time = max(0, next_run - time.time())
    time.sleep(sleep_time)  # das Skript so lange schlafen legen, bis 30 Sekunden vergangen sind