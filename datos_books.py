import requests
import json

# Datos que quieres enviar
data = {
    "title": "Sebasbook",
    "author": "book"
}

# URL de la API a la que quieres enviar los datos
url = "http://localhost:5001/books"

# Convertir el diccionario a JSON
json_data = json.dumps(data)

# Configurar la cabecera para indicar que se envía JSON
headers = {'Content-Type': 'application/json'}

# Enviar la solicitud POST con los datos y la cabecera
response = requests.post(url, data=json_data, headers=headers)

# Verificar el código de estado de la respuesta
if response.status_code == 201:
    print("Datos enviados correctamente")
else:
    print("Error al enviar datos:", response.status_code, response.text)
