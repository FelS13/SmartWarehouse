#!/usr/bin/python
#-*- coding: utf-8 -*-


import datetime
import json
from smartcard.System import readers
import array


"Reading ID fiscal code from the Sensor"

class ID_Reader(object): 
    
    def __init__(self):

        self.Id = ''

    def senseID(self): 
        try: 
            
            r = readers()
            reader = r[0]
            #print ("I'm using: ", reader)
            connection = reader.createConnection()
            connection.connect() 
            
            #file we need can be find in: MF>DF1>EF_DATI_PERS
            #Select MF (master folder)
            #CLS 00, instr. A4 (select file), P1 = P2 = 0 (select per ID),
            #Lc: 2, Data: 3F00 (id del MF)
            SELECT_MF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
            data, sw1, sw2 = connection.transmit(SELECT_MF)
            # sw1 e sw2 contain values 0x90 e 0x00 
            
            #Select of DF1
            SELECT_DF1 = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x00]
            data, sw1, sw2 = connection.transmit(SELECT_DF1)
            
            #Select file EF.Dati_personali
            SELECT_EF_PERS = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02]
            data, sw1, sw2 = connection.transmit(SELECT_EF_PERS)
            
            #data reading
            #CLS 00, instruction B0 (reads binary data in file)
            READ_BIN = [0x00, 0xB0, 0x00, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(READ_BIN)
            #contains anagraphic data
            #transfor in string
            stringa_dati_personali = array.array('B', data).tostring()
            
            
            dimensione = int(stringa_dati_personali[0:6],16)
            print ("Dimension of string: ", dimensione)
            
            from = 68
            to = 84
            codice_fiscale = stringa_dati_personali[da:a]
            print ("CF: ", codice_fiscale)
            
            self.Id = codice_fiscale

        except: 
            #print("ID_Reader_Sensor: ERROR IN READING THE ID")
            pass
        if self.Id is not None and self.Id != '': 
            get_time = datetime.datetime.now()
            current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
            print('These are the sensed data:')
            print("ID_Reader_sensor : ", 'Time: ' ,current_time ,' ID : ' , self.Id)

            "put all the data in a Json"
            OutputJson = json.dumps({"ID": self.Id, "time":current_time})
            self.Id = ""
            return OutputJson
        else:
            #print('ID_Reader_Sensor: ERROR IN SENDING JSON')
            pass
        return
