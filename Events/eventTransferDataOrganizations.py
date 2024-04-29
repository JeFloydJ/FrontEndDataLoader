import requests
import logging
import ssl
import json
import csv
import re
from simple_salesforce import Salesforce
import os
from dotenv import load_dotenv

# Set up logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
#                     force=True)

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                     force=True, 
                     filename='out.txt.log',
                     filemode='w')


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

#parameters: 
#description: get data in sky api, 
#return: clean data with others personal information in csv files
class DataProcessor:
    #parameters: 
    #description: necessary keys for request to sky api
    #return: response to request
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID_SKY_API")
        self.client_secret = os.getenv("CLIENT_SECRET_SKY_API")
        self.token_url = "https://oauth2.sky.blackbaud.com/token"
        self.subscription_key = os.getenv("SUBSCRIPTION_KEY_SKY_API")
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

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_households(self, input_csv, output_csv):
            with open(input_csv, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                data = list(reader)
                name_index = headers.index('Name')

                for row in data:
                    # Dejar solo la primera letra en la columna de nombre
                    if row[name_index]:
                        row[name_index] = row[name_index][:5]

                with open(output_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)

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
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

                if row[web_address_index]:
                    protocol, rest = row[web_address_index].split('//')
                    domain, path = rest.split('.com', 1)
                    row[web_address_index] = protocol + '//website.com' + path

                if '@' in row[email_index]:
                    local, domain = row[email_index].split('@')
                    row[email_index] = local + '@tmail.comx'
            
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
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            address_index = headers.index('Addresses\\Address')
            zip_index = headers.index('Addresses\\ZIP')

            for row in data:
                if row[address_index]:
                    row[address_index] = row[address_index].split()[0]

                if row[zip_index]:
                    row[zip_index] = row[zip_index][:2]

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
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            phone_index = headers.index('Phones\\Number')

            for row in data:
                if row[phone_index]:
                    row[phone_index] = row[phone_index][:5]

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_contacs_address(self, input_csv, output_csv):
            with open(input_csv, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                data = list(reader)
                name_index = headers.index('Name')
                last_name_index = headers.index('Last/Organization/Group/Household name')
                
                address_index = headers.index('Addresses\\Address')
                zip_index = headers.index('Addresses\\ZIP')

                for row in data:
       
                    if row[address_index]:
                        row[address_index] = row[address_index].split()[0]

                    if row[zip_index]:
                        row[zip_index] = row[zip_index][:2]

                    if row[name_index]:
                        row[name_index] = row[name_index][:5]

                    if row[last_name_index]:
                        first_word = row[last_name_index].split()[0]
                        row[last_name_index] = 'x' + first_word + 'x'

                with open(output_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_contacs_email(self, input_csv, output_csv):
            with open(input_csv, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                data = list(reader)
                name_index = headers.index('Name')
                last_name_index = headers.index('Last/Organization/Group/Household name')                
                email_index = headers.index('Email Addresses\\Email address')

                for row in data:
                    if row[name_index]:
                        row[name_index] = row[name_index][:5]

                    if row[last_name_index]:
                        first_word = row[last_name_index].split()[0]
                        row[last_name_index] = 'x' + first_word + 'x'

                    if '@' in row[email_index]:
                        local, domain = row[email_index].split('@')
                        row[email_index] = local + '@tmail.comx'

                with open(output_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_contacs(self, input_csv, output_csv):
            with open(input_csv, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                data = list(reader)
                name_index = headers.index('Name')
                last_name_index = headers.index('Last/Organization/Group/Household name') 

                for row in data:
                    if row[name_index]:
                        row[name_index] = row[name_index][:5]

                    if row[last_name_index]:
                        first_word = row[last_name_index].split()[0]
                        row[last_name_index] = 'x' + first_word + 'x'


                with open(output_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_phones(self, input_csv, output_csv):
        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')
            phone_index = headers.index('Phones\\Number')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

                if row[phone_index]:
                    row[phone_index] = row[phone_index][:5]

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)

    #parameters:
    #description: generate csv file of the reports in sky api with changed information
    #return: csv file with changed information of all reports
    def process_data(self):
        report_names = ["Veevart Organizations Report test", "Veevart Organization Addresses Report test", "Veevart Organization Phones Report test", "Veevart HouseHolds Report test", "Veevart Contacts Report test", "Veevart Contacts Report Address test", "Veevart Contacts Report Email test", "Veevart Contacts Report Email test", "Veevart Contacts Report Phones test"]
        for report_name in report_names:
            id_value = self.get_id(report_name)
            self.get_query(id_value, report_name)
            self.json_to_csv(ABS_PATH.format(f'Events/{report_name}_response.json'), ABS_PATH.format(f'Events/{report_name}_output.csv'))            
            if report_name == "Veevart Organizations Report test":
                self.modify_csv_names(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart Organization Addresses Report test":
                self.modify_csv_address(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart Organization Phones Report test":
                self.modify_csv_phone(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart HouseHolds Report test":
                self.modify_csv_households(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart Contacts Report Address test":
                self.modify_csv_contacs_address(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart Contacts Report Email test":
                self.modify_csv_contacs_email(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart Contacts Report test":
                self.modify_csv_contacs(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))
            elif report_name == "Veevart Contacts Report Phones test":
                self.modify_csv_phones(ABS_PATH.format(f'Events/{report_name}_output.csv'), ABS_PATH.format(f'Events/{report_name}_output.csv'))

#parameters: 
#description: sent information of the csv file to salesforce 
#return: sent information in salesforce
class SalesforceProcessor:
    #parameters: 
    #description: info necessary to make a request in salesforce and data for sent to salesforce
    #return: sent information to salesforce
    def __init__(self, report_name):
        self.client_id = os.getenv("CLIENT_ID_SALESFORCE")
        self.client_secret = os.getenv("CLIENT_SECRET_SALESFORCE")
        self.redirect_uri = os.getenv("REDIRECT_URI_SALESFORCE")
        self.token_url = "https://test.salesforce.com/services/oauth2/token"
        self.report_name = report_name
        self.address_list = []
        self.account_list = []
        self.phone_list = []
        self.phone_act_list = []
        self.address_act_list = []
        self.houseHolds_list = []
        self.contacts_list = []
        self.contacts_phones_list = []
        self.contacts_emails_list = []
        self.contacts_address_list = []
        self.contacts_id_list = []
        self.contacts_accounts_id = {}
        self.contacts_act_phone = []
        self.contacts_act_email = []
        self.houseHolds_external_ids_list = []
        self.households_ids = {}
        self.valid_check = {}


        
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

        self.organizations_id = self.get_organizations_id() #id of organizations
        self.households_id = self.get_households_id() #id of households

    #parameters: 
    #description: get recordTypeId for households in org
    #return: return Id of households
    def get_households_id(self):
        query = self.sf.query("SELECT Id FROM RecordType WHERE DeveloperName = 'HH_Account' AND IsActive = true")
        Id = query['records'][0]['Id']
        return Id

    #parameters: 
    #description: get recordTypeId for organizations in org
    #return: return Id of organizations
    def get_organizations_id(self):
        query = self.sf.query("SELECT Id FROM RecordType WHERE DeveloperName = 'organization' AND IsActive = true")
        Id = query['records'][0]['Id']
        return Id

    #parameters: 
    #description: get AccountId for contacts in org
    #return: return hash table like: {'Auctifera__Implementation_External_ID__c': 'AccountId'}
    def get_account_id(self):
        query = {}
        ans = self.sf.query_all("SELECT Id, AccountId, Auctifera__Implementation_External_ID__c FROM Contact WHERE Auctifera__Implementation_External_ID__c != null")
        print('query:', ans)
        for record in ans['records']:
            query[record['Auctifera__Implementation_External_ID__c']] = record['AccountId']
        return query

    #Parameters:
    #description: get househoulds id modify for avoid duplicates error
    #return: return hashtable like {'1-households-code' : 'code'}
    def find_households_id(self, lst):
        dic = {}
        for element in lst:
            match = re.search(r'(\d+)-households-(.*)', element)
            if match:
                id = match.group(2)
                dic[id] = element
        return dic
    

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
        account_info = {
            'RecordTypeId': self.organizations_id,
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'],
            'Name': row['Name'],
            'Website': row['Web address'],
            'vnfp__Do_not_Email__c' : False if row['Email Addresses\\Do not email'] == '' or row['Email Addresses\\Do not email'] == False else True,
        }
        self.account_list.append(account_info)  

    #parameters: row with information of addresses
    #description: sent addresses info to salesforce
    #return: add information in a list for sent
    def handle_addresses_report(self, row, counter):
        lookup_id = row['Lookup ID']
        addresses_info = {
            'npsp__MailingStreet__c': row['Addresses\\Address'],
            'npsp__MailingCity__c': row['Addresses\\City'],
            'npsp__MailingState__c': row['Addresses\\State'],
            'npsp__MailingPostalCode__c': row['Addresses\\ZIP'],
            'npsp__MailingCountry__c': row['Addresses\\Country'],
            'npsp__Default_Address__c' : False if row['Addresses\\Primary address'] == '' or row['Addresses\\Primary address'] == False else True,
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'address'+ '-organization' + '-' + row['QUERYRECID']),
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'address'+ '-organization' + '-' + row['QUERYRECID']),
            'npsp__Household_Account__r': {'Auctifera__Implementation_External_ID__c': lookup_id} # upsert
        }
        self.address_list.append(addresses_info)

    #parameters: row with information of phone
    #description: sent phone info to salesforce
    #return: add information in a list for sent
    def handle_phone_report(self, row):
        lookup_id = row['Lookup ID']
        phone_info = {
            'vnfp__Type__c' : 'Phone',
            'vnfp__value__c' : row['Phones\\Number'],
            'vnfp__Account__r': {'Auctifera__Implementation_External_ID__c': lookup_id}
        }
        self.phone_list.append(phone_info)

    #parameters: update organization with a primary phone
    #description: sent update info to phone  to salesforce
    #return: add information in a list for sent
    def handler_update_phone_organization(self, row):
        valid = row['Phones\\Primary phone number']
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Phone' : row['Phones\\Number']
        }
        if(valid):
            self.phone_act_list.append(new_info)            

    #parameters: update address information in organization
    #description: sent update information to addresses to salesforce
    #return: add update information in a list for sent
    def handler_update_address_organization(self, row):
        valid = row['Addresses\\Primary address']
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'BillingStreet' : row['Addresses\\Address'],
            'BillingCity' : row['Addresses\\City'],
            'BillingState' : row['Addresses\\State'],
            'BillingPostalCode' : row['Addresses\\ZIP'] ,
            'BillingCountry' : row['Addresses\\Country'],
        }
        if(valid):
            self.address_act_list.append(new_info)            

    #parameters: row with information of households
    #description: sent households info to salesforce
    #return: add information in a list for sent
    def handler_households(self, row, counter):
        #object with info to sent
        self.houseHolds_external_ids_list.append(str( str(counter) + '-' + 'households' +'-'+row['QUERYRECID'])) 
        households_info = {
            'RecordTypeId': self.households_id,
            'Auctifera__Implementation_External_ID__c': str( str(counter) + '-' + 'households' +'-'+row['QUERYRECID']),
            'Name': row['Name']
        }
        #add info to list
        self.houseHolds_list.append(households_info)

    #parameters: row with information of contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    #parameters: row with information of contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    def handler_contacts(self, row, dic):
        #object with info to sent
        account = row['Households Belonging To\\Household Record ID'] 
        contacts_info = {
            'Salutation' : row['Title'],
            'FirstName' : row['First name'],
            'LastName' : row['Last/Organization/Group/Household name'],
            'Auctifera__Implementation_External_ID__c' : row['Lookup ID'],
            'Description' : row['Notes\\Notes'],
            'GenderIdentity' : row['Gender'],
        }
        if account != '':
            contacts_info['Account'] = {'Auctifera__Implementation_External_ID__c': dic[account]}

        self.contacts_list.append(contacts_info)

    #parameters: row with phones information of the contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    def handle_contacts_phone_report(self, row, counter):
        lookup_id = row['Lookup ID']
        phone_info = {
            'vnfp__Type__c' : 'Phone',
            'vnfp__value__c' : row['Phones\\Number'],
            #'vnfp__Do_not_call__c' : row['Phones\\Do not call'],
            'vnfp__Contact__r': {'Auctifera__Implementation_External_ID__c': lookup_id},
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'phone' + '-' + row['QUERYRECID']),
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'phone' + '-' + row['QUERYRECID'])
        }
        self.contacts_phones_list.append(phone_info)

    #parameters: row with emails information of contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    def handle_contacts_emails_report(self, row, counter):
        lookup_id = row['Lookup ID']
        email_info = {
            'vnfp__Type__c' : 'Email',
            'vnfp__value__c' : row['Email Addresses\\Email address'],
            #'vnfp__Do_not_call__c' : row['Phones\\Do not call'],
            'vnfp__Contact__r': {'Auctifera__Implementation_External_ID__c': lookup_id},
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'contacts-email' + '-' + row['QUERYRECID'])
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'contacts-email' + '-' + row['QUERYRECID'])

        }
        self.contacts_emails_list.append(email_info)

    #parameters: row with address information of contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    def handle_contacts_addresses_report(self, row, dic, counter):
        lookup_id = row['Lookup ID']
        # print('dic en address', dic)
        addresses_info = {
            'npsp__MailingStreet__c': row['Addresses\\Address'],
            'npsp__MailingCity__c': row['Addresses\\City'],
            'npsp__MailingState__c': row['Addresses\\State'],
            'npsp__MailingPostalCode__c': row['Addresses\\ZIP'],
            'npsp__MailingCountry__c': row['Addresses\\Country'],
            'npsp__Household_Account__c': dic[lookup_id],
            'npsp__Default_Address__c' : False if row['Addresses\\Primary address'] == '' or row['Addresses\\Primary address'] == False else True,
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'contacts-address' + '-' + 'contacts' +row['QUERYRECID'])
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'contacts-address' + '-' + 'contacts' +row['QUERYRECID'])
        }

        self.contacts_address_list.append(addresses_info)

    #parameters: row with phone information of contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    def handle_contacts_update_phone(self, row):
        valid = False if row['Phones\\Primary phone number'] == '' or row['Phones\\Primary phone number'] == False else True
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Phone' : row['Phones\\Number']
        }
        if(valid):
            self.contacts_act_phone.append(new_info)

    #parameters: row with email information of contacts
    #description: sent contacts info to salesforce
    #return: add information in a list for sent
    def handle_contacts_update_email(self, row):
        valid = False if row['Email Addresses\\Primary email address'] == '' or row['Email Addresses\\Primary email address'] == False else True
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Email' : row['Email Addresses\\Email address']
        }
        if valid and self.valid_check.get(row['Lookup ID'], None) == None:
            self.contacts_act_email.append(new_info)       
            self.valid_check[row['Lookup ID']] = True
      
   
    #parameters: 
    #description: sent organizations information to salesforce
    #return: sent data
    def process_organizations(self):
        counter = 0
        with open(ABS_PATH.format(f'Events/{self.report_name}_output.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Veevart Organizations Report test' == self.report_name: 
                    self.handle_organizations_report(row)
                elif 'Veevart Organization Phones Report test' == self.report_name: 
                    self.handle_phone_report(row)
                    self.handler_update_phone_organization(row)
                elif 'Veevart Organization Addresses Report test' == self.report_name:
                    self.handle_addresses_report(row,counter)
                    self.handler_update_address_organization(row)

            if self.account_list:
                self.sf.bulk.Account.upsert(self.account_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)  # update info in account object
            
            if self.phone_list:
                self.sf.bulk.vnfp__Legacy_Data__c.upsert(self.phone_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True)            
            
            if self.address_list:
                self.sf.bulk.npsp__Address__c.upsert(self.address_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True)

            if self.phone_act_list:
                self.sf.bulk.Account.upsert(self.phone_act_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update information in account object
            
            if self.address_act_list:
                self.sf.bulk.Account.upsert(self.address_act_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update informacion in address object

    #parameters: 
    #description: sent households information to salesforce
    #return: sent data
    def process_households(self):
        counter = 0
        with open(ABS_PATH.format(f'Events/{self.report_name}_output.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                counter += 1
                if 'Veevart HouseHolds Report test' == self.report_name:
                    self.handler_households(row, counter)
                
            if self.houseHolds_list:
 #               self.sf.bulk.account.insert(self.houseHolds_list, batch_size='auto',use_serial=True) #sent information in account(household) object            
                  self.sf.bulk.Account.upsert(self.houseHolds_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update informacion in address object
        
        return self.houseHolds_external_ids_list   
    
    #parameters: 
    #description: sent households information to salesforce
    #return: sent data
    def process_households_ids(self):
        self.households_ids = self.find_households_id(self.houseHolds_external_ids_list)
        return self.households_ids
    
    #parameters: 
    #description: sent contacts information to salesforce
    #return: sent data
    def process_contacts(self):
        counter = 0
        with open(ABS_PATH.format(f'Events/{self.report_name}_output.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                counter += 1
                if 'Veevart Contacts Report test' == self.report_name:
                    self.handler_contacts(row, self.households_ids)
                elif 'Veevart Contacts Report Phones test' == self.report_name:
                    self.handle_contacts_phone_report(row, counter)
                    self.handle_contacts_update_phone(row)
                elif 'Veevart Contacts Report Email test' == self.report_name:
                    self.handle_contacts_emails_report(row, counter)
                    self.handle_contacts_update_email(row)
                   
             
            if self.contacts_list:
                results = self.sf.bulk.Contact.upsert(self.contacts_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update information in contact object
                for result in results:
                    if result['success']:
                        self.contacts_id_list.append(result['id'])
                
                self.contacts_accounts_id = self.get_account_id()

            if self.contacts_phones_list:
                self.sf.bulk.vnfp__Legacy_Data__c.upsert(self.contacts_phones_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True) 
            
            if self.contacts_emails_list:
                self.sf.bulk.vnfp__Legacy_Data__c.upsert(self.contacts_emails_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True) 
            
            if self.contacts_act_phone:
                self.sf.bulk.Contact.upsert(self.contacts_act_phone, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update information in account object
            
            #print('update emails contacts', self.contacts_act_email)
            if self.contacts_act_email:
                self.sf.bulk.Contact.upsert(self.contacts_act_email, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) #update information in account object

        return self.contacts_accounts_id

    #parameters: 
    #description: sent address of contacts information to salesforce
    #return: sent data
    def process_contact_address(self):
        with open(ABS_PATH.format(f'Events/{self.report_name}_output.csv'), 'r') as f:
            counter = 0
            reader = csv.DictReader(f)
            for row in reader:
                counter += 1
                if 'Veevart Contacts Report Address test' == self.report_name:
                    self.handle_contacts_addresses_report(row, self.contacts_accounts_id, counter)

            # print('update address contacts', self.contacts_address_list)
            if self.contacts_address_list:
                self.sf.bulk.npsp__Address__c.upsert(self.contacts_address_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True)  #sent information in address object


# hash table like: {'Auctifera__Implementation_External_ID__c': 'AccountId'} for sent address information
dic_accounts = {}
#hashtable like {'1-households-code' : 'code'}
dic_households_ids = {}

#parameters: 
#description: adapter between sky an salesforce for sent data
#return: get data and sent data
class Adapter:
    #parameters: report_names
    #description: Initializes the DataProcessor and report names
    #return: 
    def __init__(self, report_names):
        self.data_processor = DataProcessor()
        self.report_names = report_names
        self.dic_households_ids = {}

    #parameters: 
    #description: Processes data using the DataProcessor and sends address of contacts information to Salesforce
    #return: sent data
    def process_data(self):
        self.data_processor.process_data()
        dic_accounts = {}
        for report_name in self.report_names:
            processor = SalesforceProcessor(report_name)
            processor.process_organizations()
            processor.process_households()
            logger.info(dic_households_ids)
            self.dic_households_ids = {**self.dic_households_ids, **processor.process_households_ids()}
            processor.households_ids = self.dic_households_ids
            dic = processor.process_contacts()
            dic_accounts = {**dic_accounts, **dic}
            processor.process_contact_address()



