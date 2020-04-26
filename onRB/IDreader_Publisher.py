from IDreader import ID_Reader
import paho.mqtt.client as mqttc
import time
import datetime
#import requests
import json

class PublishData(object): 
    def __init__ (self, sensor_data , client):
        self.data = sensor_data
        self.client = client

#    def load_topics(self):
#        # sending request to the resource catalog to get the topics related to the room id
#        try: 
#            "occorre connettersi al broker"
#            self.respond = requests.get(self.url)
#            json_format = json.loads(self.respond.text)
#            self.DHT_Topic = json_format["topic"]["dhtTopic"]
#            print("Temp_Humidity_Publisher: BROKER VARIABLES ARE READY")
#        except:
#            print("ID_Reader_Publisher: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER TOPICS")
    
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print('connected to broker')
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print ('ID_Reader_Publisher: CONNACK received with code: ' + str(rc))
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
        print("----------------------------------------------------------------")
        return str(mid)

    def publish_sensor_data(self):
        #This function will publish the data related to sensor ID 
        while 15==15:    
            try:
                inputJsonFromIDSensor = self.data.senseID()
                inputData = json.loads(inputJsonFromIDSensor)
                ID = inputData["ID"]
                time1 = inputData["time"]
                outputJson=json.dumps({"subject":"ID_sensor_data", "ID": ID, "time":time1})
                client.publish("user/ID_fiscal_code", str(outputJson), qos=1)
    #            msg_info = client.publish("user/ID_fiscal_code", str(outputJson), qos=1)
    #            if msg_info.is_published() == True:
    #                print ("\n ID_Publisher : Message is published.")
                # This call will block until the message is published
                #msg_info.wait_for_publish()
                print("PLEASE WITHDRAW THE CARD") 
                time.sleep(30)
                #return ("HELLO") # <-- andava dentro json_format
            except:
                #get_time = datetime.datetime.now()
                #current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
                #print("IDReader_Publisher: ERROR IN PUBLISHING DATA RELATED TO THE SENSORS")
                #print ("at time: " + str(current_time))
                print("PLEASE INSERT A CARD") 
                time.sleep(5)


if __name__ == '__main__': 
    
    try:
        # create an object from ID_Reader class
        sensor_data = ID_Reader()
    except:
        print("ID_Reader_Publisher: ERROR IN GETTING DATA FROM SENSOR ")
    
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
    "url database , dati generati dal sensore , ID nel database , client appena creato"
    sens = PublishData(sensor_data, client)
#    sens.load_topics()
    
#    try:
#        #requesting the broker info from resource catalog
#        respond = requests.get(resourceCatalogIP+"broker")
#        json_format = json.loads(respond.text)
#        broker_ip = json_format["ip"]
#        port = json_format["port"]
#    except:
#        print("ID_Reader_Publisher: ERROR IN CONNECTING TO THE SERVER FOR READING BROKER IP")

    try:
        "ti permette di attaccare le callback al client che in questo caso si comporta da publisher"
        " assegna delle funzioni alla callback "
        client.on_connect = PublishData.on_connect
        client.on_publish = PublishData.on_publish
        client.connect(broker_address, int(port1), int(port2))
        client.loop_start()
        
    except:
        print("ID_Reader_Publisher: ERROR IN CONNECTING TO THE BROKER")

    sens.publish_sensor_data()
    time.sleep(10) # wait
    client.loop_stop() #stop the loop
