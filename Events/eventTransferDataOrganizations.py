import requests
import ssl
import json
import csv
from simple_salesforce import Salesforce
import os

ABS_PATH = os.path.join("/Users/juanestebanfloyd/Documents/FrontendDataLoader/App", "{}")

#parameters: 
#description: get data in sky api, 
#return: clean data with others personal information in csv files
class DataProcessor:
    #parameters: 
    #description: necessary keys for request to sky api
    #return: response to request
    def __init__(self):
        self.client_id = "14ff689a-1054-43ef-a3ec-e3137c3c4a3e"
        self.client_secret = "Y/YJK4+22KtLQt4CTkA3cwVtOXh7B+jpCUQolXYdLfo="
        self.token_url = "https://oauth2.sky.blackbaud.com/token"
        self.subscription_key = 'fa43a7b522a54b718178a4af6727392f'
        ssl._create_default_https_context = ssl._create_stdlib_context

    #parameters: 
    #description: generate and write refresh token in sky api when the old token isn't works
    #return: refresh token
    def refresh_token(self):
        #read refresh token
        with open(ABS_PATH.format("altru_refresh_token.txt"), 'r') as f:
            #obtain refrsh token
            refresh_token = f.read().strip()

        #necessary info to obtain refresh token
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        #request to obtain new token
        token_response = requests.post(self.token_url, data=token_data)

        #verify if the dtatus for obtain new token is succeed 
        if token_response.status_code == 200:
            #obtain new token
            new_access_token = token_response.json()["access_token"]
            print(f"Nuevo token de acceso: {new_access_token}")
            #write in file new token
            with open(ABS_PATH.format('altru_token.txt'), 'w') as f:
                f.write(new_access_token)
        else:
            #error to request new token
            print(f"Error al actualizar el token de acceso: {token_response.content}")

    #parameters: report name for request id
    #description: get id of the report in sky api
    #return: id of the report
    def get_id(self, report_name):
        #url for request
        url = f"https://api.sky.blackbaud.com/alt-anamg/adhocqueries/id/{report_name}"
        
        #access token for request
        with open(ABS_PATH.format('altru_token.txt'), 'r') as f:
            access_token = f.read().strip()
        
        #necessary headers to make a request 
        headers = {
            'Cache-Control': 'no-cache',
            'Authorization': f'Bearer {access_token}',
            'Bb-Api-Subscription-Key': self.subscription_key
        }

        try:
            #make a request
            response = requests.request("GET", url, headers=headers)
            
            #if the old token isn't work
            if response.status_code == 401:  # Unauthorized
                #obtain new token
                print("El token de acceso ha expirado. Actualizando el token...")
                self.refresh_token()

                #obtain id with new token
                return self.get_id(report_name)  
            
            #necessary info of the id report
            response_json = json.loads(response.text)
            id_value = response_json.get('id', None)

            #return id of the report 
            return id_value

        except requests.exceptions.RequestException as e:
            print(e)

    #parameters: report name for obtain info
    #description: get info of the report
    #return: write a info of the report in a json file
    def get_query(self, id, report_name):
        #url to make a request
        url = f"https://api.sky.blackbaud.com/alt-anamg/adhocqueries/{id}"

        #token for make a request
        with open(ABS_PATH.format('altru_token.txt'), 'r') as f:
            access_token = f.read().strip()

        #necessary info to make a request in sky api
        headers = {
            'Cache-Control': 'no-cache',
            'Authorization': f'Bearer {access_token}',
            'Bb-Api-Subscription-Key': self.subscription_key
        }

        try:
            #try, make a request
            response = requests.request("GET", url, headers=headers)

            #if old token isn't work
            if response.status_code == 401:  # Unauthorized
                print("El token de acceso ha expirado. Actualizando el token...")
                self.refresh_token()
                return self.get_query(id, report_name)  #obtain infor of the report by id

            #answer to info of the report in json file
            response_json = json.loads(response.text)

            #load info of the report in json file
            with open(ABS_PATH.format(f'Events/{report_name}_response.json'), 'w') as f:
                json.dump(response_json, f)

        except requests.exceptions.RequestException as e:
            print(e)

    #parameters: path of the json file and path of the csv file
    #description: convert json file in a csv file
    #return: csv file with info of the report
    def json_to_csv(self, json_file_path, csv_file_path):
        #open and load of the json file in read mode
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        #csv file in write mode
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)

            # write name of the fields in the firt row
            writer.writerow(data['field_names'])

            #write rows of with necessary data
            for row in data['rows']:
                writer.writerow(row)
                
    #parameters: csv file, header to want delete, csv without headers
    #description: delete header in a csv
    #return: csv without headers 
    def delete_columns(self, csv_input, headers_eliminar, csv_output):
        # Leer el archivo CSV
        with open(csv_input, 'r') as f:
            rows = list(csv.reader(f))
        
        headers = rows[0]
        
        #find index of the columns to delete
        indices_eliminar = [headers.index(header) for header in headers_eliminar if header in headers]
        
        #delete of the columns
        rows = [[value for i, value in enumerate(row) if i not in indices_eliminar] for row in rows]
        
        #load rows in the new csv file
        with open(csv_output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_names(self, input_csv, output_csv):
        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            #headers
            headers = next(reader)
            #data
            data = list(reader)
            #change email info
            email_index = headers.index('Email Addresses\\Email address')
            #change web address information
            web_address_index = headers.index('Web address')
            #change index information
            name_index = headers.index('Name')
            #change last_name information
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                # only store five characters in a name 
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                # only store firt word of the column last name and add "x" in the start and last position in the string
                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

                #only store the word "website.com"
                if row[web_address_index]:
                    protocol, rest = row[web_address_index].split('//')
                    domain, path = rest.split('.com', 1)
                    row[web_address_index] = protocol + '//website.com' + path

                #add "@tmail.comx" after of the @ in the email column
                if '@' in row[email_index]:
                    local, domain = row[email_index].split('@')
                    row[email_index] = local + '@tmail.comx'
            
            #apply changes in csv file
            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_address(self, input_csv, output_csv):
        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            #headers
            headers = next(reader)
            #data 
            data = list(reader)
            #index of name
            name_index = headers.index('Name')
            #index to last_name
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                #only store five characters of the name string
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                #only store first word of the column and add "x" in the start and the last position of the string
                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            #addres index
            address_index = headers.index('Addresses\\Address')
            #zip index
            zip_index = headers.index('Addresses\\ZIP')

            for row in data:
                #only store the first worh of the first space
                if row[address_index]:
                    row[address_index] = row[address_index].split()[0]

                #only store the 2 characters in the zip code column
                if row[zip_index]:
                    row[zip_index] = row[zip_index][:2]

            #store new information in csv           
            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_phone(self, input_csv, output_csv):
        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            #header
            headers = next(reader)
            #data
            data = list(reader)
            #index of name
            name_index = headers.index('Name')
            #index of last_name
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                #only store the 5 characters of the name
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                #only store the fist word of the name and add "x" in start position and last position
                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            #index of the phone 
            phone_index = headers.index('Phones\\Number')

            for row in data:
                #only add the 5 five characters in a phone string
                if row[phone_index]:
                    row[phone_index] = row[phone_index][:5]

            #store new infomration in csv file
            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)

    #parameters:
    #description: generate csv file of the reports in sky api with changed information
    #return: csv file with changed information of all reports
    def process_data(self):
        report_names = ["Veevart Organizations Report test", "Veevart Organization Addresses Report test", "Veevart Organization Phones Report test"] #name of the reports in sky api
        for report_name in report_names:
            id_value = self.get_id(report_name) #id of the report
            self.get_query(id_value, report_name) #info of the report by id
            self.json_to_csv(ABS_PATH.format(f'Events/{report_name}_response.json'), ABS_PATH.format(f'Events/{report_name}_output.csv')) #convert json files to csv files
            headers_eliminar = ["QUERYRECID"] #delete this header in all csv files
            self.delete_columns(ABS_PATH.format(f'Events/{report_name}_output.csv'), headers_eliminar, ABS_PATH.format(f'Events/{report_name}_output.csv')) #delete header of this csv file
            if report_name == "Veevart Organizations Report test":
                self.modify_csv_names(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv')) #changed information in this csv file
            elif report_name == "Veevart Organization Addresses Report test":
                self.modify_csv_address(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv')) #changed information in this csv file
            elif report_name == "Veevart Organization Phones Report test":
                self.modify_csv_phone(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv')) #changed information in this csv file

#parameters: 
#description: sent information of the csv file to salesforce 
#return: sent information in salesforce
class SalesforceProcessor:
    #parameters: 
    #description: info necessary to make a request in salesforce and data for sent to salesforce
    #return: sent information to salesforce
    def __init__(self, report_name):
        self.client_id = '3MVG9zeKbAVObYjPODek1PYnJW15VxHyhGPUOe1vzfHcg89tL_3Xyj_DCZQql_RL4Gjdnmk7EpfFk4DGDulnz'
        self.client_secret = '6003041383007768349'  
        self.redirect_uri = "http://localhost:8000"
        self.token_url = "https://test.salesforce.com/services/oauth2/token"
        self.report_name = report_name
        self.address_list = []
        self.account_list = []
        self.phone_list = []
        self.phone_act_list = []
        self.address_act_list = []
        
        #read token for make request in salesforce
        with open(ABS_PATH.format('salesforce_token.txt'), 'r') as f:
            self.access_token = f.read().strip()
        
        #read instance of the salesforce 
        with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
            instance = f.read().strip()

        #instance without "https://"
        instance = instance.split('https://')[1]


        #necessary to make request in salesforce
        self.sf = Salesforce(instance=instance, session_id=self.access_token)

    #parameters: 
    #description: generate and write refresh token in sky api when the old token isn't works
    #return: refresh token
    def refresh_token(self):
        #read refresh token
        with open(ABS_PATH.format("salesforce_refresh_token.txt"), 'r') as f:
            #obtain refrsh token
            refresh_token = f.read().strip()
            
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        #request to obtain new token
        token_response = requests.post(self.token_url, data=token_data)
        
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            refresh_token = token_response.json()["refresh_token"]
            instance = token_response.json()["instance_url"]
            #obtain new token
            try:
                with open(ABS_PATH.format('salesforce_token.txt')) as f:
                    f.write(access_token)
                with open(ABS_PATH.format('salesforce_refresh_token.txt'), 'w') as f:
                    f.write(refresh_token)
                with open(ABS_PATH.format('salesforce_instance.txt'), 'w') as f:
                    f.write(instance)
            except Exception as e:
                print(f"Error writing to file: {e}")


    #parameters: row with information of organizations
    #description: sent organizations info to salesforce
    #return: add information in a list for sent
    def handle_organizations_report(self, row):
        #info for sent 
        account_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'],
            'Name': row['Name'],
            'Website': row['Web address'],
            'vnfp__Do_not_Email__c' : row['Email Addresses\\Do not email'],
            'vnfp__Email__c': row['Email Addresses\\Email address']
        }
        #add info in a list for sent
        self.account_list.append(account_info)  

    #parameters: row with information of addresses
    #description: sent addresses info to salesforce
    #return: add information in a list for sent
    def handle_addresses_report(self, row):
        #implementation external ID
        lookup_id = row['Lookup ID']
        #information for sent
        addresses_info = {
            'npsp__MailingStreet__c': row['Addresses\\Address'],
            'npsp__MailingCity__c': row['Addresses\\City'],
            'npsp__MailingState__c': row['Addresses\\State'],
            'npsp__MailingPostalCode__c': row['Addresses\\ZIP'],
            'npsp__MailingCountry__c': row['Addresses\\Country'],
            'npsp__Default_Address__c' : row['Addresses\\Address'],
            'npsp__Household_Account__r': {'Auctifera__Implementation_External_ID__c': lookup_id} # upsert
        }
        #add information in list for sent
        self.address_list.append(addresses_info)

    #parameters: row with information of phone
    #description: sent phone info to salesforce
    #return: add information in a list for sent
    def handle_phone_report(self, row):
        #implementation external id
        lookup_id = row['Lookup ID']
        
        #info to sent
        phone_info = {
            'vnfp__number__c' : row['Phones\\Number'],
            'vnfp__Do_not_call__c' : row['Phones\\Do not call'],
            'vnfp__Account__r': {'Auctifera__Implementation_External_ID__c': lookup_id}
        }
        #add information in a list to sent
        self.phone_list.append(phone_info)

    #parameters: update organization with a primary phone
    #description: sent update info to phone  to salesforce
    #return: add information in a list for sent
    def handler_update_phone_organization(self, row):
        #primary phone
        valid = row['Phones\\Primary phone number']
        #info to update
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Phone' : row['Phones\\Number']
        }
        #if chaeckbox is True, add in a list to update phone info to list 
        if(valid):
            self.phone_act_list.append(new_info)            

    #parameters: update address information in organization
    #description: sent update information to addresses to salesforce
    #return: add update information in a list for sent
    def handler_update_address_organization(self, row):
        #implementation external id
        valid = row['Addresses\\Primary address']
        #info necessary to sent 
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            #'npsp__Default_Address__c' : row['Addresses\\Address']
            'BillingStreet' : row['Addresses\\Address'],
            'BillingCity' : row['Addresses\\City'],
            'BillingState' : row['Addresses\\State'],
            'BillingPostalCode' : row['Addresses\\ZIP'] ,
            'BillingCountry' : row['Addresses\\Country'],
        }
        #if the checkbox is True, add information to update in a organization 
        if(valid):
            self.address_act_list.append(new_info)            

    #parameters: 
    #description: proccess information to sent and store data in a list
    #return: add data in a list to sent
    def process_csv(self):
        with open(ABS_PATH.format(f'Events/{self.report_name}_output.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Veevart Organization Addresses Report' in self.report_name:
                    self.handle_addresses_report(row) #proccess info in a address for sent 
                    self.handler_update_address_organization(row) #proccess updated info to organization
                elif 'Veevart Organization Report' in self.report_name: 
                    self.handle_organizations_report(row) #process info to report of organization
                elif 'Veevart Organization Phones Report' in self.report_name: 
                    self.handle_phone_report(row) #process phone info to sent
                    self.handler_update_phone_organization(row) #proccess to updated info to organizations
        try:
            #if the list are not empty 
            if self.address_list:
                    self.sf.bulk.npsp__Address__c.insert(self.address_list, batch_size='auto',use_serial=True) #sent information in address object
            #if the list are not empty 
            if self.account_list:  
                self.sf.bulk.Account.upsert(self.account_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) # update info in account object
            #if the list are not empty 
            if self.phone_list:
                self.sf.bulk.vnfp__Phone__c.insert(self.phone_list, batch_size = 'auto', use_serial = True) #sent information in address object
            #if the list are not empty 
            if self.phone_act_list:
                self.sf.bulk.Account.upsert(self.phone_act_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update information in account object
            #if the list are not empty 
            if self.address_act_list:
                self.sf.bulk.Account.upsert(self.address_act_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update informacion in address object
        
        except requests.exceptions.RequestException as e:
            self.refresh_token()
            #read token for make request in salesforce
            with open(ABS_PATH.format('salesforce_token.txt'), 'r') as f:
                self.access_token = f.read().strip()
            
            #read instance of the salesforce 
            with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
                instance = f.read().strip()

            #instance without "https://"
            instance = instance.split('https://')[1]
            #necessary to make request in salesforce
            self.sf = Salesforce(instance=instance, session_id=self.access_token)
            self.process_csv

#parameters: adapter class between sky api(GET) and salesforce(POST) 
#description: sent info to salesforce
#return: sent information to salesforce
class Adapter:
    #parameters: name of report for sent info 
    #description: constructor for sent info to salesforce (GET and POST)
    #return: sent information of report 
    def __init__(self, report_names):
        self.data_processor = DataProcessor()
        self.salesforce_processors = [(report_name, SalesforceProcessor(report_name)) for report_name in report_names]

    #parameters: adapter class between sky api(GET) and salesforce(POST) 
    #description: sent info to salesforce after data was procceeed
    #return: sent information to salesforce
    def process_data(self):
        self.data_processor.process_data()
        for report_name, salesforce_processor in self.salesforce_processors:
            salesforce_processor.process_csv()

