import pandas as pd
import coverage
import unittest

# Ejecuta tus pruebas con coverage
cov = coverage.Coverage()
cov.start()

# Crea un cargador de pruebas y una suite de pruebas
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Añade las pruebas de cada archivo a la suite de pruebas
for test_file in ['testApp.py', 'testAuthAltru.py', 'testAuthSalesforce.py', 'testDataProcessor.py']:
    tests = loader.discover(start_dir='.', pattern=test_file)
    suite.addTests(tests)

# Ejecuta la suite de pruebas
runner = unittest.TextTestRunner()
runner.run(suite)

cov.stop()
cov.save()

# Obtiene los datos de cobertura
data = cov.get_data()
files = data.measured_files()

coverage_data = []
for file in files:
    _, executable_lines, _, executed_lines, _ = cov.analysis2(file)
    coverage_data.append([file, len(executable_lines), len(executed_lines)])

# Convierte los datos a un DataFrame de pandas
df = pd.DataFrame(coverage_data, columns=['File', 'Executable Lines', 'Executed Lines'])

# Guarda el DataFrame en un archivo CSV
df.to_csv('coverage_report.csv')
