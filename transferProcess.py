import time
import os
from Events.eventTransferDataOrganizations import Adapter

if(os.path.exists('finish.txt')):
    os.remove('finish.txt')
    
#list of reports name with data necessary
report_names = ["Veevart Organizations Report test","Veevart Organization Addresses Report test", "Veevart Organization Phones Report test", "Veevart HouseHolds Report test", "Veevart Contacts Report test", "Veevart Contacts Report Address test", "Veevart Contacts Report Email test", "Veevart Contacts Report Email test", "Veevart Contacts Report Phones test"]
    
#class adapter between get in sky api and post salesforce
adapter = Adapter(report_names)

#method to get and post data
adapter.process_data()


with open('finish.txt', 'w') as f:
    f.write('finish')
