import requests
import webbrowser

def authSalesforce():
    # Tus credenciales de Salesforce
    client_id = '3MVG9zeKbAVObYjPODek1PYnJW15VxHyhGPUOe1vzfHcg89tL_3Xyj_DCZQql_RL4Gjdnmk7EpfFk4DGDulnz'
    redirect_uri = 'http://localhost:8000/salesforce/callback'
    response_type = 'code'

    # URL de autenticación de Salesforce
    url = f"https://login.salesforce.com/services/oauth2/authorize?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}"

    headers = {}
    payload = {}

    # Realizar la solicitud de autenticación
    response = requests.request("GET", url, headers=headers, data=payload)

    return response.url
