import connexion
from os import environ as env

# Initial authentication

app = connexion.App(__name__)
app.add_api('swagger/tuya-gateway.yaml')
app.run(port=8080)
