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
# Asumiendo que tienes la información para algunas de las nuevas columnas en las siguientes variables
source = "Migration Tool"
external_id = ""  # Aquí debes poner tu ID externo
repository = "a2oVs0000002KfNIAU"
product = "Migration Tool"

# Parse the output of the report to get the coverage percentages
coverage_data = [] 
for line in report.split('\n'):
    match = re.search(r'(.*)\s+(\d+)\s+(\d+)\s+(\d+)%', line)
    if match:
        file, statements, missed, coverage = match.groups()
        # Aquí es donde extraemos la parte específica del string
        start_index = file.find('FrontendDataLoader')
        if start_index != -1:
            path_name = file[start_index:]
        else:
            path_name = file
        coverage_data.append([source, external_id, repository, path_name, int(statements), int(missed), int(statements) + int(missed), f'{int(coverage)}%', product])

# Convert the coverage data into a pandas DataFrame
df = pd.DataFrame(coverage_data, columns=['Source', 'External Id', 'Repository', 'Path Name', 'Cover Lines', 'Uncover Code Lines', 'Lines', 'Coverage Status', 'Product'])

# Y luego guardas el DataFrame en un archivo CSV de la misma manera que antes
df.to_csv('coverage_report.csv', index=False)

# Save the DataFrame to a CSV file
df.to_csv('coverage_report.csv', index=False)
