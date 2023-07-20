import requests
import pprint

response = requests.get('https://perenual.com/api/species-list?key=sk-L9aC64b73122e37dc1596&q=daisy')
result = response.json()
newRes = result['data']

id = newRes[0]['id']
idStr = str(id)
response = requests.get('https://perenual.com/api/species/details/'+idStr+'?key=sk-L9aC64b73122e37dc1596')
result = response.json()

print(result['description'])
    