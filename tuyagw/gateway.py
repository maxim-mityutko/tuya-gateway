import connexion

app = connexion.App(__name__)
app.add_api('tuya-gw.yaml')
app.run(port=8080)
