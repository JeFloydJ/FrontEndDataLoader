# Import necessary modules
from flask import Flask, request, render_template, redirect
import logging
import requests
import urllib.parse
from dotenv import load_dotenv
from auth.authAltru import authAltru
from auth.authSalesforce import authSalesforce
from Events.eventTransferDataOrganizations import Adapter
import subprocess
import os

# Load environment variables
load_dotenv()

#absolute path of files
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "App", "{}")

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    force=True)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Define client IDs
client_ids = {
    'salesforce': os.getenv("CLIENT_ID_SALESFORCE"),
    'altru': os.getenv("CLIENT_ID_SKY_API")
}

# Define client secrets
client_secrets = {
    'salesforce': os.getenv("CLIENT_SECRET_SALESFORCE"),
    'altru': os.getenv("CLIENT_SECRET_SKY_API")
}

# Define redirect URIs
redirect_uris = {
    'skyapi': os.getenv("REDIRECT_URI_SKY_API"),
    'salesforce': os.getenv("REDIRECT_URI_SALESFORCE")
}

# Define token URLs
token_urls = {
    'salesforce': 'https://login.salesforce.com/services/oauth2/token',
    'altru': 'https://oauth2.sky.blackbaud.com/token'
}

# List of files with tokens
token_files = ['altru_token.txt', 'altru_refresh_token.txt', 'salesforce_token.txt', 'salesforce_refresh_token.txt', 'salesforce_instance.txt']

#List of reports and csv files
special_files = ['Veevart Organization Addresses Report test_output.csv', 'Veevart Organization Addresses Report test_response.json', 'Veevart Organization Phones Report test_output.csv', 'Veevart Organization Phones Report test_response.json', 'Veevart Organizations Report test_output.csv', 'Veevart Organizations Report test_response.json', 'Veevart HouseHolds Report test_response.json', 'Veevart HouseHolds Report test_output.csv', 'Veevart Contacts Report test_response.json', 'Veevart Contacts Report test_output.csv', 'Veevart Contacts Report Phones test_response.json', 'Veevart Contacts Report Phones test_output.csv', 'Veevart Contacts Report Email test_response.json', 'Veevart Contacts Report Email test_output.csv', 'Veevart Contacts Report Address test_response.json', 'Veevart Contacts Report Address test_output.csv']

# delete the content in each token file 
for filename in token_files:
    open(filename, 'w').close()

#delete content in each csv and json file
for filename in special_files:
    open((ABS_PATH.format(f'Events/{filename}')), 'w').close()

#parameters: file of text
#description: verify if the file is empty
#return: if the file is empty or not.
def isEmpty(file):
    return not bool(file.read())

@app.route('/Validator')
def validateToken():
    statusValidator = 404
    try:
        with open('finish.txt', 'r') as f:
            statusValidator = 200
    finally:
        return {'status': statusValidator}


#parameters: 
#description: the main page of this project, decided wich page render depends of the auths
#return: render the page
@app.route('/')
def index():
    #variables for know in wich service is auth
    loggedSkyApi = False
    loggedSalesforce = False
    transferData = False
    
    #if is logged in salesforce, the variable its True 
    with open('salesforce_token.txt', 'r') as f:
        if(not(isEmpty(f))):
            loggedSalesforce = True 

    #if is logged in Sky Api, the variable its True
    with open('altru_token.txt', 'r') as f:
        if(not(isEmpty(f))):
            loggedSkyApi = True
    
    for filename in special_files:
        with open((ABS_PATH.format(f'Events/{filename}')), 'r') as f:
            if(not(isEmpty(f))):
                transferData = True
 
    # Render the index page
    return render_template('index.html', loggedSkyApi = loggedSkyApi, loggedSalesforce = loggedSalesforce, transferData = transferData)


#parameters: 
#description: get data in sky api, after transfer to salesforce
#return: render the page of the complete data
@app.route('/transferData', methods=['GET'])
def transferData():
    # os.spawnl(os.P_NOWAIT, 'python3 transferProcess.py')
    subprocess.Popen(['python3', 'transferProcess.py', '&'])
    #render main page
    return {'status': 200}

#parameters: 
#description: obtain access tokens when authorizing in altru
#return: render the page
@app.route('/skyapi/callback')
def getSkyApiToken():
    # Define the service and API
    service = 'altru'
    api = 'skyapi'
    # Parse the URL query
    query = urllib.parse.urlparse(request.url).query
    query_components = dict(qc.split("=") for qc in query.split("&") if "=" in qc)

    # If the query contains a code, get the token
    if "code" in query_components:
        code = query_components["code"]
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uris[api],
            "client_id": client_ids[service],
            "client_secret": client_secrets[service]
        }
        token_url = "https://oauth2.sky.blackbaud.com/token"
        token_response = requests.post(token_url, data=token_data)

        # If the token response is successful, write the tokens to files
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            refresh_token = token_response.json()["refresh_token"]
            try:
                with open(f'{service}_token.txt', 'w') as f:
                    f.write(access_token)
                with open(f'{service}_refresh_token.txt', 'w') as f:
                    f.write(refresh_token)
            except Exception as e:
                logger.error(f"Error writing to file: {e}")
        else:
            logger.warning(f"Token response error: {token_response.content}")
    
    # Return the answer
    return redirect('/')

#parameters: 
#description: obtain access tokens when authorizing in salesforce
#return: render the page
@app.route('/salesforce/callback')
def getSalesforceToken():
    # Define the service and API
    service = 'salesforce'
    api = 'salesforce'
    # Parse the URL query
    query = urllib.parse.urlparse(request.url).query
    query_components = dict(qc.split("=") for qc in query.split("&") if "=" in qc)

    # If the query contains a code, get the token
    if "code" in query_components:
        code = query_components["code"]
        access_token = query_components["code"]
        access_token = access_token.replace("%3D%3D", "==")

        # Write the access token to a file
        with open(f'{service}_token.txt', 'w') as f:
            f.write(access_token)

        # Request an access token
        token_url = "https://test.salesforce.com/services/oauth2/token"
        token_data = {
            "grant_type": "authorization_code",
            "code": access_token,
            "redirect_uri": redirect_uris[api],
            "client_id": client_ids[service],
            "client_secret": client_secrets[service]
        }
        token_response = requests.post(token_url, data=token_data)
        #logger.info(token_response)

        # If the token response is successful, write the tokens to files
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            refresh_token = token_response.json()["refresh_token"]
            instance = token_response.json()["instance_url"]
            logger.info(instance)
            try:
                with open(f'{service}_token.txt', 'w') as f:
                    f.write(access_token)
                with open(f'{service}_refresh_token.txt', 'w') as f:
                    f.write(refresh_token)
                with open(f'{service}_instance.txt', 'w') as f:
                    f.write(instance)
            except Exception as e:
                logger.error(f"Error writing to file: {e}")
        else:
            logger.warning(f"Token response error: {token_response.content}")
    
    #logger.info(ans)

    # Return the answer
    return redirect('/')

#parameters: service (others CRM)
#description: obtain method for service
#return: render the page oh service
@app.route('/auth/<service>', methods=['GET'])
def auth(service):
    # Determine the service and get the authorization URL
    if service == 'altru':
        auth_url = authAltru()
    elif service == 'salesforce':
        auth_url = authSalesforce()

    # Redirect to the authorization URL
    return redirect(auth_url)


#run the server in port 8000
if __name__ == '__main__':
    # Run the app
    app.run(debug=True, port=8000)
