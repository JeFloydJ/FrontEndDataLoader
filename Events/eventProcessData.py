
import csv
import os
from dotenv import load_dotenv

#paths
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")
csv_dir = os.path.join(ABS_PATH.format('data'))


#parameters: 
#description: get data in sky api, 
#return: clean data with others personal information in csv files
class DataProcessor:
    #parameters: 
    #description: necessary path
    #return: response to request
    def __init__(self, base_path):
        self.base_path = base_path

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_households(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_names(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            email_index = headers.index('Email Addresses\\Email address')
            web_address_index = headers.index('Web address')
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

                if row[web_address_index]:
                    protocol, rest = row[web_address_index].split('//')
                    domain, path = rest.split('.com', 1)
                    row[web_address_index] = protocol + '//website.com' + path

                if '@' in row[email_index]:
                    local, domain = row[email_index].split('@')
                    row[email_index] = local + '@tmail.comx'
            
            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_address(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            address_index = headers.index('Addresses\\Address')
            zip_index = headers.index('Addresses\\ZIP')

            for row in data:
                if row[address_index]:
                    row[address_index] = row[address_index].split()[0]

                if row[zip_index]:
                    row[zip_index] = row[zip_index][:2]

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_phone(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig' ) as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            phone_index = headers.index('Phones\\Number')

            for row in data:
                if row[phone_index]:
                    row[phone_index] = row[phone_index][:5]

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_contacs_address(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')
            
            address_index = headers.index('Addresses\\Address')
            zip_index = headers.index('Addresses\\ZIP')

            for row in data:
                if row[address_index]:
                    row[address_index] = row[address_index].split()[0]

                if row[zip_index]:
                    row[zip_index] = row[zip_index][:2]

                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_contacs_email(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')                
            email_index = headers.index('Email Addresses\\Email address')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

                if '@' in row[email_index]:
                    local, domain = row[email_index].split('@')
                    row[email_index] = local + '@tmail.comx'

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_contacs(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name') 

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)

    #parameters: input csv for change information, csv with changed information
    #description: change personal information in csv file
    #return: csv file with changed information
    def modify_csv_phones(self, input_csv, output_csv):
        with open(input_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            data = list(reader)
            name_index = headers.index('Name')
            last_name_index = headers.index('Last/Organization/Group/Household name')
            phone_index = headers.index('Phones\\Number')

            for row in data:
                if row[name_index]:
                    row[name_index] = row[name_index][:5]

                if row[last_name_index]:
                    first_word = row[last_name_index].split()[0]
                    row[last_name_index] = 'x' + first_word + 'x'

                if row[phone_index]:
                    row[phone_index] = row[phone_index][:5]

            with open(output_csv, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(data)    
    #parameters:
    #description: generate csv file of the reports in sky api with changed information
    #return: csv file with changed information of all reports
    def process_data(self):
        report_names = [
            "Veevart Contacts Report Address test.csv",
            "Veevart HouseHolds Report test.csv",
            "Veevart Contacts Report Email test.csv",
            "Veevart Organization Addresses Report test.csv",
            "Veevart Contacts Report Phones test.csv",
            "Veevart Organization Phones Report test.csv",
            "Veevart Contacts Report test.csv",
            "Veevart Organizations Report test.csv"
        ]
        for report_name in report_names:
            file_path = self.base_path  
            if report_name == "Veevart Organizations Report test.csv":
                self.modify_csv_names(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart Organization Phones Report test.csv":
                self.modify_csv_phone(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart HouseHolds Report test.csv":
                self.modify_csv_households(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart Contacts Report Email test.csv":
                self.modify_csv_contacs_email(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart Contacts Report test.csv":
                self.modify_csv_contacs(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart Contacts Report Phones test.csv":
                self.modify_csv_phones(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart Contacts Report Address test.csv":
                 self.modify_csv_contacs_address(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))
            elif report_name == "Veevart Organization Addresses Report test.csv":
                self.modify_csv_address(os.path.join(file_path, report_name), os.path.join(self.base_path, report_name))


# # # Ejemplo de uso
# base_path = csv_dir
# processor = DataProcessor(base_path)
# processor.process_data()