import requests
import json

url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=QK9WnbZyRDkUbL0f9tKwBUR5wqIV9aBdL1ePA19P"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)
