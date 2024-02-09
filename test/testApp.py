# Import necessary modules
import sys
import unittest
from unittest.mock import patch
sys.path.insert(1, '../')
from app import app

#parameters: 
#description: test server, the server should obtain tokens in altru and salesforce
#return: result of the test
class TestApp(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        app.config['TESTING'] = True

    #parameters: 
    #description: test server, the server should obtain tokens in altru 
    #return: result of the test
    @patch('requests.post')
    def test_get_altru_token(self, mock_post):
        # Simulate a response from the Blackbaud API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'access', 'refresh_token': 'refresh'}

        # Simulate a GET request to the /skyapi/callback route with an authorization code
        response = self.app.get('/skyapi/callback?code=auth_code')

        # Verify that the function behaved as expected
        self.assertEqual(response.status_code, 302)  # The response should be a redirection

    #parameters: 
    #description: test server, the server should obtain tokens in salesforce
    #return: result of the test
    @patch('requests.post')
    def test_get_salesforce_token(self, mock_post):
        # Simulate a response from the Salesforce API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'access', 'refresh_token': 'refresh'}

        # Simulate a GET request to the /salesforce/callback route with an authorization code
        response = self.app.get('/salesforce/callback?code=auth_code')

        # Verify that the function behaved as expected
        self.assertEqual(response.status_code, 302)  # The response should be a redirection

    #parameters: 
    #description: test server, the server should render the main page
    #return: result of the test
    def test_index(self):
        # Test for the index route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)  # The response should be 200 OK

if __name__ == '__main__':
    # Run the tests
    unittest.main()
