import os
import requests
import schedule
import threading
import time

from datetime import datetime


path = '/path/to/your/folder'  # der Pfad, wo die Dateien abgelegt werden sollen
url = 'https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/8000105'  # die URL zum Abfragen geplanter Daten

headers = {  # die Header für die Abfrage (erforderlich, um Daten erhalten zu können)
    'DB-Client-Id': '<Your client ID>',  # die ID des Clients
    'DB-Api-Key': '<Your API key>'  # der API-Schlüssel
}


# Diese Funktion holt die geplanten Daten für einen Tag und speichert sie:
def fetch_plan() -> None:
    now = datetime.now()
    strfdate = now.strftime('%y%m%d')  # das aktuelle Datum im Format „JJMMTT“
    strfdate_hyphens = now.strftime('%Y-%m-%d')  # das aktuelle Datum im Format „JJJJ-MM-TT“
    os.makedirs(f'{path}/{strfdate_hyphens}', exist_ok=True)  # einen Ordner für den aktuellen Tag anlegen
    try:
        for i in range(24):  # von 0 bis 23 iterieren
            stri = str(i).rjust(2, '0')  # i als String mit zwei Zeichen, dem Nullen vorangestellt werden
            response = requests.get(f'{url}/{strfdate}/{stri}', headers=headers)  # eine Abfrage an die API schicken
            with open(f'{path}/{strfdate_hyphens}/{stri}.xml', 'w', encoding='UTF-8') as file:  # eine neue Datei in dem Verzeichnis für den aktuellen Tag anlegen und öffnen
                file.write(response.text)  # den Text der Antwort in die Datei schreiben
            time.sleep(15)  # 15 Sekunden warten, um die API nicht zu überlasten
    except Exception as e:  # wenn irgendetwas schiefläuft
        print('%s — %s' % (datetime.now().strftime('%Y-%m-%d, %H:%M:%S'), type(e)))  # die aktuelle Zeit und den Typ der Ausnahme ausgeben
        threading.Timer(3600, fetch_plan).start()  # die Funktion in einer Stunde nochmals aufrufen


schedule.every().day.at('12:00').do(fetch_plan)  # jeden Tag um 12 Uhr die Funktion `fetch_plan()` aufrufen

while True:  # Dauerschleife
    schedule.run_pending()  # der Scheduler führt alles aus, was ansteht
    time.sleep(60)  # das Programm für eine Minute schlafen legen, damit der Prozessor nicht überlastet wird