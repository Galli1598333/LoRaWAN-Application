import json
import random
import time
import base64
from paho.mqtt import client as mqtt_client
from pymongo import MongoClient
from lib.requests_api import RequestsApi

broker = ''
port = 1883

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
mqtt_auth = {
  "username": "",
  "password": ""
}

URL = "https://uniorchestra.uniot.eu"
HEADER = {"Content-type": "application/json", "Accept": "application/json"}
LOGIN = {
  "username": "",
  "password": ""
}


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.username_pw_set(mqtt_auth['username'], mqtt_auth['password'])
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, payload):
    msg = json.dumps(payload)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def subscribe(client: mqtt_client, devEui, collection):
    def on_message(client, userdata, msg):
        print(f"From topic `{msg.topic}` received `{msg.payload.decode()}`")
        publish(client, "lora/uplink/" + devEui + "/res", {"result": "ok"})
        payload = json.loads(msg.payload.decode())
        #controllare dove sta il payload
        #bytes_object = bytes.fromhex(payload['payload'])
        #ascii_string = bytes_object.decode("ASCII")
        #payload['payload'] = ascii_string

        base64_bytes = payload['payload'].encode('ascii')
        message_bytes = base64.b64decode(base64_bytes).hex()
        #message = message_bytes.decode('ascii')
        #message = hex2number(message_bytes)
        payload['parsed_payload'] = message_bytes
        print(payload)

        if isinstance(payload, list):
            collection.insert_many(payload)
        else:
            collection.insert_one(payload)
        """
        if payload["counter_up"] % 2 == 0:
            cursor = collection.find({})
            for document in cursor:
                print(document)
        """

    client.subscribe("lora/uplink/"+devEui+"/req")
    client.on_message = on_message

def hex2number(msg):
    # How many numbers to read
    N_TO_READ = 4
    # How many characters is a number. An int is 4 bytes so 8 chars
    CHAR_PER_INT = 8
    CHAR_PER_LONG = 16

    #msg = "17EA5A8700133BA8000109900000017667549F4D"

    # Expecting to read all ints and the last number as long
    if (N_TO_READ - 1) * CHAR_PER_INT + 1 * CHAR_PER_LONG != len(msg):
        raise Exception(f"Wrong message length {len(msg)} for {N_TO_READ} numbers to read")

    ints = []
    for n in range(N_TO_READ - 1):
        next_hex = msg[n * CHAR_PER_INT:(n + 1) * CHAR_PER_INT]
        ints.append(str(int(next_hex, base=16)))
    # Read last as long
    ints.append(str(int(msg[-CHAR_PER_LONG:], base=16)))

    latitude = ints[0]
    longitude = ints[1]
    altitude = ints[2]
    timestamp = ints[3]

    position = {
        'lat': float(latitude[:2] + '.' + latitude[2:]),
        'lon': float(longitude[:2] + '.' + longitude[2:]),
        'alt': float(altitude[:2] + '.' + altitude[2:]),
        'tx_time': float(timestamp[:10] + '.' + timestamp[10:]),
    }
    print(position)
    return position


def run():
    # database
    myclient = MongoClient(port=27017)
    db = myclient["GFG"]
    Collection = db["data-localization"]
    Collection.drop()
    cursor = Collection.find({})
    for document in cursor:
        print(document)
    client = connect_mqtt()

    uniOrchestra = RequestsApi(URL)
    r = uniOrchestra.post("/auth/local", data=LOGIN)
    token = r.json()['token']
    print(token)
    uniOrchestra = RequestsApi(URL, headers={"Authorization": "Bearer " + token})
    r = uniOrchestra.get("/api/devices", headers=HEADER)
    print(json.dumps(r.json(), indent=2))
    for device in r.json():
        devEui = device['devEui']
        subscribe(client, devEui, Collection)
    #publish(client, "/python/mqtt/req", {"request": "0"})
    client.loop_forever()


if __name__ == '__main__':
    run()
