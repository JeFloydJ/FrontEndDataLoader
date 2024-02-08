from flask import Flask, request, render_template, redirect
import logging 
import requests
import urllib.parse
from auth.authAltru import authAltru  
from auth.authSalesforce import authSalesforce

logging.basicConfig(level = logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    force=True)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

client_ids = {
    'salesforce': '3MVG9zeKbAVObYjPODek1PYnJW15VxHyhGPUOe1vzfHcg89tL_3Xyj_DCZQql_RL4Gjdnmk7EpfFk4DGDulnz',
    'altru': '14ff689a-1054-43ef-a3ec-e3137c3c4a3e'
}
client_secrets = {
    'salesforce': '6003041383007768349',
    'altru': 'Y/YJK4+22KtLQt4CTkA3cwVtOXh7B+jpCUQolXYdLfo='
}
redirect_uris = {
    'skyapi' : "http://localhost:8000/skyapi/callback",
    'salesforce' : "http://localhost:8000/salesforce/callback"
}

token_urls = {
    'salesforce': 'https://login.salesforce.com/services/oauth2/token',
    'altru': 'https://oauth2.sky.blackbaud.com/token'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/skyapi/callback')
def getAltruToken():
    service = 'altru'
    api = 'skyapi'
    query = urllib.parse.urlparse(request.url).query
    query_components = dict(qc.split("=") for qc in query.split("&") if "=" in qc)
    #logger.info(query)
    #logger.info(query_components)
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
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            refresh_token = token_response.json()["refresh_token"]
            try:
                with open(f'{service}_token.txt', 'w') as f:
                    f.write(access_token)
                with open(f'{service}_refresh_token.txt', 'w') as f:
                    f.write(refresh_token)
            except Exception as e:
                logger.error(f"Error al escribir en el archivo: {e}")
        else:
            logger.warning(f"Error en la respuesta del token: {token_response.content}")

    return redirect('/')

@app.route('/salesforce/callback')
def getSalesforceToken():
    service = 'salesforce'
    api = 'salesforce'
    #logger.info(query)
    #logger.info(query_components)
    query = urllib.parse.urlparse(request.url).query
    query_components = dict(qc.split("=") for qc in query.split("&") if "=" in qc)

    if "code" in query_components:
        code = query_components["code"]
        print(f"Código de autorización recibido: {code}")
        access_token = query_components["code"]
        access_token = access_token.replace("%3D%3D", "==")
        with open(f'{service}_token.txt', 'w') as f:
            f.write(access_token)
            # Solicitar un token de acceso
        token_url = "https://login.salesforce.com/services/oauth2/token"

        token_data = {
            "grant_type": "authorization_code",
            "code": access_token,
            "redirect_uri": redirect_uris[api],
            "client_id": client_ids[service],
            "client_secret": client_secrets[service]
        }
        token_url = "https://login.salesforce.com/services/oauth2/token"
        token_response = requests.post(token_url, data=token_data)
        logger.info(token_response)
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]
            refresh_token = token_response.json()["refresh_token"]
            try:
                with open(f'{service}_token.txt', 'w') as f:
                    f.write(access_token)
                with open(f'{service}_refresh_token.txt', 'w') as f:
                    f.write(refresh_token)
            except Exception as e:
                logger.error(f"Error al escribir en el archivo: {e}")
        else:
            logger.warning(f"Error en la respuesta del token: {token_response.content}")
    return redirect('/')

@app.route('/auth/<service>', methods=['GET'])
def auth(service):
    #logger.info(service)
    if service == 'altru':
        auth_url = authAltru()
    elif(service == 'salesforce'):
        auth_url = authSalesforce()

    return redirect(auth_url)


if __name__ == '__main__':
    app.run(debug=True, port=8000)

