import requests as req
import json, datetime
import paho.mqtt.client as mqttc


file = open("configFile.json", 'r')
json_string = file.read()
file.close()
data = json.loads(json_string)
url = data['resourceCatalog']["url"]
port = data['resourceCatalog']["port"]
broker_ip = data['resourceCatalog']["broker_address"]
port1 = data['resourceCatalog']["port1"]
port2 = data['resourceCatalog']["port2"]

class RealTime(object):
        
    def __init__(self):
        pass

            
    def handler(self, command,fiscal_code):
        if command =='c':
            self.UserOUT(fiscal_code)
        if command =='r':
            self.UserIN(fiscal_code)

    def UserOUT(self,fiscal_code):
        
        global url
        global port
        r_user=req.get('http://'+url+':'+port+'/user/{}'.format(fiscal_code))
        if r_user.status_code == 404:
            print('\nACCESS DENIED\n')
        else:
            user=r_user.json()
            p_user=req.post('http://'+url+':'+port+'/user', data=json.dumps(user))
            if p_user.status_code == 404:
                print('\nUSER ALREADY SIGNED\n')
            else:
                print('\nSCAN THE BARCODE\n')
                global In_Out 
                In_Out = 0
                

    def UserIN(self,fiscal_code):
        
        global url
        global port
        r_user=req.get('http://'+url+':'+port+'/user/{}'.format(fiscal_code))
        if r_user.status_code == 404:
            print('\nACCESS DENIED\n')
        else:
            user=r_user.json()
            p_user=req.post('http://'+url+':'+port+'/user', data=json.dumps(user))
            if p_user.status_code == 404:
                print('\nUSER ALREADY SIGNED\n')
            else:
                print('\nSCAN THE BARCODE\n')
                global In_Out 
                In_Out = 1

def MaterialIN(barcode,user):
    
    global url 
    global port
    print(f'BARCODE SCANNED: {barcode}')
    r_material=req.get('http://'+url+':'+port+'/return/{}'.format(barcode))
    if r_material.status_code == 404:
        print('\nNON-EXISTENT MATERIAL\n')
    else:
        material=r_material.json()
        p_material=req.put('http://'+url+':'+port+'/return', data=json.dumps(material))
        if p_material.status_code == 404:
            print('\nERROR\n')
    ans=input('\nDO YOU NEED TO RETURN MORE?\nAVAILABLE ANSWERS:\ny : yes\nn : no\nINSERT ANSWER:\n')
    if ans == 'y':
        print('\nSCAN THE BARCODE\n')
    elif ans == 'n':
        Del_User(user)
    else:
        print('\nWRONG COMMAND\n')
        pass
            
def MaterialOUT(barcode,user):
    
    global url 
    global port
    print(f'BARCODE SCANNED: {barcode}')
    r_material=req.get('http://'+url+':'+port+'/barcode/{}'.format(barcode))
    if r_material.status_code == 404:
        print('\nNON-EXISTENT MATERIAL\n')
    else:
        material=r_material.json()
        p_material=req.put('http://'+url+':'+port+'/barcode', data=json.dumps(material))
        if p_material.status_code == 404:
            print('\nERROR\n')
    ans=input('\nDO YOU NEED TO TAKE MORE?\nAVAILABLE ANSWERS:\ny : yes\nn : no\nINSERT ANSWER:\n')
    if ans == 'y':
        print('\nSCAN THE BARCODE\n')
    elif ans == 'n':
        Del_User(user)
    else:
        print('\nWRONG COMMAND\n')
        pass
   
def Del_User(user):
    
    global url 
    global port
    r_user=req.get('http://'+url+':'+port+'/user/{}'.format(user))
    client.publish("user/exit", "User exiting", qos=1)
    if r_user.status_code == 404:
        print('\nACCESS DENIED\n')
    else:
        l_user=r_user.json()
        del_user=req.put('http://'+url+':'+port+'/user', data=json.dumps(l_user))
        print(f'\nThe user {user} has been deleted\n')
        print('\n----- OPERATION FINISHED -----\n')
        if del_user.status_code == 404:
            print('\nWRONG PROCEDURE\n')
            
       
class SubscribeData(object):

    def __init__(self, client):
        self.client=client
        self.fiscal_code='null'
        self.barcode = "null"
        
    def on_connect(client, userdata, flags, rc):
        # get the current time
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print ('CONNACK received with code: ' + str(rc))
        print ("at time: " + str(current_time))
        return str(rc)


    def on_publish(client, userdata, mid, granted_qos):
        print("Sending data to Thinkspeak")


    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        get_time = datetime.datetime.now()
        current_time =  get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("Subscribed messageID: " + str(mid) + ", with QoS: " + str(granted_qos[0]))
        print ("at time: " + str(current_time))
        print ("LISTENING")

    @classmethod
    def on_message(self,client, userdata, msg):
        get_time = datetime.datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("\nMessage received by JARVIS " + "at time: " + str(current_time))
        if (msg.topic == "user/ID_fiscal_code"):
            message_body = str(msg.payload.decode("utf-8"))
            self.fiscal_code = json.loads(message_body)
            main(self.fiscal_code["ID"])
        elif (msg.topic == "user/barcode"):
            message_body = str(msg.payload.decode("utf-8"))
            self.barcode = json.loads(message_body)
            if In_Out == 0:
                MaterialOUT(self.barcode["BC"], self.fiscal_code["ID"])
            elif In_Out == 1:
                MaterialIN(self.barcode["BC"], self.fiscal_code["ID"])
        
        
def main(fiscal_code):
    rt=RealTime()
    command=input('\nAVAILABLE COMMANDS:\nc : collection\nr : return\nINSERT COMMAND:\n')
    if command=='c' or command=='r':
        rt.handler(command,fiscal_code)
    else:
        print('\nWRONG COMMAND\n')

if __name__ == '__main__':
    

    client = mqttc.Client('Sub')

    
    sens = SubscribeData(client)
    In_Out = 0
    
    try:

        client.on_connect = SubscribeData.on_connect
        client.on_subscribe = SubscribeData.on_subscribe
        client.on_publish = SubscribeData.on_publish
        client.on_message = SubscribeData.on_message
        client.connect(broker_ip, int(port1), int(port2))
        client.subscribe("user/ID_fiscal_code", qos=1) #message ID 1
        client.subscribe("user/barcode", qos=1) #message ID 2
        client.publish("user/exit", qos = 1)
        client.loop_forever()
        
    except:
        print("Problem in connecting to broker")
        
        
        
        
        