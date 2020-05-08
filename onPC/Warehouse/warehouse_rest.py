from InitialData.catalog_db_rest import WarehouseDB
import sqlite3 as sql
import cherrypy as cp
import json, datetime






class WarehouseRestDB:
    exposed=True
    '''
    manage the outgoing flow of materials from the warehouse
    '''
    def __init__(self, directory):
        self.directory = directory
        
    def GET(self, *uri):
        # GET (READ of CRUD) - can only retrieve data
        # method to retrieve some material in the materials database
        # it receives as uri[0] the barcode to search
        connection=sql.connect(self.directory) # create a connection to the database specified in 'configFile.json'
        cursor=connection.cursor() # create a cursor to retrieve data in the connected database

        if len(uri)>0:

            sql_search="""SELECT * FROM materials WHERE barcode='%s' """ %(uri[0])
            # selct all the available fields in the materials database
            # that corresponds to the searched material

            cursor.execute(sql_search) # execute the sql_search script
            result=cursor.fetchall() # return the result of the research

            list_diz=[]
            for r in result:
                w=list(r)
                diz={'barcode':w[0], 'denomination':w[1], 'unit_price':w[2],
                     'actual_quantity':w[3], 'quantity_present':w[4]}
                # create a dict in which are stored all the information on the searched material
                list_diz.append(diz)
            if not list_diz:
                raise cp.HTTPError(404)
            list_diz=json.dumps(list_diz)[1:-1]
            return list_diz

    def PUT(self):
        # PUT (UPDATE of CRUD) - update an instance
        # method that receives as input the information on the enabled user
        # it takes information about the scanned material
        # and it updates moving materials and materials databases
        
        connection=sql.connect(self.directory)
        cursor=connection.cursor()
        string=cp.request.body.read() # read the input string with the information on the enabled user
        diz=json.loads(string) # convert the string in a JSON file

        sql_search="""SELECT * FROM enabled_users"""
        # selct all the available fields in the enabled users database
       
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
                # create a dict in which are stored all the information about the enabled user and the current time
                info_user.append(user)
            h=json.dumps(info_user)[1:-1] 
            jinfo_user=json.loads(h) # convert the string in a JSON file
            sql_in_search="""SELECT barcode FROM moving_materials WHERE barcode='%s'""" %(diz['barcode'])
            # select the barcode field in the moving materials database
            # in which the barcode is equal to the scanned one
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
                cursor.execute(sql_insert_moving_materials) # insert the scanned material in the moving materias database
                sql_update="""
                    UPDATE materials SET quantity_present = (quantity_present - 1) WHERE barcode='%s'""" %(diz['barcode'])
                cursor.execute(sql_update) # decreases the present quantity of the scanned material by 1 in the materials database
            else:
                sql_update_moving="""
                    UPDATE moving_materials SET moving_quantity = (moving_quantity + 1) WHERE barcode='%s'""" %(diz['barcode'])
                cursor.execute(sql_update_moving) # update the moving quantity of the scanned material in the moving materials database
                sql_update_materials="""
                    UPDATE materials SET quantity_present = (quantity_present - 1) WHERE barcode='%s'""" %(diz['barcode'])
                cursor.execute(sql_update_materials) # decreases the present quantity of the scanned material by 1 in the materials database

        connection.commit()
        connection.close()

