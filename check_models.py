import requests
API_KEY = "AIzaSyCUz79l1tisuJxAF-dSRYuaERXHJMCWIVE"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
response = requests.get(url)
print(response.json())