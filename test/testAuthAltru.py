# Import necessary modules
import unittest
import sys
sys.path.insert(1, '../')
from auth.authAltru import authAltru

#parameters: 
#description: test function for obtain tokens in altru
#return: result of the test
class TestAuthAltru(unittest.TestCase):
    #parameters: 
    #description: test function for obtain tokens in altru
    #return: result of the test
    def test_auth_altru_returns_valid_url(self):
        # Call the authAltru() function
        url = authAltru()

        # Verify that the URL is not empty and starts with "https://app.blackbaud.com"
        self.assertTrue(url.startswith("https://app.blackbaud.com"))
        self.assertNotEqual(url, "https://app.blackbaud.com")  # Ensure it's not the home URL

if __name__ == '__main__':
    # Run the tests
    unittest.main()
