# Sensor BC publisher which reads the data from the sensor and outputs a json message to the broker using the topic "user/barcode"


from BCreader import BC_Reader
import paho.mqtt.client as mqttc
import time
import datetime
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
                # get data from the sensor in a json
                inputJsonFromBCSensor = self.data.senseBC()
                inputData = json.loads(inputJsonFromBCSensor)
                # manipulate the json
                BC = inputData["BC"]
                time1 = inputData["time"]
                # get all information required for the exchange
                outputJson=json.dumps({"subject":"BARCODE_sensor_data", "BC": BC, "time":time1})
                # publish the message 
                client.publish("user/barcode", str(outputJson), qos=1)
                print("MOVE THE CAMERA FROM THE BARCODE") 
                time.sleep(10)                
            except:
                print("PLEASE SCAN A BARCODE") 
                time.sleep(5)



if __name__ == '__main__': 
    
    try:
        # create an object from BC_Reader class
        sensor_data = BC_Reader()
    except:
        print("BC_Reader_sensor: ERROR IN GETTING DATA FROM SENSOR ")
    
    try: 
        # get all information of the config file
        file = open("configFile.json", 'r')
        json_string = file.read()    
        file.close()
    except:
        raise KeyError("ID_Reader_Publisher: ERROR IN READING FILE ")
    

    # get the json of the file information 
    data = json.loads(json_string)
    broker_address = data["resourceCatalog"]["broker_address"]
    port1 = data["resourceCatalog"]["port1"]
    port2 = data["resourceCatalog"]["port2"]

    "create a client"
    client = mqttc.Client()
    # create a publish object
    bar = PublishData(sensor_data, client)


    try:
        "attachment of callbacks to client "
        client.on_connect = PublishData.on_connect
        client.on_publish = PublishData.on_publish
        client.connect(broker_address, int(port1), int(port2))
        client.loop_start()
        
    except:
        print("BC_Reader_sensor: ERROR IN CONNECTING TO THE BROKER")

    bar.publish_sensor_data()
    time.sleep(10) # wait
    client.loop_stop() #stop the loop
