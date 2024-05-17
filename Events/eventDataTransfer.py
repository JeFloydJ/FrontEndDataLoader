import requests
import ssl
import json
import re
from simple_salesforce import Salesforce
import boto3
import csv
import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

class SalesforceProcessor:
    def __init__(self, report_name, bucket_name):
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
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.bucket_name = bucket_name

        with open(ABS_PATH.format('salesforce_token.txt')) as f:
            self.access_token = f.read().strip()

        with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
            instance = f.read().strip()

        #instance without "https://"
        if 'https://' in instance:
            instance = instance.split('https://')[1]
        else:
            instance = instance

        self.sf = Salesforce(instance=instance, session_id=self.access_token)
        
        self.organizations_id = self.get_organizations_id() 
        self.households_id = self.get_households_id()
    
    def get_households_id(self):
        query = self.sf.query("SELECT Id FROM RecordType WHERE DeveloperName = 'HH_Account' AND IsActive = true")
        Id = query['records'][0]['Id']
        return Id
    
    def get_organizations_id(self):
        query = self.sf.query("SELECT Id FROM RecordType WHERE DeveloperName = 'organization' AND IsActive = true")
        Id = query['records'][0]['Id']
        return Id
    
    def get_account_id(self):
        query = {}
        ans = self.sf.query_all("SELECT Id, AccountId, Auctifera__Implementation_External_ID__c FROM Contact WHERE Auctifera__Implementation_External_ID__c != null")

        for record in ans['records']:
            query[record['Auctifera__Implementation_External_ID__c']] = record['AccountId']
        return query

    def find_households_id(self, HouseHoldslist):
        dic = {}
        for element in HouseHoldslist:
            match = re.search(r'(\d+)-households-(.*)', element)
            if match:
                id = match.group(2)
                dic[id] = element
        return dic
    
    def handle_organizations_report(self, row):
        account_info = {
            'RecordTypeId': self.organizations_id,
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'],
            'Name': row['"Name"'],
            'Website': row['Web address'],
            #'vnfp__Do_not_Email__c' : False if row['Email Addresses\\Do not email'] != 'Yes' else True,
        }
        if row['Email Addresses\\Email address'] != '':
            account_info['Auctifera__Email__c'] = row['Email Addresses\\Email address']

        self.account_list.append(account_info)  

    def handle_organization_addresses_report(self, row, counter):
        lookup_id = row['Lookup ID']
        addresses_info = {
            'npsp__MailingStreet__c': row['Addresses\\Address'],
            'npsp__MailingCity__c': row['Addresses\\City'],
            'npsp__MailingState__c': row['Addresses\\State'],
            'npsp__MailingPostalCode__c': row['Addresses\\ZIP'],
            'npsp__MailingCountry__c': row['Addresses\\Country'],
            'npsp__Default_Address__c' : False if row['Addresses\\Primary address'] != 'Yes' else True,
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'address'+ '-organization' + '-' + row['QUERYRECID']),
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'address'+ '-organization' + '-' + row['QUERYRECID']),
            'npsp__Household_Account__r': {'Auctifera__Implementation_External_ID__c': lookup_id} # upsert
        }
        self.address_list.append(addresses_info)

    def handle_organization_phone_report(self, row, counter):
        lookup_id = row['Lookup ID']
        phone_info = {
            'vnfp__Type__c' : 'Phone',
            'vnfp__value__c' : row['Phones\\Number'],
            #'vnfp__Do_not_call__c' : row['Phones\\Do not call'],
            'vnfp__Account__r': {'Auctifera__Implementation_External_ID__c': lookup_id},
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'phone' + '-' + row['QUERYRECID'])
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'phone' + '-' + row['QUERYRECID'])
        }
        self.phone_list.append(phone_info)

    def handler_update_phone_organization(self, row):
        valid = row['Phones\\Primary phone number']
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Phone' : row['Phones\\Number']
        }
        if(valid):
            self.phone_act_list.append(new_info)            

    def handler_update_address_organization(self, row):
        valid = row['Addresses\\Primary address']
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            #'npsp__Default_Address__c' : row['Addresses\\Address']
            'BillingStreet' : row['Addresses\\Address'],
            'BillingCity' : row['Addresses\\City'],
            'BillingState' : row['Addresses\\State'],
            'BillingPostalCode' : row['Addresses\\ZIP'] ,
            'BillingCountry' : row['Addresses\\Country'],
        }
        if(valid):
            self.address_act_list.append(new_info)            

    def handler_households(self, row, counter):
        self.houseHolds_external_ids_list.append(str( str(counter) + '-' + 'households' +'-'+row['QUERYRECID'])) 
        households_info = {
            'RecordTypeId': self.households_id,
            'Auctifera__Implementation_External_ID__c': str( str(counter) + '-' + 'households' +'-'+row['QUERYRECID']),
            'Name': row['"Name"']
        }
        self.houseHolds_list.append(households_info)

    def handler_contacts_report(self, row, dic):
        #object with info to sent
        account = row['Households Belonging To\\Household Record ID'] 
        contacts_info = {
            'Salutation' : row['Title'],
            'FirstName' : row['First name'],
            'LastName' : row['Last/Organization/Group/Household name'],
            'Auctifera__Implementation_External_ID__c' : row['Lookup ID'],
            #'Description' : row['Notes\\Notes'],
            #'GenderIdentity' : row['Gender'],
        }
        if account != '':
            contacts_info['Account'] = {'Auctifera__Implementation_External_ID__c': dic[account]}

        self.contacts_list.append(contacts_info)

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

    def handle_contacts_addresses_report(self, row, dic, counter):
        lookup_id = row['Lookup ID']
        # print('dic en address', dic)
        addresses_info = {
            'npsp__MailingStreet__c': row['Addresses\\Address'],
            'npsp__MailingCity__c': row['Addresses\\City'],
            'npsp__MailingState__c': row['Addresses\\State'],
            'npsp__MailingPostalCode__c': row['Addresses\\ZIP'],
            'npsp__MailingCountry__c': row['Addresses\\Country'],
            #'npsp__Household_Account__c': dic[lookup_id],
            'npsp__Default_Address__c' : False if row['Addresses\\Primary address'] != 'Yes' else True,
            'vnfp__Implementation_External_ID__c' : str(str(counter)+ '-' + 'contacts-address' + '-' + 'contacts' +row['QUERYRECID'])
            #'Implementation_External_ID__c' : str(str(counter)+ '-' + 'contacts-address' + '-' + 'contacts' +row['QUERYRECID'])
        }
        if lookup_id in dic:
            addresses_info['npsp__Household_Account__c'] = [row['Lookup ID']]

        self.contacts_address_list.append(addresses_info)

    def handle_contacts_update_phone(self, row):
        valid = False if row['Phones\\Primary phone number'] != 'Yes' else True
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Phone' : row['Phones\\Number']
        }
        if(valid):
            self.contacts_act_phone.append(new_info)       

    def handle_contacts_update_email(self, row):
        valid = False if row['Email Addresses\\Primary email address'] != 'Yes' else True
        new_info = {
            'Auctifera__Implementation_External_ID__c': row['Lookup ID'], 
            'Email' : row['Email Addresses\\Email address']
        }
        if valid and self.valid_check.get(row['Lookup ID'], None) == None:
            self.contacts_act_email.append(new_info)       
            self.valid_check[row['Lookup ID']] = True

    def process_organizations(self):
        counter = 0
        object_key = f'{self.report_name}.csv'
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.DictReader(f, delimiter=';')
        data = list(reader)
        for row in data:
            counter += 1
            if 'Veevart Organizations Report test' == self.report_name: 
                self.handle_organizations_report(row)
            elif 'Veevart Organization Phones Report test' == self.report_name: 
                self.handle_organization_phone_report(row, counter)
                self.handler_update_phone_organization(row)
            elif 'Veevart Organization Addresses Report test' == self.report_name:
                self.handle_organization_addresses_report(row, counter)
                self.handler_update_address_organization(row)

        if self.account_list:
            self.sf.bulk.Account.upsert(self.account_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)  
            
        if self.phone_list:
            self.sf.bulk.vnfp__Legacy_Data__c.upsert(self.phone_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True)
            
        if self.address_list:
            self.sf.bulk.npsp__Address__c.upsert(self.address_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True)

        if self.phone_act_list:
            self.sf.bulk.Account.upsert(self.phone_act_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)
            
        if self.address_act_list:
            self.sf.bulk.Account.upsert(self.address_act_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) 

    def process_households(self):
        counter = 0
        object_key = f'{self.report_name}.csv'
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.DictReader(f, delimiter=';')
        data = list(reader)
        for row in data:
            counter += 1
            if 'Veevart HouseHolds Report test' == self.report_name:
                self.handler_households(row, counter)
                
        if self.houseHolds_list:
            self.sf.bulk.Account.upsert(self.houseHolds_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)
        
        return self.houseHolds_external_ids_list
    
    def process_households_ids(self):
        self.households_ids = self.find_households_id(self.houseHolds_external_ids_list)
        return self.households_ids

    def process_contacts(self):
        counter = 0
        object_key = f'{self.report_name}.csv'
        print(object_key)
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.DictReader(f, delimiter=';')
        data = list(reader)
        for row in data:
            counter += 1
            if 'Veevart Contacts Report test' == self.report_name:
                self.handler_contacts_report(row, self.households_ids)
            elif 'Veevart Contacts Report Phones test' == self.report_name:
                self.handle_contacts_phone_report(row, counter)
                self.handle_contacts_update_phone(row)
            elif 'Veevart Contacts Report Email test' == self.report_name:
                self.handle_contacts_emails_report(row, counter)
                self.handle_contacts_update_email(row)

        if self.contacts_list:
            results = self.sf.bulk.Contact.upsert(self.contacts_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True) 
            for result in results:
                if result['success']:
                    self.contacts_id_list.append(result['id'])
                
            self.contacts_accounts_id = self.get_account_id()

        if self.contacts_phones_list:
            self.sf.bulk.vnfp__Legacy_Data__c.upsert(self.contacts_phones_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True) 

        if self.contacts_emails_list:
            self.sf.bulk.vnfp__Legacy_Data__c.upsert(self.contacts_emails_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True) 
            
        if self.contacts_act_phone:
            self.sf.bulk.Contact.upsert(self.contacts_act_phone, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)
            
        if self.contacts_act_email:
            self.sf.bulk.Contact.upsert(self.contacts_act_email, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)

        return self.contacts_accounts_id

    def process_contact_address(self):
        counter = 0
        object_key = f'{self.report_name}.csv'
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.DictReader(f, delimiter=';')
        data = list(reader)
        for row in data:
            counter += 1
            if 'Veevart Contacts Report Address test' == self.report_name:
                self.handle_contacts_addresses_report(row, self.contacts_accounts_id, counter)

        if self.contacts_address_list:
            self.sf.bulk.npsp__Address__c.upsert(self.contacts_address_list, 'vnfp__Implementation_External_ID__c', batch_size='auto',use_serial=True)  

# report_names = ["Veevart Organizations Report test","Veevart Organization Addresses Report test", "Veevart Organization Phones Report test", "Veevart HouseHolds Report test", "Veevart Contacts Report test", "Veevart Contacts Report Address test", "Veevart Contacts Report Email test", "Veevart Contacts Report Email test", "Veevart Contacts Report Phones test"]
# dic_accounts = {}
# dic_households_ids = {}
# for report_name in report_names:
#     processor = SalesforceProcessor(report_name, os.getenv('BUCKET_NAME'))  
#     processor.process_organizations()
#     processor.process_households()
#     dic_households_ids = {**dic_households_ids, **processor.process_households_ids()}
#     processor.households_ids = dic_households_ids
#     dic = processor.process_contacts()
#     dic_accounts = {**dic_accounts, **dic}
#     processor.process_contact_address()