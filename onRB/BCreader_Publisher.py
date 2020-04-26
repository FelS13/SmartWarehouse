from BCreader import BC_Reader
import paho.mqtt.client as mqttc
import time
import datetime
#import requests
import json

class PublishData(object): 
    def __init__ (self, sensor_data , client):
        self.data = sensor_data
        self.client = client
    
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print('connected to broker')
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print ('BC_Reader_sensor: CONNACK received with code: ' + str(rc))
        print ("at time: " + str(current_time))
        return str(rc)

# When the message has been published to the Broker an 
# acknowledgement is sent that results in the on_publish callback being called.
    @classmethod # Create Function for Callback
    def on_publish(cls, client, userdata, mid):
        # cls is equal to self but for class methods 
        # get the current time
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        # mid = message ID
        print("mid: " + str(mid) + " has been published with success")
        print ("at time: " + str(current_time))
        print("---------------------------------------------------------------")
        return str(mid)

    def publish_sensor_data(self):
        #This function will publish the data related to sensor BC 
        while 4==4:    
            try:
                inputJsonFromBCSensor = self.data.senseBC()
                inputData = json.loads(inputJsonFromBCSensor)
                BC = inputData["BC"]
                time1 = inputData["time"]
                outputJson=json.dumps({"subject":"BARCODE_sensor_data", "BC": BC, "time":time1})
                client.publish("user/barcode", str(outputJson), qos=1)
    #            msg_info = client.publish("user/ID_fiscal_code", str(outputJson), qos=1)
    #            if msg_info.is_published() == True:
    #                print ("\n ID_Publisher : Message is published.")
                # This call will block until the message is published
                #msg_info.wait_for_publish()
                #return ("HELLO") # <-- andava dentro json_format
                print("MOVE THE CAMERA FROM THE BARCODE") 
                time.sleep(10)                
            except:
                #get_time = datetime.datetime.now()
                #current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
                #print("BC_Reader_sensor: ERROR IN PUBLISHING DATA RELATED TO THE SENSORS")
                #print ("at time: " + str(current_time))
                print("PLEASE SCAN A BARCODE") 
                time.sleep(5)



if __name__ == '__main__': 
    
    try:
        # create an object from ID_Reader class
        sensor_data = BC_Reader()
    except:
        print("BC_Reader_sensor: ERROR IN GETTING DATA FROM SENSOR ")
    
    try: 
        file = open("configFile.json", 'r')
        json_string = file.read()    
        file.close()
    except:
        raise KeyError("ID_Reader_Publisher: ERROR IN READING FILE ")
    

    data = json.loads(json_string)
    broker_address = data["resourceCatalog"]["broker_address"]
    port1 = data["resourceCatalog"]["port1"]
    port2 = data["resourceCatalog"]["port2"]

    "creo un client"
    client = mqttc.Client()

    bar = PublishData(sensor_data, client)


    try:
        "ti permette di attaccare le callback al client che in questo caso si comporta da publisher"
        " assegna delle funzioni alla callback "
        client.on_connect = PublishData.on_connect
        client.on_publish = PublishData.on_publish
        client.connect(broker_address, int(port1), int(port2))
        client.loop_start()
        
    except:
        print("BC_Reader_sensor: ERROR IN CONNECTING TO THE BROKER")

    bar.publish_sensor_data()
    time.sleep(10) # wait
    client.loop_stop() #stop the loop
