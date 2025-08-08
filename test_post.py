import requests

url = "http://localhost:5000/generate-swagger"
data = {
    "url": "https://developer.adobe.com/commerce/webapi/rest/"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print("Código de respuesta:", response.status_code)
print("Contenido YAML:")
print(response.text)
