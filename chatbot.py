import os
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                          CallbackContext)
#import configparser
import logging
#import redis
import pymongo
from ChatGPT_HKBU import HKBU_ChatGPT
import json
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

# test workflow

global mycol
def main():
    # Load your token and create an Updater for your Bot
    #config = configparser.ConfigParser()
    #config.read('config.ini')
    #updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)

    keyVaultName = os.environ["KEY_VAULT_NAME"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"

    credential = ClientSecretCredential(
	tenant_id= os.environ["AZURE_TENANT_ID"],
	client_id= os.environ["AZURE_CLIENT_ID"],
	client_secret= os.environ["AZURE_CLIENT_SECRET"]
	)
    client = SecretClient(vault_url=KVUri, credential=credential)

    updater = Updater(token=(client.get_secret("AccessToken").value), use_context=True)
    dispatcher = updater.dispatcher
    global mycol
    #redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
    #redis1 = redis.Redis(host=(os.environ['REDIS_HOST']), password=(os.environ['REDIS_PASSWORD']), port=(os.environ['REDIS_PORT']))

    # You can set this logging module, so you will know when and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    logging.info("COMP7940 Begin chatbot logging")
    print("COMP7940 Begin chatbot print")

    mongoUrl="mongodb://"+client.get_secret("MongodbUser").value+":"+client.get_secret("MongodbPwd").value+"@"+client.get_secret("MongodbHost").value+":10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@"+client.get_secret("MongodbUser").value+"@"
    myclient = pymongo.MongoClient(mongoUrl)
    mydb = myclient["ChatBotDB"]

    mycol = mydb["ChatBotCollection"]
   
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    #echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    #dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    #chatgpt = HKBU_ChatGPT(config)
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("addReview", addReview))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("searchByGenre", searchByGenre))
    dispatcher.add_handler(CommandHandler("searchByMovie", searchByMovie))
    dispatcher.add_handler(CommandHandler("searchByRating", searchByRating))

    
    # To start the bot:
    updater.start_polling()
    updater.idle()



def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)


