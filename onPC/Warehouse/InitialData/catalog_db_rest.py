import sqlite3 as sql
import cherrypy as cp
import json, os, datetime

class WarehouseDB:
    def __init__(self):
        # create and populate the DB if it doesn't exist yet
        # the data to populate the DB are stored in a * .txt file
        if os.path.isfile('catalog.db') == False: # check the existence of a database named 'catalog.db'
            connection=sql.connect('catalog.db') # create a connection to the database named 'catalog.db'
            self.cursor=connection.cursor() # create a cursor on the connection object

            sql_create="""			  
            CREATE TABLE users (
            fiscal_code VARCHAR(20) PRIMARY KEY,
            grade VARCHAR(20),
            name VARCHAR(20),
            surname VARCHAR(20));
            
            CREATE TABLE materials (
            barcode VARCHAR(15) PRIMARY KEY,
            denomination VARCHAR(40),
            unit_price REAL,
            actual_quantity INTEGER,
            quantity_present INTEGER);
            
            CREATE TABLE enabled_users (
            fiscal_code VARCHAR(20) PRIMARY KEY,
            grade VARCHAR(20),
            name VARCHAR(20),
            surname VARCHAR(20),
            time DATE);
            
            CREATE TABLE moving_materials (
            barcode VARCHAR(15) PRIMARY KEY,
            denomination VARCHAR(40),
            moving_quantity INTEGER,
            fiscal_code VARCHAR(15),
            grade VARCHAR(20),
            name VARCHAR(20),
            surname VARCHAR(20),
            time DATE);"""
            
            self.cursor.executescript(sql_create) # execute the sql_create script and create the tables
            
            sql_insert=open('insert_database.txt','r').read() # insert in the tables the initial data stored in
							      # the file 'insert_database.txt'
            self.cursor.executescript(sql_insert) # execute the sql_insert script
            
            connection.commit() # commit the connection
            connection.close()  # close the connection

if __name__ == '__main__':
	WarehouseDB()
