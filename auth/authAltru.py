# Import necessary modules
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def authAltru():
    # Get the environment variables
    client_id = os.getenv("CLIENT_ID_SKY_API")
    client_secret = os.getenv("CLIENT_SECRET_SKY_API")
    redirect_uri = os.getenv("REDIRECT_URI_SKY_API")
    response_type = "code"
    
    # Construct the URL for the authorization request
    url = f"https://app.blackbaud.com/oauth/authorize?redirect_uri={redirect_uri}&client_secret={client_secret}&client_id={client_id}&response_type={response_type}"

    # Define the payload and headers (both are empty in this case)
    payload = {}
    headers = {}

    # Send the GET request and get the response
    response = requests.request("GET", url, headers=headers, data=payload)

    # Return the URL from the response
    return response.url
