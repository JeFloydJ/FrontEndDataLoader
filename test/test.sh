#!/bin/bash

# Run the test for the application
python3 testApp.py

# Run the test for the Altru authentication
python3 testAuthAltru.py

# Run the test for the Salesforce authentication
python3 testAuthSalesforce.py

# Run the test for the data processor
python3 testDataProcessor.py
