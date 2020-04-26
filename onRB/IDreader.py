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
            #print ("Sto usando: ", reader)
            connection = reader.createConnection()
            connection.connect() 
            
            #il file che ci serve si trova in: MF>DF1>EF_DATI_PERS
            #Seleziona del MF (master folder)
            #CLS 00, istruzione A4 (seleziona file), P1 = P2 = 0 (seleziona per ID),
            #Lc: 2, Data: 3F00 (id del MF)
            SELECT_MF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
            data, sw1, sw2 = connection.transmit(SELECT_MF)
            #se tutto è andato a buon fine sw1 e sw2 contengono
            #rispettivamente i valori 0x90 e 0x00 il corrispettivo del 200 in HTTP
            
            #Seleziona del DF1...vedi sopra
            SELECT_DF1 = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x00]
            data, sw1, sw2 = connection.transmit(SELECT_DF1)
            
            #Seleziona del file EF.Dati_personali... vedi sopra sopra
            SELECT_EF_PERS = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02]
            data, sw1, sw2 = connection.transmit(SELECT_EF_PERS)
            
            #leggiamo i dati
            #CLS 00, istruzione B0 (leggi i dati binari contenuti nel file
            READ_BIN = [0x00, 0xB0, 0x00, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(READ_BIN)
            #data contiene i dati anagrafici in formato binario
            #trasformiamo il tutto in una stringa
            stringa_dati_personali = array.array('B', data).tostring()
            
            
            dimensione = int(stringa_dati_personali[0:6],16)
            print ("Dimensione in byte dei dati: ", dimensione)
            
            da = 68
            a = 84
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
    
if __name__ == '__main__':
    "this is for testing we use this class in the PublishTempHum class"
    data_of_ID = ID_Reader()
    count = 0
    while count<2:
        data_of_ID.senseID()
        count += 1