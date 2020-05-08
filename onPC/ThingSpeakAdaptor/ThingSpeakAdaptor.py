

import paho.mqtt.client as mqtt
import json, time, datetime
import requests

file = open("configFile.json", "r")
jsonString = file.read()
file.close()
data = json.loads(jsonString)
url = data["resourceCatalog"]["url"]
channel = data["resourceCatalog"]["channel"]
write_key = data["resourceCatalog"]["write_key"]
broker_address = data["resourceCatalog"]["broker_address"]
port1 = data["resourceCatalog"]["port1"]
port2 = data["resourceCatalog"]["port2"]
name = data["resourceCatalog"]["name"]


class ThingSpeakConnector():

    
    def __init__(self):
        
        global name
        global channel
        global url
        global write_key
        global broker_address
        
        
        self.warehouse = name
        self.channel = channel
        self.write_key = write_key
        self.ID = self.warehouse+"_TS-Adaptor"
        self.type = "TS-Adaptor"

        self.broker_address = broker_address

        self.client_obj = mqtt.Client(self.ID)

        self.isSubscriber = True
        self.isPublisher = False

        self.field1_data = None #users
        self.field2_data = None #materials

        self.client_obj.on_connect = self.connect_callback
        self.client_obj.on_message = self.message_callback
      


    # device starting
    def start(self):
        
        global port1
        global port2
        
        self.client_obj.connect(self.broker_address, int(port1), int(port2))
        self.client_obj.loop_start()

        self.client_obj.subscribe("user/ID_fiscal_code", qos=1) #subscribe to know when a user is entering
        self.client_obj.subscribe("user/barcode", qos=1) #subscribe to know when an item is taken
        self.client_obj.subscribe("user/exit", qos=1) #subscribe to know when a user is exiting
        
    # device stopping
    def stop(self):        
        self.client_obj.unsubscribe("user/ID_fiscal_code")
        self.client_obj.unsubscribe("user/barcode")
        self.client_obj.unsubscribe("user/exit")
        self.client_obj.disconnect()
        

    # callback for connection
    def connect_callback(self,client,userdata,flags,rc):
        if rc == 0:
            print("%s connected to broker %s." % (self.ID,self.broker_address))
            rc = 1

    # callback for messages
    def message_callback(self, client, userdata, message):
         if (message.topic == "user/ID_fiscal_code"):
            
            self.field1_data =  json.loads("1") #if the user enter send 1 to Field1 --> relative to users
            
         if (message.topic == "user/barcode"):
            
            self.field2_data =  json.loads("1")  #if an object is scanned send "1" to Field2 --> relative to objects
           
         elif (message.topic == "user/exit"): #if an user exit set both fields to "0"
            
            self.field1_data = json.loads("0")   
            self.field2_data = json.loads("0")


    



# main function

headers = {'Content-type': 'application/json', 'Accept': 'raw'}
cnt = 1

tsa = ThingSpeakConnector()
tsa.start()

t=0
while t<80:

    data_upload_json = json.dumps({"api_key": tsa.write_key,
    "channel_id": tsa.channel, 
    "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "entry_id": cnt,
    "field1": tsa.field1_data,
    "field2": tsa.field2_data
    })

    if(tsa.field1_data != None or tsa.field2_data != None):
        print("Publishing on TS:", data_upload_json)
        requests.post(url=url, data=data_upload_json, headers=headers)

    tsa.field1_data = None #users
    tsa.field2_data = None #items
    

    time.sleep(30) #check for updates every 30sec
    cnt += 1 #update the entry id
    t+=1

tsa.stop()
