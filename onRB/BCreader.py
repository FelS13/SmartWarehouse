# -*- coding: utf-8 -*-

from pyzbar.pyzbar import decode
import datetime
import cv2, json, time
import requests as req

"Reading BARCODE from the Webcam"

class BC_Reader(object): 
    
    def __init__(self):
		#initialize barcode
        self.barcode = ''
        
    def senseBC(self): 
        try: 
            barcode=''
	    	#start video capture
            cap = cv2.VideoCapture(0)
            
			#try to scanning a barcode, until the camera reads it
            while(True):
			    time.sleep(0.1)
			  	while(True):
			      	_, img = cap.read()
					#transform the image in a grey scale image
					gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
					barcodes = decode(gray_img)
					if barcodes:
						break

				barcode = barcodes[0].data.decode('utf-8')
				if barcode!='':
					break
            print(barcode)
            self.barcode = barcode
        except: 
            #print("BC_Reader_Sensor: ERROR IN READING THE BARCODE")
            pass
        if self.barcode is not None and self.barcode != '': 
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print('These are the sensed data:')
            print("BC_Reader_sensor : ", 'Time: ' ,current_time ,' BC : ' , self.barcode)

            "put all the data in a Json"
            OutputJson = json.dumps({"BC": self.barcode, "time":current_time})
            self.barcode = ""
            return OutputJson
        else:
            #print('BC_Reader_sensor: ERROR IN SENDING JSON')
            pass
        return
