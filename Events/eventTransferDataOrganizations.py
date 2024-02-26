import datetime
import requests
import ssl
import json
import csv
from simple_salesforce import Salesforce
import os

ABS_PATH = os.path.join("/Users/juanestebanfloyd/Documents/FrontendDataLoader/App", "{}")

class DataProcessor:
    def __init__(self):
        self.client_id = "14ff689a-1054-43ef-a3ec-e3137c3c4a3e"
        self.client_secret = "Y/YJK4+22KtLQt4CTkA3cwVtOXh7B+jpCUQolXYdLfo="
        self.token_url = "https://oauth2.sky.blackbaud.com/token"
        self.subscription_key = 'fa43a7b522a54b718178a4af6727392f'
        ssl._create_default_https_context = ssl._create_stdlib_context

    def refresh_token(self):
        with open(ABS_PATH.format("altru_refresh_token.txt"), 'r') as f:
            refresh_token = f.read().strip()

        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        token_response = requests.post(self.token_url, data=token_data)

        if token_response.status_code == 200:
            new_access_token = token_response.json()["access_token"]
            print(f"Nuevo token de acceso: {new_access_token}")

            with open(ABS_PATH.format('altru_token.txt'), 'w') as f:
                f.write(new_access_token)
        else:
            print(f"Error al actualizar el token de acceso: {token_response.content}")

    def get_id(self):
        report_name = 'testOrganization'
        url = f"https://api.sky.blackbaud.com/alt-anamg/adhocqueries/id/{report_name}"

        with open(ABS_PATH.format('altru_token.txt'), 'r') as f:
            access_token = f.read().strip()

        headers = {
            'Cache-Control': 'no-cache',
            'Authorization': f'Bearer {access_token}',
            'Bb-Api-Subscription-Key': self.subscription_key
        }

        try:
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 401:  # Unauthorized
                print("El token de acceso ha expirado. Actualizando el token...")
                self.refresh_token()
                return self.get_id()  # Llama a la función de nuevo después de actualizar el token

            response_json = json.loads(response.text)
            id_value = response_json.get('id', None)

            return id_value

        except requests.exceptions.RequestException as e:
            print(e)

    def get_query(self, id):
        url = f"https://api.sky.blackbaud.com/alt-anamg/adhocqueries/{id}"

        with open(ABS_PATH.format('altru_token.txt'), 'r') as f:
            access_token = f.read().strip()

        headers = {
            'Cache-Control': 'no-cache',
            'Authorization': f'Bearer {access_token}',
            'Bb-Api-Subscription-Key': self.subscription_key
        }

        try:
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 401:  # Unauthorized
                print("El token de acceso ha expirado. Actualizando el token...")
                self.refresh_token()
                return self.get_query(id)  # Llama a la función de nuevo después de actualizar el token

            response_json = json.loads(response.text)

            # Guardar la respuesta en un archivo JSON
            with open(ABS_PATH.format("Events/response.json"), 'w') as f:
                json.dump(response_json, f)

        except requests.exceptions.RequestException as e:
            print(e)

    def json_to_csv(self, json_file_path, csv_file_path):
        # Abre y carga el archivo JSON
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Abre el archivo CSV en modo escritura
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)

            # Escribe los nombres de los campos en la primera fila
            writer.writerow(data['field_names'])

            # Escribe las filas de datos
            for row in data['rows']:
                writer.writerow(row)

    def eliminar_columnas(self, csv_input, headers_eliminar, csv_output):
        # Leer el archivo CSV
        with open(csv_input, 'r') as f:
            rows = list(csv.reader(f))
        
        headers = rows[0]
        
        # Encontrar los índices de las columnas a eliminar
        indices_eliminar = [headers.index(header) for header in headers_eliminar if header in headers]
        
        # Eliminar las columnas
        rows = [[value for i, value in enumerate(row) if i not in indices_eliminar] for row in rows]
        
        # Guardar las filas en un nuevo archivo CSV
        with open(csv_output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def modificar_csv(self, input_csv, output_csv):
        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = list(reader)

        email_index = headers.index('Email Addresses\\Email address')
        name_index = headers.index('Name')
        last_name_index = headers.index('Last/Organization/Group/Household name')
        web_address_index = headers.index('Web address')
        phone_index = headers.index('Phones\\Number')
        address_index = headers.index('Addresses\\Address')
        zip_index = headers.index('Addresses\\ZIP')

        for row in data:
            # Agregar "@tmail.comx" después del @ en la columna de correo electrónico
            if '@' in row[email_index]:
                local, domain = row[email_index].split('@')
                row[email_index] = local + '@tmail.comx'

            # Dejar solo la primera letra en la columna de nombre
            if row[name_index]:
                row[name_index] = row[name_index][:5]

            # Dejar solo la primera palabra en la columna de apellido y agregar 'x' al principio y al final
            if row[last_name_index]:
                first_word = row[last_name_index].split()[0]
                row[last_name_index] = 'x' + first_word + 'x'

            # Cambiar lo que se encuentra después del // y antes del .com por "website" en la columna de dirección web
            if row[web_address_index]:
                protocol, rest = row[web_address_index].split('//')
                domain, path = rest.split('.com', 1)
                row[web_address_index] = protocol + '//website.com' + path

            # Dejar solo los 3 primeros números en la columna de teléfono
            if row[phone_index]:
                row[phone_index] = row[phone_index][:5]

            # Dejar solo lo primero antes del primer espacio en la columna de dirección
            if row[address_index]:
                row[address_index] = row[address_index].split()[0]

            # Dejar solo los dos primeros caracteres en la columna de código postal
            if row[zip_index]:
                row[zip_index] = row[zip_index][:2]

        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)

    def process_data(self):
        id_value = self.get_id()
        self.get_query(id_value)
        self.json_to_csv(ABS_PATH.format('Events/response.json'), ABS_PATH.format('Events/output.csv'))
        headers_eliminar = ["QUERYRECID"]
        self.eliminar_columnas(ABS_PATH.format('Events/output.csv'), headers_eliminar, ABS_PATH.format('Events/output.csv'))
        self.modificar_csv(ABS_PATH.format('Events/output.csv'), ABS_PATH.format('Events/output.csv'))

