import pandas as pd
import coverage
import unittest
import io
import re

# Run your tests with coverage
cov = coverage.Coverage()
cov.start()

# Create a test loader and a test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Add the tests from each file to the test suite
for test_file in ['testApp.py', 'testAuthAltru.py', 'testAuthSalesforce.py', 'testDataProcessor.py']:
    tests = loader.discover(start_dir='.', pattern=test_file)
    suite.addTests(tests)

# Run the test suite
runner = unittest.TextTestRunner()
runner.run(suite)

cov.stop()
cov.save()

# Create a text file in memory to capture the output of the report
file = io.StringIO()
cov.report(file=file)

# Get the output of the report as a string
report = file.getvalue()

# Parse the output of the report to get the coverage percentages
coverage_data = []
for line in report.split('\n'):
    match = re.search(r'(.*)\s+(\d+)\s+(\d+)\s+(\d+)%', line)
    if match:
        file, statements, missed, coverage = match.groups()
        coverage_data.append([file, int(statements), int(missed), int(coverage)])

# Convert the coverage data into a pandas DataFrame
df = pd.DataFrame(coverage_data, columns=['File', 'Statements', 'Missed', 'Coverage'])

# Add the "%" symbol at the end of each number in the coverage column
df['Coverage'] = df['Coverage'].apply(lambda x: f'{x}%')

# Save the DataFrame to a CSV file
df.to_csv('coverage_report.csv', index=False)
