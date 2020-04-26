from InitialData.catalog_db_rest import WarehouseDB
import sqlite3 as sql
import cherrypy as cp
import json, datetime






class WarehouseRestDB:
    exposed=True
    
    def __init__(self, directory):
        #self.db=WarehouseDB()
        self.directory = directory
        
    def GET(self, *uri):
        # GET (READ of CRUD) - può solo recuperare dati
        # funzione per cercare del materiale nel DB
        # riceve come uri[0] il barcode da ricercare
        connection=sql.connect(self.directory) # crea una connessione al database 'catalog.db'
        cursor=connection.cursor() # crea un cursore per ritovare i dati dal database connesso

        if len(uri)>0:

            sql_search="""SELECT * FROM materials WHERE barcode='%s' """ %(uri[0])
            # seleziona tutti i campi disponibili dalla tabella materials
            # corrispondenti al materiale cercato

            cursor.execute(sql_search) # esegue la ricerca
            result=cursor.fetchall() # ritorna il risultato della ricerca

            list_diz=[]
            for r in result:
                w=list(r)
                diz={'barcode':w[0], 'denomination':w[1], 'unit_price':w[2],
                     'actual_quantity':w[3], 'quantity_present':w[4]}
                # crea un dizionario contenente tutte le informazioni sul materiale cercato
                list_diz.append(diz)
            if not list_diz:
                raise cp.HTTPError(404)
            list_diz=json.dumps(list_diz)[1:-1] #ritorna il dizionario senza []
            return list_diz

    def PUT(self):
        # PUT (UPDATE of CRUD) - aggiorna un'istanza
        # funzione che riceve in ingresso un JSON con le info dell'utente abilitato
        # prende informazioni su materiale scansionato tramite webcam
        # e aggiorna la tabella moving_materials e la tabella materials
        connection=sql.connect(self.directory)
        cursor=connection.cursor()
        string=cp.request.body.read()
        diz=json.loads(string) #codifico il dizionario in ingresso come un oggetto JSON

        sql_search="""SELECT * FROM enabled_users"""
        cursor.execute(sql_search)
        result=cursor.fetchall()

        if not result:
            raise cp.HTTPError(404, "NOT ENABLED USER")
        else:
            info_user=[]
            for r in result:
                w=list(r)
                user={"fiscal_code":w[0], "grade":w[1], 
                      "name":w[2], "surname":w[3],"time":w[4]}
                info_user.append(user)
            h=json.dumps(info_user)[1:-1] #elimino le parentesi quadre iniziali
            jinfo_user=json.loads(h)
            sql_in_search="""SELECT barcode FROM moving_materials WHERE barcode='%s'""" %(diz['barcode'])
            cursor.execute(sql_in_search)
            in_result=cursor.fetchall()
            if not in_result:
                moving_quantity = 1
                sql_insert_moving_materials="""
                    INSERT OR IGNORE INTO moving_materials (barcode, denomination, moving_quantity,
                                              fiscal_code, grade, name, surname, time)
                    VALUES ('%s','%s','%d','%s','%s','%s','%s','%s');
                    """ %(diz['barcode'], diz['denomination'], moving_quantity, jinfo_user['fiscal_code'],
                        jinfo_user['grade'],jinfo_user['name'],
                        jinfo_user['surname'], jinfo_user['time'])
                cursor.execute(sql_insert_moving_materials)
                sql_update="""
                    UPDATE materials SET quantity_present = (quantity_present - 1) WHERE barcode='%s'""" %(diz['barcode'])
                cursor.execute(sql_update)
            else:
                sql_update_moving="""
                    UPDATE moving_materials SET moving_quantity = (moving_quantity + 1) WHERE barcode='%s'""" %(diz['barcode'])
                cursor.execute(sql_update_moving)
                sql_update_materials="""
                    UPDATE materials SET quantity_present = (quantity_present - 1) WHERE barcode='%s'""" %(diz['barcode'])
                cursor.execute(sql_update_materials)

        connection.commit()
        connection.close()