class WarehouseIN:
    exposed=True
    '''
    manage the ingoing flow of materials from the warehouse
    '''
    def __init__(self, directory):
        self.directory = directory

    def GET(self, *uri):
        # GET (READ of CRUD) - can only retrieve data
        # method to retrieve some material in the moving materials database
        # it receives as uri[0] the barcode to search

        connection=sql.connect(self.directory) 
        cursor=connection.cursor() 

        if len(uri)>0:

            sql_search="""SELECT barcode FROM moving_materials WHERE barcode='%s' """ %(uri[0])
            # select the barcode field in the moving materials database
            # in which the barcode is equal to the scanned one
            cursor.execute(sql_search)
            result=cursor.fetchall()

            list_diz=[]
            for r in result:
                w=list(r)
                diz={'barcode':w[0]}
                list_diz.append(diz)
            if not list_diz:
                raise cp.HTTPError(404)
            list_diz=json.dumps(list_diz)[1:-1]
            return list_diz






    def PUT(self):
        # PUT (UPDATE of CRUD) - update an instance
        # method that receives as input the information on the enabled user
        # it takes information about the scanned material
        # and it updates moving materials and materials databases
        
        connection=sql.connect(self.directory)
        cursor=connection.cursor()
        string=cp.request.body.read() # read the input string with the information on the enabled user
        diz=json.loads(string) # convert the string in a JSON file 

        sql_search="""SELECT * FROM enabled_users"""
        # selct all the available fields in the enabled users database
        cursor.execute(sql_search)
        result=cursor.fetchall()

        if not result:
            raise cp.HTTPError(404, "NOT ENABLED USER")
        else:
        	info_user=[]
        	for r in result:
        		w=list(r)
        		user={"fiscal_code":w[0], "grade":w[1], "name":w[2], "surname":w[3],"time":w[4]}
                # create a dict in which are stored all the information about the enabled user
        		info_user.append(user)
        	h=json.dumps(info_user)[1:-1]
        	jinfo_user=json.loads(h) # convert the string in a JSON file
        	sql_in_search="""SELECT barcode FROM moving_materials WHERE barcode='%s' AND fiscal_code='%s'""" %(diz['barcode'], jinfo_user['fiscal_code'])
            # select the barcode field in the moving materials database
            # in which the barcode is equal to the scanned one
            # and the fiscal code is equal to the enabled user one
        	cursor.execute(sql_in_search)
        	in_result=cursor.fetchall()
        	if not in_result:
        		raise cp.HTTPError(404, "ERROR")
        	else:
        		sql_search_quantity="""SELECT moving_quantity FROM moving_materials WHERE barcode='%s'""" %(diz['barcode'])
                # select the moving quantity field in the moving materials database
                # in which the barcode is equal to the scanned one
        		cursor.execute(sql_search_quantity)
        		quantity=cursor.fetchall()
        		b=json.dumps(quantity)
        		q=int(b[2:-2]) # it is the integer quantity of the selected material
        		if q == 1:
        			sql_delete="""DELETE FROM moving_materials WHERE barcode='%s' AND fiscal_code='%s'""" %(diz['barcode'], jinfo_user['fiscal_code'])
                    # if there is only 1 material in the moving materials database
                    # in which the barcode is equal to the scanned one
                    # and the fiscal code is equal to the one of the enabled user
                    # delete the entry 
        			cursor.execute(sql_delete)
        			sql_update_materials="""
        			UPDATE materials SET quantity_present = (quantity_present +1) WHERE barcode='%s'""" %(diz['barcode'])
                    # increases the present quantity of the scanned material by 1 in the materials database
        			cursor.execute(sql_update_materials)
        		else:
        			sql_update_moving="""
        			UPDATE moving_materials SET moving_quantity = (moving_quantity - 1) WHERE barcode='%s' AND fiscal_code='%s'""" %(diz['barcode'], jinfo_user['fiscal_code'])
        			# if there is more than 1 material in the moving materials database
                    # in which the barcode is equal to the scanned one
                    # and the fiscal code is equal to the one of the enabled user
                    # decrease the moving quantity by 1
                    cursor.execute(sql_update_moving)
        			sql_update_materials="""
        			UPDATE materials SET quantity_present = (quantity_present +1) WHERE barcode='%s'""" %(diz['barcode'])
                    # increases the present quantity of the scanned material by 1 in the materials database
        			cursor.execute(sql_update_materials)
        connection.commit()
        connection.close()

class UserRestDB:
    exposed=True

    def __init__(self, directory):
        self.directory = directory
        pass

    def GET(self, *uri):
        # GET (READ of CRUD) - can only retrieve data
        # method to check the enabled users
        # it receives as uri[0] the fiscal code to search
        # and check if it is present in the users database
        
        connection=sql.connect(self.directory)
        cursor=connection.cursor()

        fiscal_code=uri[0]

        sql_search="""SELECT fiscal_code FROM users WHERE fiscal_code='%s' """ %(fiscal_code)
        # select the fiscal code field in the users database
        # in which the fiscal code is equal to the inserted one
        cursor.execute(sql_search)
        result=cursor.fetchall()


        if not result:
            raise cp.HTTPError(404)
        else:
            sql_return="""SELECT * FROM users WHERE fiscal_code='%s' """ %(fiscal_code)
            # selct all the available fields in the users database
            # in which the fiscal code is equal to the inserted one
            cursor.execute(sql_return)
            result=cursor.fetchall()
            info_user=[]
            for r in result:
                w=list(r)
                user={"fiscal_code":w[0], "grade":w[1], 
                      "name":w[2], "surname":w[3]}
                info_user.append(user)
            return json.dumps(info_user)[1:-1]
        connection.close()

    def POST(self):
        # POST (UPDATE of CRUD) - create an instance
        # method that receives as input the information on the enabled user
        # and the current time
        # and create an instance of on the enabled users database
        
        connection=sql.connect(self.directory)
        cursor=connection.cursor()               
        now=datetime.datetime.now()
        jstring=cp.request.body.read() # read the input string with the fiscal code of the entering user 
        diz=json.loads(jstring) # convert the string in a JSON file 

        sql_insert_enabled_user="""
            INSERT INTO enabled_users (fiscal_code, grade, name, surname, time)
            VALUES ('%s','%s','%s','%s','%s');
            """ %(diz['fiscal_code'],diz['grade'],diz['name'],
                  diz['surname'], now)
        # 

        sql_search="""SELECT fiscal_code FROM enabled_users WHERE fiscal_code='%s' """ %diz['fiscal_code']
        cursor.execute(sql_search)
        result=cursor.fetchall()
    
        if not result:
            cursor.executescript(sql_insert_enabled_user)

        else:
            raise cp.HTTPError(404)

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
    
    
    file = open("configFile.json", "r") # open the configuration file
    jsonString = file.read()
    file.close()
    data = json.loads(jsonString) # covert the string in a JSON format
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
