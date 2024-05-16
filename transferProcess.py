import os
from Events.eventTransferDataOrganizations import Adapter

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
with open('finish.txt', 'w') as f:
    f.write('finish')