class WarehouseIN:
    exposed=True

    def __init__(self, directory):
        #self.db=WarehouseDB()
        self.directory = directory

    def GET(self, *uri):
        # GET (READ of CRUD) - può solo recuperare dati
        # funzione per cercare del materiale nella tabella moving_materials del DB
        # riceve come uri[0] il barcode da ricercare
        connection=sql.connect(self.directory) # crea una connessione al database 'catalog.db'
        cursor=connection.cursor() # crea un cursore per ritovare i dati dal database connesso

        if len(uri)>0:

            sql_search="""SELECT barcode FROM moving_materials WHERE barcode='%s' """ %(uri[0])
            cursor.execute(sql_search) # esegue la ricerca
            result=cursor.fetchall() # ritorna il risultato della ricerca

            list_diz=[]
            for r in result:
                w=list(r)
                diz={'barcode':w[0]}
                list_diz.append(diz)
            if not list_diz:
                raise cp.HTTPError(404)
            list_diz=json.dumps(list_diz)[1:-1] #ritorna il dizionario senza []
            return list_diz






    def PUT(self):
        # PUT (UPDATE of CRUD) - aggiorna un'istanza
        # funzione che riceve in ingresso un JSON con le info dell'utente abilitato
        # prende informazioni su materiale scansionato tramite webcam
        # e aggiorna la tabella moving_materials e la tabella materials
        connection=sql.connect(self.directory)
        cursor=connection.cursor()
        string=cp.request.body.read()
        diz=json.loads(string) #codifico il dizionario in ingresso come un oggetto JSON

        sql_search="""SELECT * FROM enabled_users"""
        cursor.execute(sql_search)
        result=cursor.fetchall()

        if not result:
            raise cp.HTTPError(404, "NOT ENABLED USER")
        else:
        	info_user=[]
        	for r in result:
        		w=list(r)
        		user={"fiscal_code":w[0], "grade":w[1], "name":w[2], "surname":w[3],"time":w[4]}
        		info_user.append(user)
        	h=json.dumps(info_user)[1:-1]
        	jinfo_user=json.loads(h)
        	sql_in_search="""SELECT barcode FROM moving_materials WHERE barcode='%s' AND fiscal_code='%s'""" %(diz['barcode'], jinfo_user['fiscal_code'])
        	cursor.execute(sql_in_search)
        	in_result=cursor.fetchall()
        	if not in_result:
        		raise cp.HTTPError(404, "ERROR")
        	else:
        		sql_search_quantity="""SELECT moving_quantity FROM moving_materials WHERE barcode='%s'""" %(diz['barcode'])
        		cursor.execute(sql_search_quantity)
        		quantity=cursor.fetchall()
        		b=json.dumps(quantity)
        		q=int(b[2:-2])
        		if q == 1:
        			sql_delete="""DELETE FROM moving_materials WHERE barcode='%s' AND fiscal_code='%s'""" %(diz['barcode'], jinfo_user['fiscal_code'])
        			cursor.execute(sql_delete)
        			sql_update_materials="""
        			UPDATE materials SET quantity_present = (quantity_present +1) WHERE barcode='%s'""" %(diz['barcode'])
        			cursor.execute(sql_update_materials)
        		else:
        			sql_update_moving="""
        			UPDATE moving_materials SET moving_quantity = (moving_quantity - 1) WHERE barcode='%s' AND fiscal_code='%s'""" %(diz['barcode'], jinfo_user['fiscal_code'])
        			cursor.execute(sql_update_moving)
        			sql_update_materials="""
        			UPDATE materials SET quantity_present = (quantity_present +1) WHERE barcode='%s'""" %(diz['barcode'])
        			cursor.execute(sql_update_materials)
        connection.commit()
        connection.close()

