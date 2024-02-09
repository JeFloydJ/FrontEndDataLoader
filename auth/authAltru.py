# Import necessary modules
import requests

#parameters: 
#description: this function, make a request for solicit the tokens in salesforce service
#return: url with token
def authAltru():

    # Define the client ID, client secret, redirect URI, and response type
    client_id = "14ff689a-1054-43ef-a3ec-e3137c3c4a3e"
    client_secret = "Y/YJK4+22KtLQt4CTkA3cwVtOXh7B+jpCUQolXYdLfo="
    redirect_uri = "http://localhost:8000/skyapi/callback"
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