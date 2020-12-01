import connexion

app = connexion.App(__name__)
app.add_api('swagger/tuya-gateway.yaml')
app.run(port=8080)
