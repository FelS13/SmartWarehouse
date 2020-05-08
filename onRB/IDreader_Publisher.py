# Sensor ID publisher which reads the data from the sensor and outputs a json message to the broker using the topic "user/ID_fiscal_code"

from IDreader import ID_Reader
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
        print ('ID_Reader_Publisher: CONNACK received with code: ' + str(rc))
        print ("at time: " + str(current_time))
        return str(rc)

# When the message has been published to the Broker an 
# acknowledgement is sent that results in the on_publish callback being called.
    @classmethod # Create Function for Callback
    def on_publish(cls, client, userdata, mid):
        # get the current time
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("mid: " + str(mid) + " has been published with success")
        print ("at time: " + str(current_time))
        print("----------------------------------------------------------------")
        return str(mid)

    def publish_sensor_data(self):
        #This function will publish the data related to sensor ID 
        while 15==15:    
            try:
                # read the data from the sensor
                inputJsonFromIDSensor = self.data.senseID()
                # obtain the json file
                inputData = json.loads(inputJsonFromIDSensor)
                ID = inputData["ID"]
                time1 = inputData["time"]
                #create a new json with the needed information 
                outputJson=json.dumps({"subject":"ID_sensor_data", "ID": ID, "time":time1})
                # puclish the new message
                client.publish("user/ID_fiscal_code", str(outputJson), qos=1)
                print("PLEASE WITHDRAW THE CARD") 
                time.sleep(30)
            except:
                # if there is no card in the sensor, simply ask to insert a new one
                print("PLEASE INSERT A CARD") 
                time.sleep(5)


if __name__ == '__main__': 
    
    try:
        # create an object from ID_Reader class
        sensor_data = ID_Reader()
    except:
        print("ID_Reader_Publisher: ERROR IN GETTING DATA FROM SENSOR ")
    
    try: 
        # get all information contained in the config file
        file = open("configFile.json", 'r')
        json_string = file.read()    
        file.close()
    except:
        raise KeyError("ID_Reader_Publisher: ERROR IN READING FILE ")
    

    data = json.loads(json_string)
    broker_address = data["resourceCatalog"]["broker_address"]
    port1 = data["resourceCatalog"]["port1"]
    port2 = data["resourceCatalog"]["port2"]
    "create a client"
    client = mqttc.Client()
    "sensor object, client"
    sens = PublishData(sensor_data, client)

    try:
        "attachment of callbacks to client"
        client.on_connect = PublishData.on_connect
        client.on_publish = PublishData.on_publish
        client.connect(broker_address, int(port1), int(port2))
        client.loop_start()
        
    except:
        print("ID_Reader_Publisher: ERROR IN CONNECTING TO THE BROKER")

    sens.publish_sensor_data()
    time.sleep(10)
    client.loop_stop() 
