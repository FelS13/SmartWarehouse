
import requests as req
import json
from telegram import InputTextMessageContent, ParseMode, InlineQueryResultArticle
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler
import logging



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
flag = 0

FISCAL_CODE =  0 

fiscal = ' '

file = open("configFile.json", "r")
jsonString = file.read()
file.close()
data = json.loads(jsonString)
API = data["APIkey"]
ip = data["resourceCatalog"]["ip"]
port = data["resourceCatalog"]["port"]


def start(update, context):
    
    update.message.reply_text(
            'This is the Telegram service of the Military Warehouse, please type in your fiscal code for the identification:')
    
    return FISCAL_CODE

def fiscal_code(update, context):
    
    global fiscal 
    global port
    global ip 
    fiscal = update.message.text
    logger.info("Message of : %s", update.message.text)
    r_fiscal = req.get('http://' + ip + ':' + port + '/telegram/fiscal?first=%s' %fiscal )
    if r_fiscal.status_code == 404:
        print('\nNON-EXISTENT USER\n')
        update.message.reply_text("Sorry, you're not allowed to use this service!")
        return ConversationHandler.END
    
    else: 
#        print('user allowed')
#        dati = {'id' : user_id, 'fiscal' : fiscal}
#        insert_id = req.put('http://127.0.0.1:8080/telegram', data = dati)
#        if  insert_id.status_code == 404:
#            print('\nWRONG PROCEDURE\n')
#        else: 
#            print("chat id updated")
            
        update.message.reply_text( 'Welcome to the Telegram service of the Military Warehouse!\n'            
            '1) To see the complete list of your movements press /movements\n'
            '2) To know what is the available material press /materials\n'
            '3) Press /help to have the list of all commands')
       
    return ConversationHandler.END




def help(update, context):
    update.message.reply_text('1) To see the complete list of your movements press /movements\n'
            '2) To know what is the available material press /materials\n')


    
    
    

def materials(update, context):
    global fiscal
    global port 
    global ip    
    
        
    r_material=req.get('http://' + ip + ':' + port + '/telegram/material')
    if r_material.status_code == 404:
        print('\nNON-EXISTENT MATERIAL\n')
        update.message.reply_text("non trovato")
    else:
        lista = r_material.text.split('},')
        for ele in lista:
            print(ele.replace('{', ' '))
        new = ' '
        for ele in lista:
            new += ele.replace('{', ' ') + "\n"
        #print(new[0:(len(new)-2)])  
        update.message.reply_text("This is the catalog of the material:\n %s ." %new[0:(len(new)-2)])
     
    #for key in material:
        #update.message.reply_text(key,'->', material[key])
   
    
    
    
def movements(update, context):
    
    global ip
    global port
    global fiscal
    r_movements = req.get('http://' + ip + ':' + port + '/telegram/moving?first=%s' %fiscal )
    if r_movements.status_code == 404:
        print('\nNON-EXISTENT MATERIAL\n')
    else: 
        lista = r_movements.text.split('},')
        for ele in lista:
            print(ele.replace('{', ' '))
        new = ' '
        for ele in lista:
            new += ele.replace('{', ' ') + "\n"
        #print(new[0:len(new)])  
        update.message.reply_text("This is the list of the products you rented:\n %s " %new[0:(len(new)-2)])
    
    


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    
    global API
    updater = Updater(API, use_context=True)
   
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FISCAL_CODE: [MessageHandler(filters = None, callback = fiscal_code)]
            },

       fallbacks = [CommandHandler('help', help)]
    )

    updater.dispatcher.add_handler(conv_handler)
    
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('movements', movements)) #cerca movimenti utente
    updater.dispatcher.add_handler(CommandHandler('materials', materials)) #cerca materiale utente
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)
     
    
    
    

    # start the bot
    updater.start_polling()
    
  
    
    updater.idle()
if __name__ == '__main__':
    main()



