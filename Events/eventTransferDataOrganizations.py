import logging
from Events import eventProcessData
from Events import eventDataTransfer
import os
from dotenv import load_dotenv

# Set up logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
#                     force=True)

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                     force=True, 
                     filename='out.txt.log',
                     filemode='w')


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

# hash table like: {'Auctifera__Implementation_External_ID__c': 'AccountId'} for sent address information
dic_accounts = {}
#hashtable like {'1-households-code' : 'code'}
dic_households_ids = {}

#parameters: 
#description: adapter between sky an salesforce for sent data
#return: get data and sent data
class Adapter:

    #parameters: report_names
    #description: Initializes the DataProcessor and report names
    #return: 
    def __init__(self, report_names):
        csv_dir = os.path.join(ABS_PATH.format('data')) 
        base_path = csv_dir
        self.data_processor = eventProcessData.DataProcessor(base_path)
        self.report_names = report_names
        self.dic_households_ids = {}
        self.dic_accounts = {}

    #parameters: 
    #description: Processes data using the DataProcessor and sends address of contacts information to Salesforce
    #return: sent data
    def process_data(self):
        self.data_processor.process_data()
        for report_name in self.report_names:
            processor = eventDataTransfer.SalesforceProcessor(report_name)  
            processor.process_organizations()
            processor.process_households()
            self.dic_households_ids = {**self.dic_households_ids, **processor.process_households_ids()}
            processor.households_ids = self.dic_households_ids
            dic = processor.process_contacts()
            self.dic_accounts = {**self.dic_accounts, **dic}
            processor.process_contact_address()



