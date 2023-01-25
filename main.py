import requests
import json
import time
from decimal import Decimal
from settings import api_key,api_secret,discord_autho,balance_margin,testnet1,discord_channel,market_pos
from binance.client import Client
import re
import math
quantity1 = 0
quantity_entry1 = 0
quantity2 = 0
quantity_entry2 = 0
usdt_balance = 0
client = Client(api_key=api_key, api_secret=api_secret,testnet = testnet1)
def retrieve_last_message(channelid):
    global content
    headers = {
        'authorization': discord_autho
    }
    position = "Position not found"
    r = requests.get(f'https://discord.com/api/v6/channels/{channelid}/messages?limit=3', headers=headers)
    jsonn = json.loads(r.text)
    last_message = jsonn[-3]
    content = last_message['content']
    lines = content.strip().split("\n")
    instrument = lines[0].strip()
    target = '0'
    stoploss = '0'
    for line in lines:
        if "Target 1:" in line:
             target = line.split(":")[1].strip().split("(")[0]
        elif "Stoploss:" in line:
            stoploss = line.split(":")[1].strip().split("(")[0]

    match = re.search("Entry: ([\d.]+)", content)
    if match:
        entry_price = float(match.group(1))
        
    
    for line in lines:
        long_split = line.split("BUY/LONG")
        short_split = line.split("SELL/SHORT")
        if len(long_split) > 1:
            position = "BUY/LONG"
            break
        elif len(short_split) > 1:
            position = "SELL/SHORT"
            break

        
    return content,instrument,target,stoploss,position,entry_price
content, instrument, target, stoploss,position,entry_price = retrieve_last_message(discord_channel)

def send_message_to_user(message):
    # code to send message to user
    pass   

bought_symbols = []
while True:
    
    for item in client.futures_account_balance():
        if item['asset'] == 'USDT':
            usdt_balance = float(item['balance'])
            break
        print(usdt_balance)
    
    content, instrument, target, stoploss, position, entry_price = retrieve_last_message(discord_channel)
    modified_string = instrument.replace("$", "") + "USDT"
    print(modified_string)
    key = f"https://api.binance.com/api/v3/ticker/price?symbol={modified_string}"
    data = requests.get(key)  
    data = data.json()
    last_price = float(data['price'])
    




    quantity1 = (usdt_balance * balance_margin) / last_price
    if quantity1 > 1:
        quantity2 = math.floor(quantity1)
    elif quantity_entry1 <1:
        quantity_entry2 = quantity1 
    quantity_entry1 =(usdt_balance * balance_margin) / entry_price
    if quantity_entry1 >1:
        quantity_entry2= math.floor(quantity_entry1)
    elif quantity_entry1 <1:
        quantity_entry2 = quantity1 
         

    print(quantity2)
    print(position)
    print(quantity_entry2)
    print(modified_string)
    print(stoploss)
    print(target)

    if modified_string not in bought_symbols:
        

        if position == 'BUY/LONG':
            if market_pos == 'MARKET':
                buyorder=client.futures_create_order(symbol=modified_string,side='BUY',type='MARKET',quantity=quantity2)     
                print(buyorder)
                buyorderlimit1=client.futures_create_order(symbol=modified_string,side='SELL',type='STOP_MARKET',stopPrice=stoploss,closePosition='true') 
                print(buyorderlimit1)
                
                
            elif market_pos == 'LIMIT':
                buyorder=client.futures_create_order(symbol=modified_string,side='BUY',type='LIMIT',quantity=quantity_entry2,price = entry_price,timeInForce='GTC')       
                print(buyorder)
                buyorderlimit1=client.futures_create_order(symbol=modified_string,side='SELL',type='STOP_MARKET',stopPrice=stoploss,closePosition='true') 
        
        elif position == 'SELL/SHORT':
            if market_pos == 'MARKET':
                buyorder=client.futures_create_order(symbol=modified_string,side='SELL',type='MARKET',quantity=quantity2)  
                print(buyorder)
                buyorderlimit=client.futures_create_order(symbol=modified_string,side='BUY',type='STOP_MARKET',stopPrice=stoploss,closePosition='true') 
              
            elif market_pos == 'LIMIT': 
                sellorder=client.futures_create_order(symbol=modified_string,side='SELL',type='LIMIT',quantity=quantity_entry2,price= entry_price,timeInForce='GTC')       
                print(sellorder)
                buyorderlimit=client.futures_create_order(symbol=modified_string,side='BUY',type='STOP_MARKET',stopPrice=stoploss,closePosition='true') 

 

        



        
        bought_symbols.append(modified_string)
    else:
        send_message_to_user(f"{modified_string} already bought.")
    # Add delay before checking for new messages again
    time.sleep(30)