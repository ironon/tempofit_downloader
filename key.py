import requests
import datetime
import json

def get_new_key():
    url = "https://api.trainwithpivot.com/oauth/token"
    payload = "grant_type=password&username=david.allan.macpherson%40gmail.com&password=GrizzIron5%24&client_id=aad0635b-0f49-4a8a-bf0f-b7cb09d8b9a8"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "insomnia/9.1.0"
    }


    response = requests.request("POST", url, data=payload, headers=headers)
    data = response.json()
    return data['access_token']

def get_key():
    ## open creds.json, if the expires_at unix time is more than 24 hours ago, get a new key
    creds = json.load(open('creds.json'))
    if datetime.datetime.now() > creds['expires_at']:
        creds['access_token'] = get_new_key()
        creds['expires_at'] = datetime.datetime.now() + datetime.timedelta(seconds=3600)
        json.dump(creds, open('creds.json', 'w'))
    return creds['access_token']
