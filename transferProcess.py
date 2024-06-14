import os
from Events.eventTransferDataOrganizations import Adapter

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "App", "{}")

# Elimina el archivo 'finish.txt' si existe
if os.path.exists('finish.txt'):
    os.remove('finish.txt')

# Lista de nombres de informes con datos necesarios
report_names = [
    "Veevart Organizations Report test",
    "Veevart Organization Addresses Report test",
    "Veevart Organization Phones Report test",
    "Veevart HouseHolds Report test",
    "Veevart Contacts Report test",
    "Veevart Contacts Report Address test",
    "Veevart Contacts Report Email test",
    "Veevart Contacts Report Phones test"
]

# Crea una instancia de la clase Adapter
adapter = Adapter(report_names)

# Procesa los datos y obtiene los resultados
dic_accounts = adapter.process_data()

# Escribe 'finish' en el archivo 'finish.txt'
finish_path = os.path.join(ABS_PATH.format(''), 'finish.txt')
with open(finish_path, 'w') as f:
    f.write('finish')