import requests
import pprint

response = requests.get('https://perenual.com/api/species-list?key=sk-L9aC64b73122e37dc1596&q=rose')
result = response.json()
newRes = result['data']
index = 0
output = ''

while index < len(newRes):
    id = newRes[index]['id']
    #print(id)
    idStr = str(id)
    output += idStr + '\n'
    #print(newRes[index]['common_name'])
    output += newRes[index]['common_name']
    output += '\n'
    #print(newRes[index]['scientific_name'])
    output += str(newRes[index]['scientific_name'])
    output += '\n'
    picture = newRes[index]['default_image']
    if picture == None:
        #print("no_url")
        output += 'no url' + '\n'
    else:
        #print(picture['original_url'])
        output += picture['original_url']
        output += '\n'
    #print()
    output += '\n'
    index += 1
    
print(output)