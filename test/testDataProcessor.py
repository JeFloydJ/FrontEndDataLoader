import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(1, '../')
from Events.eventTransferDataOrganizations import DataProcessor

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
    #description: test test_delete_columns
    #return: result of the test delete_columns
    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader', return_value=iter([["header1", "header2", "header3"], ["value1", "value2", "value3"]]))
    @patch('csv.writer', return_value=MagicMock())
    def test_delete_columns(self, mock_writer, mock_reader, mock_open):
        self.processor.delete_columns("csv_input", ["header2"], "csv_output")

        self.assertEqual(mock_open.call_count, 2)
        mock_reader.assert_called_once()
        mock_writer.assert_called_once()

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
    #description: test process data
    #return: result of the test process data
    @patch.object(DataProcessor, 'get_id')
    @patch.object(DataProcessor, 'get_query')
    @patch.object(DataProcessor, 'json_to_csv')
    @patch.object(DataProcessor, 'delete_columns')
    @patch.object(DataProcessor, 'modify_csv_names')
    @patch.object(DataProcessor, 'modify_csv_phone')
    @patch('csv.reader', return_value=iter([["Name", "Last/Organization/Group/Household name", "Addresses\\Address", "Addresses\\ZIP"], ["name", "last_name", "address", "zip"]]))
    def test_process_data(self, mock_reader, mock_modify_csv_phone, mock_modify_csv_names, mock_delete_columns, mock_json_to_csv, mock_get_query, mock_get_id):
        self.processor.process_data()
        mock_get_id.assert_called()
        mock_get_query.assert_called()
        mock_json_to_csv.assert_called()
        mock_delete_columns.assert_called()
        mock_modify_csv_names.assert_called()
        mock_modify_csv_phone.assert_called()


if __name__ == '__main__':
    unittest.main()