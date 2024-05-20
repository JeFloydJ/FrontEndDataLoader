import io
import unittest
from unittest.mock import patch, MagicMock
import sys
import boto3
from io import StringIO
import csv
sys.path.insert(1, '../')
from Events.eventProcessData import DataProcessor

class TestDataProcessor(unittest.TestCase):
    @patch('boto3.client')
    def setUp(self, mock_boto3_client):
        self.mock_s3 = MagicMock()
        mock_boto3_client.return_value = self.mock_s3
        self.data_processor = DataProcessor('test_bucket')

    def test_modify_csv_names(self):
        
        #set data for test
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address\nJohn Doe;Doe;john.doe@example.com;http://example.com'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}
        
        #call method for test
        self.data_processor.modify_csv_names('test_key')

        #verify if have been called the correct method with correct arguments
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        #verify if the data is correct
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@tmail.comx;http://website.com', modified_data)

    def test_modify_csv_address(self):

        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address;Addresses\\Address;Addresses\\ZIP\nJohn Doe;Doe;john.doe@example.com;http://example.com;123 Main St;12345'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

 
        self.data_processor.modify_csv_address('test_key')


        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

 
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@example.com;http://example.com;123;12', modified_data)

    def test_modify_csv_phones(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address;Phones\\Number\nJohn Doe;Doe;john.doe@example.com;http://example.com;1234567890'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_phones('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john@tmail.comx;http://example.com;12345', modified_data)

    def test_modify_csv_phones(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address;Phones\\Number\nJohn Doe;Doe;john.doe@example.com;http://example.com;1234567890'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_phones('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@example.com;http://example.com;12345', modified_data)

    def test_modify_csv_households(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address\nJohn Doe;Doe;john.doe@example.com;http://example.com'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_households('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;Doe;john.doe@example.com;http://example.com', modified_data)

    def test_modify_csv_contacs(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address\nJohn Doe;Doe;john.doe@example.com;http://example.com'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_contacs('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@example.com;http://example.com', modified_data)

    def test_modify_csv_contacts_phones(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address;Phones\\Number\nJohn Doe;Doe;john.doe@example.com;http://example.com;1234567890'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_contacts_phones('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@example.com;http://example.com;12345', modified_data)

    def test_modify_csv_contacs_email(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address\nJohn Doe;Doe;john.doe@example.com;http://example.com'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_contacs_email('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@tmail.comx;http://example.com\r\n', modified_data)

    def test_modify_csv_contacs_address(self):
        # Preparar los datos de prueba
        csv_data = b'Name;Last/Organization/Group/Household name;Email Addresses\\Email address;Web address;Addresses\\Address;Addresses\\ZIP\nJohn Doe;Doe;john.doe@example.com;http://example.com;123 Main St;12345'
        self.mock_s3.get_object.return_value = {'Body': io.BytesIO(csv_data)}

        # Llamar al método que se está probando
        self.data_processor.modify_csv_contacs_address('test_key')

        # Verificar que se llamó a los métodos esperados con los argumentos correctos
        self.mock_s3.get_object.assert_called_once_with(Bucket='test_bucket', Key='test_key')
        self.mock_s3.put_object.assert_called_once()

        # Verificar que los datos modificados son correctos
        modified_data = self.mock_s3.put_object.call_args[1]['Body']
        self.assertIn('John ;xDoex;john.doe@example.com;http://example.com;123;12', modified_data)



if __name__ == '__main__':
    unittest.main()

