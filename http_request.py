import requests

url = "http://localhost:3000"

response = requests.get(url)
print(response.text)