def equiped_chatgpt(update, context): 
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def addReview(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global mycol
        logging.info("len(context.args)= " + str(len(context.args)))
        
        if(len(context.args) ==0):
            update.message.reply_text('Usage: /addReview <Movie Name>, <Genres>, <Rating from 1 to 10>, <Review>')
            return
        concatArgs=' '.join(context.args)
        newArgs=map(lambda s:s.strip(), concatArgs.split(','))
        newArgs=list(newArgs)

        logging.info("newArgs[2].isnumberic()= " + str(newArgs[2].isnumeric()))
        if(not newArgs[2].isnumeric() or int(newArgs[2]) <1 or int(newArgs[2]) >10):
            update.message.reply_text('Usage: /addReview <Movie Name>, <Genres>, <Rating from 1 to 10>, <Review>')
            return
        if(len(newArgs) !=4):
            update.message.reply_text('Usage: /addReview <Movie Name>, <Genres>, <Rating from 1 to 10>, <Review>')
            return                    
        #msg = context.args[0]   # /add keyword <-- this should store the keyword
        #mycol.incr(msg)

        json_str='{"movieName": "' +newArgs[0] + '", "genres": "' + newArgs[1]+ '", "rating": '+ newArgs[2]+', "review": "' +newArgs[3] +'", "chatBotCategoryId":"movieReview"}'
        logging.info(json_str)
        movieReview = json.loads(json_str)

        x = mycol.insert_one(movieReview)

        outputString = ""
        for x in mycol.find():
            print(x)

        
        update.message.reply_text('You have added a new movie review for movie ' + newArgs[0]  + '.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <Movie Name>, <Genres>, <Rating from 1 to 10>, <Review>')

def searchByGenre(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global mycol
        logging.info("len(context.args)= " + str(len(context.args)))
        
        if(len(context.args) ==0):
            update.message.reply_text('Usage: /searchByGenre <Genre>')
            return
        json_str='{"genres":{"$regex":"'+ ' '.join(context.args)+'","$options":"i"}}'
        logging.info(json_str)
        genres = json.loads(json_str)
        
        myResult = mycol.find(genres)
        listResult = list(myResult)
        logging.info("len(list(myResult))="+str(len(listResult)))
        logging.info("2 len(list(myResult))="+str(len(listResult)))

        searchResultTxt=""
        if len(listResult)>0:
            
            for index, item in enumerate(listResult):
                print(index, item)
                searchResultTxt=searchResultTxt+"\n#"+str(index+1)+". Movie Name: " + item['movieName'] + "\n       Genres: "+item['genres']+"\n       "\
                                 "Rating: "+str(item['rating']) + "\n       Review: "+item['review']

        
            update.message.reply_text('Below are the first 3 results search by genre:' + searchResultTxt)
        else:
            update.message.reply_text('No result returned.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /searchByGenre <Genres>')

def searchByMovie(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global mycol
        logging.info("len(context.args)= " + str(len(context.args)))
        
        if(len(context.args) ==0):
            update.message.reply_text('Usage: /searchByMovie <Movie Name>')
            return
        json_str='{"movieName":{"$regex":"'+ ' '.join(context.args)+'","$options":"i"}}'
        logging.info(json_str)
        movieName = json.loads(json_str)
        
        myResult = mycol.find(movieName)
        listResult = list(myResult)
        logging.info("len(list(myResult))="+str(len(listResult)))
        logging.info("2 len(list(myResult))="+str(len(listResult)))

        searchResultTxt=""
        if len(listResult)>0:
            
            for index, item in enumerate(listResult):
                print(index, item)
                searchResultTxt=searchResultTxt+"\n#"+str(index+1)+". Movie Name: " + item['movieName'] + "\n       Genres: "+item['genres']+"\n       "\
                                 "Rating: "+str(item['rating']) + "\n       Review: "+item['review']

        
            update.message.reply_text('Below are the first 3 results search by movie name:' + searchResultTxt)
        else:
            update.message.reply_text('No result returned.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /searchByMovie <Movie Name>')

def searchByRating(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global mycol
        logging.info("len(context.args)= " + str(len(context.args)))
        
        if(len(context.args) !=2):
            update.message.reply_text('Usage: /searchByRating <operator> <rating> ; operation <= or = or >= and rating between 1 to 10')
            return
        if not(context.args[0]!="<=" or context.args[0]!="=" or context.args[0]!=">="):
            update.message.reply_text('Usage: /searchByRating <operator> <rating> ; operation <= or = or >= and rating between 1 to 10')
            return
        if (not context.args[1].isnumeric() or int(context.args[1]) <1 or int(context.args[1]) >10):
            update.message.reply_text('Usage: /searchByRating <operator> <rating> ; operation <= or = or >= and rating between 1 to 10')
            return

        logging.info("context.args[0]="+context.args[0])
        logging.info("context.args[1]="+context.args[1])
        operator=""
        json_str=""
        if context.args[0]=="<=":
            operator="$lte"
            json_str='{"rating":{"'+operator+'": '+ context.args[1]+'}}'
        elif context.args[0]==">=":
            operator="$gte"
            json_str='{"rating":{"'+operator+'": '+ context.args[1]+'}}'
        elif context.args[0]=="=":
            json_str='{"rating": '+ context.args[1]+'}'
        
        logging.info(json_str)
        movieName = json.loads(json_str)
        
        myResult = mycol.find(movieName).limit(3)
        listResult = list(myResult)
        logging.info("len(list(myResult))="+str(len(listResult)))
        logging.info("2 len(list(myResult))="+str(len(listResult)))

        searchResultTxt=""
        if len(listResult)>0:
            
            for index, item in enumerate(listResult):
                print(index, item)
                searchResultTxt=searchResultTxt+"\n#"+str(index+1)+". Movie Name: " + item['movieName'] + "\n       Genres: "+item['genres']+"\n       "\
                                 "Rating: "+str(item['rating']) + "\n       Review: "+item['review']

        
            update.message.reply_text('Below are the first 3 results search by movie name:' + searchResultTxt)
        else:
            update.message.reply_text('No result returned.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /searchByRating <operator> <rating> ; operation <= or = or >= and rating between 1 to 10')

def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    try:
        global redis1
        msg = ' '.join(context.args)   # /add keyword <-- this should store the keyword
        logging.info(msg)        
        redis1.incr(msg)
        update.message.reply_text('Good day, ' + msg +  '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')


if __name__ == '__main__':
    main()
