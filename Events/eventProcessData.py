import requests
import ssl
import json
import re
from simple_salesforce import Salesforce
import boto3
import csv
import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

class DataProcessor:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.bucket_name = bucket_name

    def read_s3_object(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        data = csv.reader(StringIO(csv_string))
        return data

    def modify_csv_names(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)
        email_index = headers.index("Email Addresses\\Email address")
        web_address_index = headers.index("Web address")
        name_index = headers.index('"Name"')
        last_name_index = headers.index("Last/Organization/Group/Household name")

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

        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)

        csv_output_string = f.getvalue()

        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_address(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)
        name_index = headers.index('"Name"')
        last_name_index = headers.index("Last/Organization/Group/Household name")
        address_index = headers.index('Addresses\\Address')
        zip_index = headers.index('Addresses\\ZIP')

        for row in data:

            if row[name_index]:
                row[name_index] = row[name_index][:5]

            if row[last_name_index]:
                first_word = row[last_name_index].split()[0]
                row[last_name_index] = 'x' + first_word + 'x'

            if row[address_index]:
                row[address_index] = row[address_index].split()[0]

            if row[zip_index]:
                row[zip_index] = row[zip_index][:2]
                
        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)

        csv_output_string = f.getvalue()

        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_phones(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)

        name_index = headers.index('"Name"')
        last_name_index = headers.index("Last/Organization/Group/Household name")
        phone_index = headers.index('Phones\\Number')

        for row in data:
            if row[name_index]:
                row[name_index] = row[name_index][:5]

            if row[last_name_index]:
                first_word = row[last_name_index].split()[0]
                row[last_name_index] = 'x' + first_word + 'x'

            if row[phone_index]:
                row[phone_index] = row[phone_index][:5]
        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)

        csv_output_string = f.getvalue()

        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_households(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)
        name_index = headers.index('"Name"')

        for row in data:
            if row[name_index]:
                row[name_index] = row[name_index][:5]
        
        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)
        csv_output_string = f.getvalue()
        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_contacs(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)
        name_index = headers.index('"Name"')
        last_name_index = headers.index('Last/Organization/Group/Household name')

        for row in data:
            if row[name_index]:
                row[name_index] = row[name_index][:5]
            if row[last_name_index]:
                first_word = row[last_name_index].split()[0]
                row[last_name_index] = 'x' + first_word + 'x'
        
        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)
        csv_output_string = f.getvalue()
        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_phones(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)
        name_index = headers.index('"Name"')
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
        
        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)
        csv_output_string = f.getvalue()
        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_contacs_email(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)

        name_index = headers.index('"Name"')
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
        
        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)
        csv_output_string = f.getvalue()
        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)

    def modify_csv_contacs_address(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        f = StringIO(csv_string)
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        headers[0] = headers[0].replace('\ufeff', '')  
        data = list(reader)
        name_index = headers.index('"Name"')
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

        f = StringIO()
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)
        csv_output_string = f.getvalue()
        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=csv_output_string)
                
    def display_csv(self, object_key):
        csv_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('max_colwidth', None)
        data = pd.read_csv(StringIO(csv_string), delimiter=';')
        print(data)
    def process_data(self):
        self.modify_csv_names('Veevart Organizations Report test.csv')
        self.modify_csv_address('Veevart Organization Addresses Report test.csv')
        self.modify_csv_phones('Veevart Organization Phones Report test.csv')
        self.modify_csv_households('Veevart HouseHolds Report test.csv')
        self.modify_csv_contacs('Veevart Contacts Report test.csv')
        self.modify_csv_phones('Veevart Contacts Report Phones test.csv')
        self.modify_csv_contacs_email('Veevart Contacts Report Email test.csv')
        self.modify_csv_contacs_email('Veevart Contacts Report Email test.csv')
        self.modify_csv_contacs_address('Veevart Contacts Report Address test.csv')
        #self.display_csv('Veevart Contacts Report Address test.csv')

        
# processor = DataProcessor(os.getenv('BUCKET_NAME'))
# processor.process_data()
# processor.modify_csv_names('Veevart Organizations Report test.csv')
# processor.modify_csv_address('Veevart Organization Addresses Report test.csv')
# processor.modify_csv_phones('Veevart Organization Phones Report test.csv')
# processor.modify_csv_households('Veevart HouseHolds Report test.csv')
# processor.modify_csv_contacs('Veevart Contacts Report test.csv')
# processor.modify_csv_phones('Veevart Contacts Report Phones test.csv')
# processor.modify_csv_contacs_email('Veevart Contacts Report Email test.csv')
# processor.modify_csv_contacs_email('Veevart Contacts Report Email test.csv')
# processor.modify_csv_contacs_address('Veevart Contacts Report Address test.csv')
# processor.display_csv('Veevart Contacts Report Address test.csv')