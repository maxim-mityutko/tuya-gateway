import connexion

app = connexion.AioHttpApp(__name__)
app.add_api("swagger/tuya-gateway.yaml", base_path="/api/v1")
app.run(port=65080)
