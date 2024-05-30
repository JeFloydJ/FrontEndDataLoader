import io
import unittest
from unittest.mock import patch, MagicMock
import sys
import boto3
from io import StringIO
import csv
sys.path.insert(1, '../')
from Events.eventProcessData import DataProcessor
import unittest
import csv
import os
from Events.eventProcessData import DataProcessor  

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.data_processor = DataProcessor('test_path')  
    def test_modify_csv_households(self):
        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Other'])
            writer.writerow(['John Doe', 'Other Data'])

        self.data_processor.modify_csv_households('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Other'])  
        self.assertEqual(data[0][0], 'John ')  
        self.assertEqual(data[0][1], 'Other Data') 

        os.remove('test_input.csv')
        os.remove('test_output.csv')

    def test_modify_csv_names(self):
        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name', 'Email Addresses\\Email address', 'Web address'])
            writer.writerow(['John Doe', 'Smith Family', 'john@example.com', 'http://example.com/page'])

        self.data_processor.modify_csv_names('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name', 'Email Addresses\\Email address', 'Web address']) 
        self.assertEqual(data[0][0], 'John ')  
        self.assertEqual(data[0][1], 'xSmithx')  
        self.assertEqual(data[0][2], 'john@tmail.comx')  
        self.assertEqual(data[0][3], 'http://website.com/page')  

        os.remove('test_input.csv')
        os.remove('test_output.csv')

    def test_modify_csv_address(self):
        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name', 'Addresses\\Address', 'Addresses\\ZIP'])
            writer.writerow(['John Doe', 'Smith Family', '123 Main St Apt 4B', '12345'])

        self.data_processor.modify_csv_address('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name', 'Addresses\\Address', 'Addresses\\ZIP'])  # Verificar los encabezados
        self.assertEqual(data[0][0], 'John ')  
        self.assertEqual(data[0][1], 'xSmithx')  
        self.assertEqual(data[0][2], '123') 
        self.assertEqual(data[0][3], '12')  

        os.remove('test_input.csv')
        os.remove('test_output.csv')

    def test_modify_csv_phone(self):

        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name', 'Phones\\Number'])
            writer.writerow(['John Doe', 'Smith Family', '1234567890'])

        self.data_processor.modify_csv_phone('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name', 'Phones\\Number'])  
        self.assertEqual(data[0][0], 'John ') 
        self.assertEqual(data[0][1], 'xSmithx') 
        self.assertEqual(data[0][2], '12345')  

        os.remove('test_input.csv')
        os.remove('test_output.csv')


    def test_modify_csv_contacs_address(self):

        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name', 'Addresses\\Address', 'Addresses\\ZIP'])
            writer.writerow(['John Doe', 'Smith Family', '123 Main St Apt 4B', '12345'])

        self.data_processor.modify_csv_contacs_address('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name', 'Addresses\\Address', 'Addresses\\ZIP'])
        self.assertEqual(data[0][0], 'John ') 
        self.assertEqual(data[0][1], 'xSmithx')  
        self.assertEqual(data[0][2], '123')  
        self.assertEqual(data[0][3], '12')  

        os.remove('test_input.csv')
        os.remove('test_output.csv')

    def test_modify_csv_contacs_email(self):

        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name', 'Email Addresses\\Email address'])
            writer.writerow(['John Doe', 'Smith Family', 'john@example.com'])

        self.data_processor.modify_csv_contacs_email('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name', 'Email Addresses\\Email address'])  
        self.assertEqual(data[0][0], 'John ')  
        self.assertEqual(data[0][1], 'xSmithx')  
        self.assertEqual(data[0][2], 'john@tmail.comx')  

        os.remove('test_input.csv')
        os.remove('test_output.csv')

    def test_modify_csv_contacs(self):
        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name'])
            writer.writerow(['John Doe', 'Smith Family'])

        self.data_processor.modify_csv_contacs('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name']) 
        self.assertEqual(data[0][0], 'John ') 
        self.assertEqual(data[0][1], 'xSmithx') 

        os.remove('test_input.csv')
        os.remove('test_output.csv')

    def test_modify_csv_phones(self):

        with open('test_input.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Last/Organization/Group/Household name', 'Phones\\Number'])
            writer.writerow(['John Doe', 'Smith Family', '1234567890'])

        self.data_processor.modify_csv_phones('test_input.csv', 'test_output.csv')

        with open('test_output.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)

        self.assertEqual(headers, ['Name', 'Last/Organization/Group/Household name', 'Phones\\Number']) 
        self.assertEqual(data[0][0], 'John ') 
        self.assertEqual(data[0][1], 'xSmithx')  
        self.assertEqual(data[0][2], '12345')  

        os.remove('test_input.csv')
        os.remove('test_output.csv')

if __name__ == '__main__':
    unittest.main()

