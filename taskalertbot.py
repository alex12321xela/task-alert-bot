from flask import Flask, request

import html
import re
import json
import time
import os.path
import requests
import sys
from datetime import datetime
import urllib3

urllib3.disable_warnings()

settings = {}
#tg bot
settings['token'] = 'token' #tg bot token
settings['chat_id'] = ['id'] 
#siem data
settings['core_url'] = 'url'   #https://maxpatrolsiemaddress
settings['client_secret'] = 'token' # from corecfg get



def parse_response(r):
    msg = ''
    taskName=''
    message=''
    for dataTaskInfo in r['dataTaskInfo']: 
        taskName = dataTaskInfo['taskName']
        for events in dataTaskInfo['events']: 
            message = events['message']
    
    msg += taskName + ': ' + message
    return msg


def send_tg_msg(msg):
    requests.post("https://api.telegram.org/bot" + settings['token'] + "/sendMessage", data = {'chat_id': settings['chat_id'], 'text':msg})


def authenticate():
    host = settings['core_url'] + ':3334/connect/token'
    auth_info = {'client_id':'mpx', 'client_secret': settings['client_secret'], 'grant_type':'client_credentials', 'response_type':'code id_token', 'scope':'authorization mpx.api ptkb.api'}
    head = {'Content-Type' : 'application/x-www-form-urlencoded'}
    
    r = requests.post(host, auth_info, verify=False)
    return r.json()["access_token"]
    

app = Flask(__name__)
@app.route('/', methods=['POST'])
def result():
    resive = request.json
    if(resive['notification_type'] == 'test'):  send_tg_msg('Получено тестовое уведомление')
    elif(resive['notification_type'] == 'event'):
        headers = {"Authorization": "Bearer "+ authenticate()}   
        r = requests.get(resive['uri'],headers=headers,verify=False)
        send_tg_msg(parse_response(r.json()))
    else: 
        send_tg_msg('Получен необрабатываемый запрос')
        send_tg_msg(resive)
    
    
    return 'Ok' 






if __name__ == '__main__':

    app.run(host='0.0.0.0',port=80)
