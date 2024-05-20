import os
import unittest
from unittest.mock import mock_open, patch, MagicMock
import sys
sys.path.insert(1, '../')
from Events.eventTransferDataOrganizations import DataProcessor
from Events.eventTransferDataOrganizations import SalesforceProcessor
from Events.eventTransferDataOrganizations import Adapter
#parameters: 
#description: test class that get info in sky api
#return: result of the test
class TestDataProcessor(unittest.TestCase):
 
    #set up class DataProcessor
    def setUp(self):
        self.processor = DataProcessor()

    #parameters: 
    #description: test refresh token
    #return: result of the test refresh token
    @patch('builtins.open', new_callable=MagicMock)
    @patch('requests.post', return_value=MagicMock())
    def test_refresh_token(self, mock_post, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = 'token'
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "new_token"}

        self.processor.refresh_token()

        mock_post.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test get id 
    #return: result of the get id
    @patch('requests.request', return_value=MagicMock())
    def test_get_id(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.text = '{"id": "123"}'

        id_value = self.processor.get_id("report_name")

        self.assertEqual(id_value, "123")
        mock_request.assert_called_once()

    #parameters: 
    #description: test get query
    #return: result of the test get query
    @patch('requests.request', return_value=MagicMock())
    def test_get_query(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.text = '{"query": "query"}'

        self.processor.get_query("id", "report_name")

        mock_request.assert_called_once()

    #parameters: 
    #description: test json to csv
    #return: result of the json to csv
    @patch('builtins.open', new_callable=MagicMock)
    @patch('json.load', return_value={"field_names": ["field1", "field2"], "rows": [["value1", "value2"]]})
    @patch('csv.writer', return_value=MagicMock())
    def test_json_to_csv(self, mock_writer, mock_load, mock_open):
        self.processor.json_to_csv("json_file_path", "csv_file_path")
        mock_load.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)


    #parameters: 
    #description: test modify csv name
    #return: result of the test modify csv name
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", "Email Addresses\\Email address", "Web address"], ["name", "last_name", "email@example.com", "http://example.com"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_names(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_names("input_csv", "output_csv")

        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test modify csv phone
    #return: result of the test csv phone
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", "Phones\\Number"], ["name", "last_name", "1234567890"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_phone(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_phone("input_csv", "output_csv")

        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test modify csv households
    #return: result of the test csv households
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name"], ["name", "last_name"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_households(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_households("input_csv", "output_csv")

        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test modify csv contacts
    #return: result of the test csv contacts
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name"], ["name", "last_name"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_contacts(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_contacs("input_csv", "output_csv")

        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test modify csv address of contacts
    #return: result of the test csv address of contacts
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", 'Addresses\\Address', 'Addresses\\ZIP'], ["name", "last_name", "address", "0000"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_contacs_address(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_contacs_address("input_csv", "output_csv")

        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test modify csv emails of contacts
    #return: result of the test csv emails of contacts
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", "Email Addresses\\Email address"], ["name", "last_name", "asdadadasd@asdadasdasd.com"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_contacs_email(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_contacs_email("input_csv", "output_csv")
        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test modify csv phones of contacts
    #return: result of the test csv phones of contacts
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", "Phones\\Number"], ["name", "last_name", "3123123213"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_modify_csv_contacs_phones(self, mock_writer, mock_reader, mock_open):
        self.processor.modify_csv_phones("input_csv", "output_csv")
        mock_reader.assert_called_once()
        mock_writer.assert_called_once()
        self.assertEqual(mock_open.call_count, 2)

    #parameters: 
    #description: test process data
    #return: result of the test process data
    @patch.object(DataProcessor, 'get_id')
    @patch.object(DataProcessor, 'get_query')
    @patch.object(DataProcessor, 'json_to_csv')
    @patch.object(DataProcessor, 'modify_csv_names')
    @patch.object(DataProcessor, 'modify_csv_phone')
    @patch.object(DataProcessor, 'modify_csv_households')
    @patch.object(DataProcessor, 'modify_csv_contacs')
    @patch.object(DataProcessor, 'modify_csv_contacs_address')
    @patch.object(DataProcessor, 'modify_csv_contacs_email')
    @patch.object(DataProcessor, 'modify_csv_phones')
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", "Addresses\\Address", "Addresses\\ZIP"], ["name", "last_name", "address", "zip"]]))
    def test_process_data(self, mock_reader, mock_modify_csv_phone, mock_modify_csv_names, mock_modify_csv_households, mock_modify_csv_contacs , mock_modify_csv_contacs_address, mock_modify_csv_contacs_email, mock_modify_csv_phones , mock_json_to_csv, mock_get_query, mock_get_id):
        self.processor.process_data()
        mock_get_id.assert_called()
        mock_get_query.assert_called()
        mock_json_to_csv.assert_called()
        mock_modify_csv_names.assert_called()
        mock_modify_csv_phone.assert_called()
        mock_modify_csv_households.assert_called()
        mock_modify_csv_contacs.assert_called()
        mock_modify_csv_contacs_address.assert_called()
        mock_modify_csv_contacs_email.assert_called()
        mock_modify_csv_phones.assert_called()



class TestSalesforceProcessor(unittest.TestCase):
    @patch('os.getenv')
    @patch('builtins.open')
    @patch('Events.eventTransferDataOrganizations.Salesforce')
    def setUp(self, mock_salesforce, mock_open, mock_getenv):
        # Mock the getenv calls
        mock_getenv.return_value = 'test_value'
        
        # Mock the Salesforce instance
        self.mock_sf_instance = MagicMock()
        mock_salesforce.return_value = self.mock_sf_instance
        
        # Mock the Salesforce Account instance
        self.mock_account_instance = MagicMock()
        self.mock_sf_instance.bulk.Account = self.mock_account_instance
        
        # Define the mock response
        mock_response = {'records': [{'Id': 'test_id'}]}
        
        # Set the mock response to the query method of the mock Salesforce instance
        self.mock_sf_instance.query.return_value = mock_response
        
        # Mock the open calls
        mock_open.return_value.__enter__.return_value.read.return_value = 'test_token@salesforce.com'
        
        # Now that the mock response is set, instantiate SalesforceProcessor
        self.processor = SalesforceProcessor('test_report')



    def test_get_households_id(self):
        # Call the method under test
        result = self.processor.get_households_id()
        
        # Assert that the result is as expected
        self.assertEqual(result, 'test_id')

    def test_get_organizations_id(self):
        result = self.processor.get_organizations_id()
        self.assertEqual(result, 'test_id')

    def test_get_account_id(self):
        # Define the mock response
        mock_response = {'records': [{'Auctifera__Implementation_External_ID__c': 'test_id', 'AccountId': 'test_account_id'}]}
        
        # Set the mock response to the query_all method of the mock Salesforce instance
        self.mock_sf_instance.query_all.return_value = mock_response
        
        # Call the method under test
        result = self.processor.get_account_id()
        
        # Assert that the result is as expected
        self.assertEqual(result, {'test_id': 'test_account_id'})
    
    def test_find_households_id(self):
        lst = ['123-households-test_id']
        result = self.processor.find_households_id(lst)
        self.assertEqual(result, {'test_id': '123-households-test_id'})

    def test_handle_organizations_report(self):
        row = {
            "Lookup ID": "test_id",
            "Name": "test_name",
            "Web address": "test_address",
            "Email Addresses\\Do not email": ""
        }
        self.processor.handle_organizations_report(row)
        self.assertEqual(self.processor.account_list[0]['Auctifera__Implementation_External_ID__c'], 'test_id')

    def test_handle_addresses_report(self):
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
        self.processor.handle_addresses_report(row, 1)
        self.assertEqual(self.processor.address_list[0]['npsp__MailingStreet__c'], 'test_address')

    def test_handle_phone_report(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123"
        }
        
        # Call the method under test
        self.processor.handle_phone_report(row)  # Removed the second argument here
        
        # Assert that the result is as expected
        self.assertEqual(self.processor.phone_list[0]['vnfp__value__c'], "123")
        self.assertEqual(self.processor.phone_list[0]['vnfp__Type__c'], "Phone")
        self.assertEqual(self.processor.phone_list[0]['vnfp__Account__r'], {'Auctifera__Implementation_External_ID__c': 'test_id'})

    def test_handler_update_phone_organization(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "Phones\\Primary phone number": True  # or False, depending on what you want to test
        }
        
        # Call the method under test
        self.processor.handler_update_phone_organization(row)
        
        # If 'Phones\\Primary phone number' is True, then new_info should have been appended to phone_act_list
        if row['Phones\\Primary phone number']:
            # Assert that the result is as expected
            self.assertEqual(self.processor.phone_act_list[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.phone_act_list[0]['Phone'], "123")
        else:
            # If 'Phones\\Primary phone number' is False, then phone_act_list should still be empty
            self.assertEqual(len(self.processor.phone_act_list), 0)

    def test_handler_update_address_organization(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": True  # or False, depending on what you want to test
        }
        
        # Call the method under test
        self.processor.handler_update_address_organization(row)
        
        # If 'Addresses\\Primary address' is True, then new_info should have been appended to address_act_list
        if row['Addresses\\Primary address']:
            # Assert that the result is as expected
            self.assertEqual(self.processor.address_act_list[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.address_act_list[0]['BillingStreet'], "123 Street")
            self.assertEqual(self.processor.address_act_list[0]['BillingCity'], "Test City")
            self.assertEqual(self.processor.address_act_list[0]['BillingState'], "Test State")
            self.assertEqual(self.processor.address_act_list[0]['BillingPostalCode'], "12345")
            self.assertEqual(self.processor.address_act_list[0]['BillingCountry'], "Test Country")
        else:
            # If 'Addresses\\Primary address' is False, then address_act_list should still be empty
            self.assertEqual(len(self.processor.address_act_list), 0)
    def test_handler_households(self):
        # Define the original row
        row = {
            "Name": "Test Name",
            "QUERYRECID": "123"
        }
        
        # Define a counter
        counter = 1
        
        # Call the method under test
        self.processor.handler_households(row, counter)
        
        # Assert that the result is as expected
        self.assertEqual(self.processor.houseHolds_external_ids_list[0], "1-households-123")
        self.assertEqual(self.processor.houseHolds_list[0]['RecordTypeId'], self.processor.households_id)
        self.assertEqual(self.processor.houseHolds_list[0]['Auctifera__Implementation_External_ID__c'], "1-households-123")
        self.assertEqual(self.processor.houseHolds_list[0]['Name'], "Test Name")

    def test_handler_contacts(self):
        # Define the original row
        row = {
            "Title": "Test Title",
            "First name": "Test First Name",
            "Last/Organization/Group/Household name": "Test Last Name",
            "Lookup ID": "test_id",
            "Notes\\Notes": "Test Notes",
            "Gender": "Test Gender",
            "Households Belonging To\\Household Record ID": "test_account_id"
        }
        
        # Define the dictionary
        dic = {
            "test_account_id": "test_account_external_id"
        }
        
        # Call the method under test
        self.processor.handler_contacts(row, dic)
        
        # Assert that the result is as expected
        self.assertEqual(self.processor.contacts_list[0]['Salutation'], "Test Title")
        self.assertEqual(self.processor.contacts_list[0]['FirstName'], "Test First Name")
        self.assertEqual(self.processor.contacts_list[0]['LastName'], "Test Last Name")
        self.assertEqual(self.processor.contacts_list[0]['Auctifera__Implementation_External_ID__c'], "test_id")
        self.assertEqual(self.processor.contacts_list[0]['Description'], "Test Notes")
        self.assertEqual(self.processor.contacts_list[0]['GenderIdentity'], "Test Gender")
        self.assertEqual(self.processor.contacts_list[0]['Account'], {'Auctifera__Implementation_External_ID__c': 'test_account_external_id'})

    def test_handle_contacts_phone_report(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "QUERYRECID": "456"
        }
        
        # Define a counter
        counter = 1
        
        # Call the method under test
        self.processor.handle_contacts_phone_report(row, counter)
        
        # Assert that the result is as expected
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__Type__c'], "Phone")
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__value__c'], "123")
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__Contact__r'], {'Auctifera__Implementation_External_ID__c': 'test_id'})
        self.assertEqual(self.processor.contacts_phones_list[0]['vnfp__Implementation_External_ID__c'], "1-phone-456")

    def test_handle_contacts_emails_report(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Email Addresses\\Email address": "test@example.com",
            "QUERYRECID": "456"
        }
        
        # Define a counter
        counter = 1
        
        # Call the method under test
        self.processor.handle_contacts_emails_report(row, counter)
        
        # Assert that the result is as expected
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__Type__c'], "Email")
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__value__c'], "test@example.com")
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__Contact__r'], {'Auctifera__Implementation_External_ID__c': 'test_id'})
        self.assertEqual(self.processor.contacts_emails_list[0]['vnfp__Implementation_External_ID__c'], "1-contacts-email-456")
    def test_handle_contacts_addresses_report(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Addresses\\Address": "123 Street",
            "Addresses\\City": "Test City",
            "Addresses\\State": "Test State",
            "Addresses\\ZIP": "12345",
            "Addresses\\Country": "Test Country",
            "Addresses\\Primary address": True,  # or False, depending on what you want to test
            "QUERYRECID": "456"
        }
        
        # Define the dictionary
        dic = {
            "test_id": "test_account_id"
        }
        
        # Define a counter
        counter = 1
        
        # Call the method under test
        self.processor.handle_contacts_addresses_report(row, dic, counter)
        
        # Assert that the result is as expected
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingStreet__c'], "123 Street")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingCity__c'], "Test City")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingState__c'], "Test State")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingPostalCode__c'], "12345")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__MailingCountry__c'], "Test Country")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__Household_Account__c'], "test_account_id")
        self.assertEqual(self.processor.contacts_address_list[0]['npsp__Default_Address__c'], True)
        self.assertEqual(self.processor.contacts_address_list[0]['vnfp__Implementation_External_ID__c'], "1-contacts-address-contacts456")
    def test_handle_contacts_update_phone(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Phones\\Number": "123",
            "Phones\\Primary phone number": True  # or False, depending on what you want to test
        }
        
        # Call the method under test
        self.processor.handle_contacts_update_phone(row)
        
        # If 'Phones\\Primary phone number' is True, then new_info should have been appended to contacts_act_phone
        if row['Phones\\Primary phone number']:
            # Assert that the result is as expected
            self.assertEqual(self.processor.contacts_act_phone[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.contacts_act_phone[0]['Phone'], "123")
        else:
            # If 'Phones\\Primary phone number' is False, then contacts_act_phone should still be empty
            self.assertEqual(len(self.processor.contacts_act_phone), 1)

    def test_handle_contacts_update_email(self):
        # Define the original row
        row = {
            "Lookup ID": "test_id",
            "Email Addresses\\Email address": "test@example.com",
            "Email Addresses\\Primary email address": True  # or False, depending on what you want to test
        }
        
        # Call the method under test
        self.processor.handle_contacts_update_email(row)
        
        # If 'Email Addresses\\Primary email address' is True and 'Lookup ID' is not in valid_check, then new_info should have been appended to contacts_act_email
        if row['Email Addresses\\Primary email address'] and self.processor.valid_check.get(row['Lookup ID'], None) == None:
            # Assert that the result is as expected
            self.assertEqual(self.processor.contacts_act_email[0]['Auctifera__Implementation_External_ID__c'], "test_id")
            self.assertEqual(self.processor.contacts_act_email[0]['Email'], "test@example.com")
        else:
            # If 'Email Addresses\\Primary email address' is False or 'Lookup ID' is in valid_check, then contacts_act_email should still be empty
            self.assertEqual(len(self.processor.contacts_act_email), 1)

    @patch('csv.DictReader')
    def test_process_organizations(self, mock_dict_reader):
        # Define the original row
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
            "Email Addresses\\Do not email": "",  # Agrega esta línea
            "QUERYRECID": "456"
        }
                # Define the report name
        self.processor.report_name = 'Veevart Organizations Report test'
        
        # Mock the CSV reader
        mock_dict_reader.return_value = [row]
        
        # Call the method under test
        self.processor.process_organizations()
        
        # Assert that the Salesforce methods were called with the correct arguments
        self.processor.sf.bulk.Account.upsert.assert_called_once_with(self.processor.account_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto', use_serial=True)

    @patch('csv.DictReader')
    def test_process_households(self, mock_dict_reader):
        # Define the original row
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
            "QUERYRECID": "456"
        }
        
        # Define the report name
        self.processor.report_name = 'Veevart HouseHolds Report test'
        
        # Mock the CSV reader
        mock_dict_reader.return_value = [row]
        
        # Call the method under test
        result = self.processor.process_households()
        
        # Assert that the Salesforce methods were called with the correct arguments
        self.processor.sf.bulk.Account.upsert.assert_called_once_with(self.processor.houseHolds_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto', use_serial=True)
        
        # Assert that the method returns the expected result
        self.assertEqual(result, self.processor.houseHolds_external_ids_list)

    def test_process_households_ids(self):
        # Define the households external IDs list
        self.processor.houseHolds_external_ids_list = ['123-households-test_id']
        
        # Call the method under test
        result = self.processor.process_households_ids()
        
        # Assert that the method returns the expected result
        self.assertEqual(result, {'test_id': '123-households-test_id'})

    @patch('csv.DictReader')
    def test_process_contacts(self, mock_dict_reader):
        # Define the original row
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
        
        # Define the report name
        self.processor.report_name = 'Veevart Contacts Report test'
        
        # Define the households_ids
        self.processor.households_ids = {'test_household_id': 'test_account_id'}
        
        # Mock the CSV reader
        mock_dict_reader.return_value = [row]
        
        # Call the method under test
        result = self.processor.process_contacts()
        
        # Assert that the Salesforce methods were called with the correct arguments
        self.processor.sf.bulk.Contact.upsert.assert_called_once_with(self.processor.contacts_list, 'Auctifera__Implementation_External_ID__c', batch_size='auto', use_serial=True)
        
        # Assert that the method returns the expected result
        self.assertEqual(result, self.processor.contacts_accounts_id)

    @patch('csv.DictReader')
    def test_process_contact_address(self, mock_dict_reader):
        # Define the original row
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
        
        # Define the report name
        self.processor.report_name = 'Veevart Contacts Report Address test'
        
        # Define the contacts_accounts_id
        self.processor.contacts_accounts_id = {'test_id': 'test_account_id'}
        
        # Mock the CSV reader
        mock_dict_reader.return_value = [row]
        
        # Call the method under test
        self.processor.process_contact_address()
        
        # Assert that the Salesforce methods were called with the correct arguments
        self.processor.sf.bulk.npsp__Address__c.upsert.assert_called_once_with(self.processor.contacts_address_list, 'vnfp__Implementation_External_ID__c', batch_size='auto', use_serial=True)



if __name__ == '__main__':
    unittest.main()