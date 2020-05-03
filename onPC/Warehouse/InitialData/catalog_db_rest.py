import sqlite3 as sql
import cherrypy as cp
import json, os, datetime

class WarehouseDB:
    def __init__(self):
        # create and populate the DB if it doesn't exist yet
        # the data to populate the DB are in a * .txt file
        if os.path.isfile('catalog.db') == False:
            connection=sql.connect('catalog.db')
            self.cursor=connection.cursor()

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
            
            self.cursor.executescript(sql_create)
            
            sql_insert=open('insert_database.txt','r').read()
            self.cursor.executescript(sql_insert)
            
            connection.commit()
            connection.close()

if __name__ == '__main__':
	WarehouseDB()
