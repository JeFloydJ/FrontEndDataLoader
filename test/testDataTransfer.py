import unittest
from unittest.mock import mock_open, patch, MagicMock
import sys
sys.path.insert(1, '../')
from Events.eventDataTransfer import SalesforceProcessor

#parameters: 
#description: test class that sent data to salesforce
#return: result of the test
class TestSalesforceProcessor(unittest.TestCase):

    #parameters: 
    #description: set config to test
    #return: result of the test
    @patch('os.getenv')
    @patch('builtins.open')
    @patch('Events.eventDataTransfer.Salesforce')
    def setUp(self, mock_salesforce, mock_open, mock_getenv):

        mock_getenv.return_value = 'test_value'
        
        self.mock_sf_instance = MagicMock()
        mock_salesforce.return_value = self.mock_sf_instance
        
        self.mock_account_instance = MagicMock()
        self.mock_sf_instance.bulk.Account = self.mock_account_instance
        
        mock_response = {'records': [{'Id': 'test_id'}]}
        
        self.mock_sf_instance.query.return_value = mock_response
        

        mock_open.return_value.__enter__.return_value.read.return_value = 'test_token@salesforce.com'
        
        self.processor = SalesforceProcessor('test_report')

    #parameters: 
    #description: test get households id
    #return: result of the test
    def test_get_households_id(self):

        result = self.processor.get_households_id()
        

        self.assertEqual(result, 'test_id')

    #parameters: 
    #description: set organization id
    #return: result of the test
    def test_get_organizations_id(self):
        result = self.processor.get_organizations_id()
        self.assertEqual(result, 'test_id')

    #parameters: 
    #description: sget accounts id
    #return: result of the test
    def test_get_account_id(self):
    
        mock_response = {'records': [{'Auctifera__Implementation_External_ID__c': 'test_id', 'AccountId': 'test_account_id'}]}
        

        self.mock_sf_instance.query_all.return_value = mock_response
   
        result = self.processor.get_account_id()
        
        self.assertEqual(result, {'test_id': 'test_account_id'})
    
    #parameters: 
    #description: test extract code to string (123-householdsa-test_id)
    #return: result of the test
    def test_find_households_id(self):
        lst = ['123-households-test_id']
        result = self.processor.find_households_id(lst)
        self.assertEqual(result, {'test_id': '123-households-test_id'})

    #parameters: 
    #description: test create organization object
    #return: result of the test
    def test_handle_organizations_report(self):
        row = {
            "Lookup ID": "test_id",
            "Name": "test_name",
            "Web address": "test_address",
            "Email Addresses\\Do not email": "",
            "Email Addresses\\Email address": ""  
        }
        self.processor.handle_organizations_report(row)
        self.assertEqual(self.processor.account_list[0]['Auctifera__Implementation_External_ID__c'], 'test_id')

    #parameters: 
    #description: test create organization address object
    #return: result of the test
    def test_handle_organization_addresses_report(self):
        row = {
            "Lookup ID": "test_id",
            "Addresses\\Address": "test_address",
            "Addresses\\City": "test_city",
            "Addresses\\State": "test_state",
            "Addresses\\ZIP": "test_zip",
            "Addresses\\Country": "test_country",
            "Addresses\\Primary address": "",
            "QUERYRECID": "test_queryrecid"
        }
        self.processor.handle_organization_addresses_report(row, 1)
        self.assertEqual(self.processor.address_list[0]['npsp__MailingStreet__c'], 'test_address')

    #parameters: 
    #description: test organization phone object
    #return: result of the test
    def test_handle_organization_phone_report(self):
  
        counter = 1  

        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "QUERYRECID" : "1234"
        }
        
  
        self.processor.handle_organization_phone_report(row, counter) 
       
        self.assertEqual(self.processor.phone_list[0]['vnfp__value__c'], "123")
        self.assertEqual(self.processor.phone_list[0]['vnfp__Type__c'], "Phone")
        self.assertEqual(self.processor.phone_list[0]['vnfp__Account__r'], {'Auctifera__Implementation_External_ID__c': 'test_id'})

    #parameters: 
    #description: test phone update in account object
    #return: result of the test
    def test_handler_update_phone_organization(self):

        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "Phones\\Primary phone number": True  
        }
        
        self.processor.handler_update_phone_organization(row)
        
        
        if row['Phones\\Primary phone number']:
         
            self.assertEqual(self.processor.phone_act_list[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.phone_act_list[0]['Phone'], "123")
        else:
            
            self.assertEqual(len(self.processor.phone_act_list), 0)

    #parameters: 
    #description: test update address in account object
    #return: result of the test
    def test_handler_update_address_organization(self):

        row = {
            "Lookup ID": "test_id",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": True 
        }

        self.processor.handler_update_address_organization(row)
        
        
        if row['Addresses\\Primary address']:

            self.assertEqual(self.processor.address_act_list[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.address_act_list[0]['BillingStreet'], "123 Street")
            self.assertEqual(self.processor.address_act_list[0]['BillingCity'], "Test City")
            self.assertEqual(self.processor.address_act_list[0]['BillingState'], "Test State")
            self.assertEqual(self.processor.address_act_list[0]['BillingPostalCode'], "12345")
            self.assertEqual(self.processor.address_act_list[0]['BillingCountry'], "Test Country")
        else:
          
            self.assertEqual(len(self.processor.address_act_list), 0)

    #parameters: 
    #description: test create household obejct
    #return: result of the test            
    def test_handler_households(self):

        row = {
            "Name": "Test Name",
            "QUERYRECID": "123"
        }
        
        counter = 1
        
        self.processor.handler_households(row, counter)
        
        self.assertEqual(self.processor.houseHolds_external_ids_list[0], "1-households-123")
        self.assertEqual(self.processor.houseHolds_list[0]['RecordTypeId'], self.processor.households_id)
        self.assertEqual(self.processor.houseHolds_list[0]['Auctifera__Implementation_External_ID__c'], "1-households-123")
        self.assertEqual(self.processor.houseHolds_list[0]['Name'], "Test Name")

    #parameters: 
    #description: test create contact object
    #return: result of the test
    def test_handler_contacts_report(self):

        row = {
            "Title": "Test Title",
            "First name": "Test First Name",
            "Last/Organization/Group/Household name": "Test Last Name",
            "Lookup ID": "test_id",
            "Notes\\Notes": "Test Notes",
            "Gender": "Test Gender",
            "Households Belonging To\\Household Record ID": "test_account_id"
        }
        
        dic = {
            "test_account_id": "test_account_external_id"
        }
        
        self.processor.handler_contacts_report(row, dic)
        
        self.assertEqual(self.processor.contacts_list[0]['Salutation'], "Test Title")
        self.assertEqual(self.processor.contacts_list[0]['FirstName'], "Test First Name")
        self.assertEqual(self.processor.contacts_list[0]['LastName'], "Test Last Name")
        self.assertEqual(self.processor.contacts_list[0]['Auctifera__Implementation_External_ID__c'], "test_id")
        self.assertEqual(self.processor.contacts_list[0]['Description'], "Test Notes")
        self.assertEqual(self.processor.contacts_list[0]['GenderIdentity'], "Test Gender")
        self.assertEqual(self.processor.contacts_list[0]['Account'], {'Auctifera__Implementation_External_ID__c': 'test_account_external_id'})

    #parameters: 
    #description: test create phone in contact object
    #return: result of the test
    def test_handle_contacts_phone_report(self):
        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "QUERYRECID": "456"
        }
        
        counter = 1
        
        
        self.processor.handle_contacts_phone_report(row, counter)
        
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__Type__c'], "Phone")
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__value__c'], "123")
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__Contact__r'], {'Auctifera__Implementation_External_ID__c': 'test_id'})
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__Implementation_External_ID__c'], "1-phone-456")

    #parameters: 
    #description: test contact create email in contact object
    #return: result of the test
    def test_handle_contacts_emails_report(self):
        row = {
            "Lookup ID": "test_id",
            "Email Addresses\\Email address": "test@example.com",
            "QUERYRECID": "456"
        }
        
        counter = 1
        
        self.processor.handle_contacts_emails_report(row, counter)
        
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__Type__c'], "Email")
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__value__c'], "test@example.com")
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__Contact__r'], {'Auctifera__Implementation_External_ID__c': 'test_id'})
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__Implementation_External_ID__c'], "1-contacts-email-456")
 
    #parameters: 
    #description: test create address object in contact object
    #return: result of the test
    def test_handle_contacts_addresses_report(self):
        row = {
            "Lookup ID": "test_id",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": "Yes",  
            "QUERYRECID": "456"
        }
        
        dic = {
            "test_id": "test_account_id"
        }
        
        counter = 1
        
        self.processor.handle_contacts_addresses_report(row, dic, counter)        

        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingStreet__c'], "123 Street")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingCity__c'], "Test City")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingState__c'], "Test State")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingPostalCode__c'], "12345")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingCountry__c'], "Test Country")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__Household_Account__c'], "test_account_id")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__Default_Address__c'], True)
        self.assertEqual(self.processor.contacts_address_list[0]['vnfp__Implementation_External_ID__c'], "1-contacts-address-contacts456")
 
    #parameters: 
    #description: test update phone in contact object
    #return: result of the test
    def test_handle_contacts_update_phone(self):

        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "Phones\\Primary phone number": "Yes"  
        }
        
        self.processor.handle_contacts_update_phone(row)
        
        if row['Phones\\Primary phone number']:
            self.assertEqual(self.processor.contacts_act_phone[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.contacts_act_phone[0]['Phone'], "123")
        else:
            self.assertEqual(len(self.processor.contacts_act_phone), 1)

    #parameters: 
    #description: test create update email in contact object
    #return: result of the test
    def test_handle_contacts_update_email(self):
        row = {
            "Lookup ID": "test_id",
            "Email Addresses\\Email address": "test@example.com",
            "Email Addresses\\Primary email address": "Yes"  
        }
        
        self.processor.handle_contacts_update_email(row)
        
        if row['Email Addresses\\Primary email address'] and self.processor.valid_check.get(row['Lookup ID'], None) == None:
            self.assertEqual(self.processor.contacts_act_email[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.contacts_act_email[0]['Email'], "test@example.com")
        else:
            self.assertEqual(len(self.processor.contacts_act_email), 1)

    #parameters: 
    #description: test create objects  and sent organization data to salesforce 
    #return: result of the test
    @patch('csv.DictReader')
    def test_process_organizations(self, mock_dict_reader):

        row = {
            "Lookup ID": "test_id",
            "Name": "Test Name",
            "Web address": "www.test.com",
            "Phones\\Number": "123",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": "Yes",
            "Email Addresses\\Email address": "",  
            "Email Addresses\\Do not email": "",
            "QUERYRECID": "456"
            }
        self.processor.report_name = 'Veevart Organizations Report test'
        
        mock_dict_reader.return_value = [row]
        
        self.processor.process_organizations()
        
        self.processor.sf.bulk.Account.upsert.assert_called_once_with(self.processor.account_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto', use_serial=True)

    #parameters: 
    #description: test create objects and sent household data to salesforce 
    #return: result of the test
    @patch('csv.DictReader')
    def test_process_households(self, mock_dict_reader):
        row = {
            "Lookup ID": "test_id",
            "Name": "Test Name",
            "Web address": "www.test.com",
            "Phones\\Number": "123",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": "Yes",
            "Email Addresses\\Do not email": "",
            "QUERYRECID": "456"
        }
        
        self.processor.report_name = 'Veevart HouseHolds Report test'
        
        mock_dict_reader.return_value = [row]
        
        result = self.processor.process_households()
        
        self.processor.sf.bulk.Account.upsert.assert_called_once_with(self.processor.houseHolds_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto', use_serial=True)
        
        self.assertEqual(result, self.processor.houseHolds_external_ids_list)

    #parameters: 
    #description: test extract households id 
    #return: result of the test
    def test_process_households_ids(self):
        self.processor.houseHolds_external_ids_list = ['123-households-test_id']
        
        result = self.processor.process_households_ids()
        
        self.assertEqual(result, {'test_id': '123-households-test_id'})

    #parameters: 
    #description: test create objects  and sent contacts data to salesforce 
    #return: result of the test
    @patch('csv.DictReader')
    def test_process_contacts(self, mock_dict_reader):
        row = {
            "Lookup ID": "test_id",
            "Name": "Test Name",
            "Web address": "www.test.com",
            "Phones\\Number": "123",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": True,
            "Email Addresses\\Do not email": "",
            "Households Belonging To\\Household Record ID": "test_household_id",
            "First name": "Test First Name",
            "Title" : "Mr.",
            "Last/Organization/Group/Household name" : "test householdsname",
            "Notes\\Notes" : "nota test",
            "GenderIdentity" : "Male",
            "Gender" : "Male",
            "QUERYRECID": "456"
        }
        
        self.processor.report_name = 'Veevart Contacts Report test'
        
        self.processor.households_ids = {'test_household_id': 'test_account_id'}
        
        mock_dict_reader.return_value = [row]
        
        result = self.processor.process_contacts()
        
        self.processor.sf.bulk.Contact.upsert.assert_called_once_with(self.processor.contacts_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto', use_serial=True)
        
        self.assertEqual(result, self.processor.contacts_accounts_id)

    #parameters: 
    #description: test create objects and sent address of organization data to salesforce 
    #return: result of the test
    @patch('csv.DictReader')
    def test_process_contact_address(self, mock_dict_reader):
        row = {
            "Lookup ID": "test_id",
            "Name": "Test Name",
            "Web address": "www.test.com",
            "Phones\\Number": "123",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": True,
            "Email Addresses\\Do not email": "",
            "Households Belonging To\\Household Record ID": "test_household_id",
            "First name": "Test First Name",
            "Title" : "Mr.",
            "Last/Organization/Group/Household name" : "test householdsname",
            "Notes\\Notes" : "nota test",
            "GenderIdentity" : "Male",
            "Gender" : "Male",
            "QUERYRECID": "456"
        }
        
        self.processor.report_name = 'Veevart Contacts Report Address test'
        
        self.processor.contacts_accounts_id = {'test_id': 'test_account_id'}
        
        mock_dict_reader.return_value = [row]
        
        self.processor.process_contact_address()

        self.processor.sf.bulk.npsp__Address__c.upsert.assert_called_once_with(self.processor.contacts_address_list, 'vnfp__Implementation_External_ID__c', batch_size='auto', use_serial=True)

if __name__ == '__main__':
    unittest.main()