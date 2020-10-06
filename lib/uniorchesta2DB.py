from lib.requests_api import RequestsApi
import json
from pymongo import MongoClient

URL = "https://uniorchestra.uniot.eu"
HEADER={"Accept": "application/json"}
LOGIN = {
  "username":"********",
  "password":"********"
}
"""
# database
myclient = MongoClient("mongodb://localhost:27017/")
db = myclient["GFG"]
Collection = db["data"]
"""

uniOrchestra = RequestsApi(URL)
r = uniOrchestra.post("/auth/local", data=LOGIN)
token = r.json()['token']
print(token)
uniOrchestra = RequestsApi(URL,  headers={"Authorization": "Bearer " + token})
r = uniOrchestra.get("/api/devices", headers=HEADER)
print(json.dumps(r.json(), indent=2))
for device in r.json():
  devEui = device['devEui']
  id = device['_id']
  print(devEui)
  print(id)
  r = uniOrchestra.get("/api/devices/packets/"+id, headers=HEADER)
  print(r.text)

"""
if isinstance(file_data, list): 
    Collection.insert_many(file_data)   
else: 
    Collection.insert_one(file_data) 
"""