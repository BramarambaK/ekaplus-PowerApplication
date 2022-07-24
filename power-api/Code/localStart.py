from api import controller

app = controller.startApp()
app.run(host='0.0.0.0', port=8080, debug=True)