class UserRestDB:
    exposed=True

    def __init__(self, directory):
        self.directory = directory
        pass

    def GET(self, *uri):
        # GET (READ of CRUD) - può solo recuperare dati
        # funzione per controllare gli utenti abilitati
        # riceve come uri[0] il codice fiscale e lo confronta
        #con quelli presenti nella tabella users nel DB        
        connection=sql.connect(self.directory)
        cursor=connection.cursor()

        fiscal_code=uri[0]

        sql_search="""SELECT fiscal_code FROM users WHERE fiscal_code='%s' """ %(fiscal_code)

        cursor.execute(sql_search)
        result=cursor.fetchall()


        if not result:
            raise cp.HTTPError(404)
        else:
            sql_return="""SELECT * FROM users WHERE fiscal_code='%s' """ %(fiscal_code)
            cursor.execute(sql_return)
            result=cursor.fetchall()
            info_user=[]
            for r in result:
                w=list(r)
                user={"fiscal_code":w[0], "grade":w[1], 
                      "name":w[2], "surname":w[3]}
                info_user.append(user)
            return json.dumps(info_user)[1:-1] #ritorna le info utenti senza []
        connection.close()

    def POST(self):
        # POST (CREATE of CRUD) - crea un'istanza
        # funzione che riceve in ingresso un JSON con le info dell'utente abilitato 
        # e l'orario di accesso e crea l'istanza nelLa tabella enabled_user nel DB
        connection=sql.connect(self.directory)
        cursor=connection.cursor()               
        now=datetime.datetime.now()
        jstring=cp.request.body.read() #json
        diz=json.loads(jstring) #dizionario con info utente

        sql_insert_enabled_user="""
            INSERT INTO enabled_users (fiscal_code, grade, name, surname, time)
            VALUES ('%s','%s','%s','%s','%s');
            """ %(diz['fiscal_code'],diz['grade'],diz['name'],
                  diz['surname'], now)

      

        sql_search="""SELECT fiscal_code FROM enabled_users WHERE fiscal_code='%s' """ %diz['fiscal_code']
        cursor.execute(sql_search)
        result=cursor.fetchall()

        if not result:
            cursor.executescript(sql_insert_enabled_user)
            #cursor.executescript(sql_insert_moving_materials)

        else:
            raise cp.HTTPError(404)
            #return diz['fiscal_code']

        connection.commit()
        connection.close()

    def PUT(self):
        # PUT (UPDATE of CRUD) - aggiorna un'istanza
        # funzione che riceve in ingresso un JSON con le info dell'utente abilitato
        # e lo elimina dala tabella enabled_user nel DB
        connection=sql.connect(self.directory)
        cursor=connection.cursor()               
        jstring=cp.request.body.read() #json
        diz=json.loads(jstring)       

        sql_search="""SELECT fiscal_code FROM enabled_users WHERE fiscal_code='%s' """ %diz['fiscal_code']
        cursor.execute(sql_search)
        result=cursor.fetchall()

        if not result:
            raise cp.HTTPError(404, "ERROR: WRONG PROCEDURE")
        else:
            sql_delete="""DELETE FROM enabled_users WHERE fiscal_code='%s' """ %diz['fiscal_code']
            cursor.execute(sql_delete)
        
        connection.commit()
        connection.close()


class TelegramDB:
    exposed = True
    def __init__(self, directory):
        #self.db=WarehouseDB()
        self.directory = directory

    def GET(self, *uri, **params):
       
        connection=sql.connect(self.directory) 
        cursor=connection.cursor() 
        if len(uri)>0:
            if(uri[0] == 'moving'):
                sql_search="""SELECT * FROM moving_materials WHERE fiscal_code  ='%s' """ %(params['first'])
               
                cursor.execute(sql_search)
                result=cursor.fetchall() 
                list_diz=[]
                for r in result:
                    w=list(r)
                    diz={'obj':w[1], 'moving_qty':w[2], 'time':w[7]}
                
                    list_diz.append(diz)
                if not list_diz:
                    raise cp.HTTPError(404)
                list_diz=json.dumps(list_diz)[1:-1]
                return list_diz
            
            if(uri[0] == 'material'):
                sql_search="""SELECT * FROM materials"""
                cursor.execute(sql_search)
                result=cursor.fetchall() 

                list_diz=[]
                for r in result:
                    w=list(r)
                    diz={'obj':w[1], 'qty':w[3]}
                    
                    list_diz.append(diz)
                if not list_diz:
                    raise cp.HTTPError(404)
                list_diz=json.dumps(list_diz)[1:-1] 
                return list_diz
            
            elif(uri[0]=='fiscal'): 
                sql_search= """SELECT fiscal_code FROM users where fiscal_code = '%s' """ %(params['first'])
                cursor.execute(sql_search)
                result=cursor.fetchall()
                if not result:
                    raise cp.HTTPError(404)
                return
                
            


    

if __name__ == '__main__': 
    
    
    file = open("configFile.json", "r")
    jsonString = file.read()
    file.close()
    data = json.loads(jsonString)
    ip = data["resourceCatalog"]["ip"]
    port = data["resourceCatalog"]["port"]
    directory = data["database"]
    
    
    
    
    conf = { 
        '/': { 
            'request.dispatch': cp.dispatch.MethodDispatcher(), 
             'tools.sessions.on': True, 
        } 
    } 
    cp.tree.mount (WarehouseRestDB(directory), '/barcode', conf)
    cp.tree.mount (UserRestDB(directory),'/user', conf)
    cp.tree.mount(WarehouseIN(directory),'/return', conf)
    cp.tree.mount(TelegramDB(directory),'/telegram', conf)
    cp.config.update({"server.socket_host": str(ip), "server.socket_port": int(port)}) 
    cp.engine.start() 
    
    
    
    
    
    cp.engine.block()
    cp.engine.exit()