class SalesforceProcessor:
    def __init__(self, csv_file_path):
        self.client_id = '3MVG9zeKbAVObYjPODek1PYnJW15VxHyhGPUOe1vzfHcg89tL_3Xyj_DCZQql_RL4Gjdnmk7EpfFk4DGDulnz'
        self.client_secret = '6003041383007768349'  
        self.redirect_uri = "http://localhost:8000"
        self.token_url = "https://test.salesforce.com/services/oauth2/token"
        self.csv_file_path = csv_file_path
        with open(ABS_PATH.format('salesforce_token.txt'), 'r') as f:
            self.access_token = f.read().strip()
        with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
            instance = f.read().strip()
        # Divide la cadena en "https://" y toma la segunda parte
        instance = instance.split('https://')[1]
        self.sf = Salesforce(instance=instance, session_id=self.access_token)

    def contar_registros_grande(self, nombre_archivo):
        with open(nombre_archivo, 'r') as f:
            reader = csv.reader(f)
            num_registros = sum(1 for row in reader) - 1  # Restamos 1 para excluir el encabezado
        return num_registros

    def process_csv(self):
        num_registros = self.contar_registros_grande(self.csv_file_path)
        print(f'El archivo tiene {num_registros} registros.')

        with open(self.csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            account_info_list = []
            for row in reader:
                # Convertir la cadena de texto a un objeto de fecha si no está vacía
                membership_join_date = None
                if row['Contact (Primary)\\Member\\Membership\\Member since']:
                    membership_join_date = datetime.datetime.strptime(row['Contact (Primary)\\Member\\Membership\\Member since'], '%Y-%m-%dT%H:%M:%S')
                    # Convertir el objeto datetime a una cadena de texto en formato ISO 8601
                    membership_join_date = membership_join_date.isoformat()

                # Convertir la cadena de texto a un booleano
                do_not_email = None  # Valor por defecto si el campo está vacío
                if row['Email Addresses\\Do not email']:
                    do_not_email = row['Email Addresses\\Do not email'].lower() == 'true'

                # Obtener el ID del RecordType basado en el valor del campo 'Type'
                record_type = self.sf.query(f"SELECT Id FROM RecordType WHERE DeveloperName = '{row['Type']}' AND isActive = TRUE")
                record_type_id = record_type['records'][0]['Id'] if record_type['records'] else ''

                account_info = {
                    'Auctifera__Implementation_External_ID__c': row['Lookup ID'],
                    'Name': row['Name'],
                    #'Description': row['Type'],  
                    'Website': row['Web address'],
                    #'RecordTypeId': record_type_id,  # Usar el ID del RecordType obtenido
                    'vnfp__Email__c': row['Email Addresses\\Email address'],
                    #'vnfp__Do_not_Email__c': do_not_email,
                    #'BillingAddress' : row['Addresses\\City'],
                    'BillingCity' : row['Addresses\\City'], 
                    'BillingState' : row['Addresses\\State'],
                    'BillingPostalCode' : row['Addresses\\ZIP'],
                    'BillingCountry' : row['Addresses\\Country'],
                    #'LatestStart Date' : row['Addresses\\Start date '],
                    #'LatestEnd Date' : row['Addresses\\End date'],
                    #'AddressType' : row['Addresses\\Type'],
                    'Phone' : row['Phones\\Number'],
                    #'Do not call' : row['Phones\\Do not call']
                }
                account_info_list.append(account_info)
        try:
            results = self.sf.bulk.Account.upsert(account_info_list, 'Auctifera__Implementation_External_ID__c', batch_size=num_registros)
            for result in results:
                if result['success']:
                    print(f"Registro con ID {result['id']} actualizado o insertado exitosamente.")
                else:
                    print(f"Error al actualizar o insertar el registro: {result['errors']}")

        except Exception as e:
            if 'INVALID_SESSION_ID' in str(e):  # El token de acceso ha expirado
                print("El token de acceso ha expirado. Actualizando el token...")
                access_token = self.refresh_token()
                if access_token is None:
                    print("No se pudo actualizar el token de acceso. Por favor, verifica tus credenciales y vuelve a intentarlo.")
                else:
                    with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
                        instance = f.read().strip()
                    # Divide la cadena en "https://" y toma la segunda parte
                    instance = instance.split('https://')[1]
                    self.sf = Salesforce(instance=instance, session_id=access_token)
            else:
                print(e)

class Adapter:
     def __init__(self, csv_file_path):
         self.data_processor = DataProcessor()
         self.salesforce_processor = SalesforceProcessor(csv_file_path)

     def process_data(self):
         self.data_processor.process_data()
         self.salesforce_processor.process_csv()

# adapter = Adapter('/output.csv')
# adapter.process_data()