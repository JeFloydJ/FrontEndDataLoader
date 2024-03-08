# Import necessary modules
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


#parameters: 
#description: this function, make a request for solicit the tokens in altru service
#return: url with token
def authSalesforce():

    # Your Salesforce credentials
    client_id = os.getenv("CLIENT_ID_SALESFORCE")
    redirect_uri = os.getenv("REDIRECT_URI_SALESFORCE")
    response_type = os.getenv("RESPONSE_TYPE_SALESFORCE")

    # Salesforce authentication URL
    url = f"https://test.salesforce.com/services/oauth2/authorize?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}"

    # Define the payload and headers (both are empty in this case)
    headers = {}
    payload = {}

    # Send the GET request and get the response
    response = requests.request("GET", url, headers=headers, data=payload)

   # Return the URL from the response
    return response.url