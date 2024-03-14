## MigrationTool

## Dependencias del proyecto

para descargar todas las dependencias necesarias sobre la carpeta `MIGRATIONTOOL` debe correr el siguiente comando:

```bash
chmod +x app.sh
./app.sh
```

Para correr este proyecto asegurese de estar en la carpeta `App` del proyecto.
para correr el proyecto ejecute en la terminal:

```bash
python3 app.py
```

esta correra en http://127.0.0.1:8000/.

hasta el momento solo tiene:
- página principal: funcional con autorización en salesforce y autorización en altru y sus test unitarios.

- página de transferencia de data: esta pagina permite transferir Accounts, estos accounts pueden tener varios telefonos y varias direcciones. Los telefonos se guardan en un objeto llamado Legacy Data. Los test unitarios de la pagina de obtener la informacion de SKY API, la clase se llama DataProcessor.

- página de data completa: Todo esto es solo visual.

Para correr test unitarios, sobre la carpeta `test` ejecutas el siguiente comando:

```bash
chmod +x test.sh
./test.sh
```


