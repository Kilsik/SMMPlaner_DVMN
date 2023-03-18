import requests
import os
import hashlib

import json
from publish_on_vk import *
from main import *

OK_GROUP_ID = '70000002104498'
OK_LONG_ACCESS_TOKEN ='tkn1If99DtalJLkKXevvskUVIdgpZDyIhu0BwMoLNvi934umx3QOzRjgIpXQrqZL37v0u7'
OK_SECRET_SESSION_KEY = '29fc02c58a30e2ac74c7c91e51979a07'
OK_APPLICATION_KEY = 'CGCBMELGDIHBABABA'


def get_hash_signature(signature):
    return hashlib.md5(signature.encode('utf-8')).hexdigest()
def get_upload_url(app_key, token, session_key, group_id):
    signature = f'application_key={app_key}format=jsongid={group_id}method=photosV2.getUploadUrl{session_key}'
    sig = get_hash_signature(signature)
    params = {
        'application_key': app_key,
        'format': 'json',
        'gid': group_id,
        'method': 'photosV2.getUploadUrl',
        'sig': sig,
        'access_token': token,
        }
    ok_url = 'https://api.ok.ru/fb.do'
    response = requests.get(ok_url, params=params)
    response.raise_for_status()
    return response.json()['upload_url']

url_ok = get_upload_url(OK_APPLICATION_KEY, OK_LONG_ACCESS_TOKEN, OK_SECRET_SESSION_KEY, OK_GROUP_ID)


def upload_photo_ok(url, img_filename):
    ''' Загружаем картинку на сервер ok '''

    with open(img_filename, 'rb') as file:
        ok_file = {
            'filename': file,
            }
        response = requests.post(url, files=ok_file)
    response.raise_for_status()
    is_response_good(response)
    response_params = response.json()
    for key in response_params['photos']:
        photo_token = response_params['photos'][key]['token']
        return photo_token


photo_token = upload_photo_ok(url_ok, 'giphy.gif')
print(photo_token)
def publish_to_ok(app_key, token, session_key, group_id, photo_token, text):
    attachment = {
      "media": [
        {
          "type": "photo",
          "list": [
            {"id": photo_token}
          ]
        },
        {
          "type": "text",
          "text": text
        }
      ]
    }
    attachment_json = json.dumps(attachment)
    signature = f'application_key={app_key}attachment={attachment}format=jsongid={group_id}method=mediatopic.posttype=GROUP_THEME{session_key}'
    sig = get_hash_signature(signature)
    params = {
        'application_key': app_key,
        'attachment': attachment_json,
        'format': 'json',
        'gid': group_id,
        'method': 'mediatopic.post',
        'type': 'GROUP_THEME',
        'sig': sig,
        'access_token': token,
    }
    ok_url = 'https://api.ok.ru/fb.do'
    response = requests.get(ok_url, params=params)
    response.raise_for_status()
    return response.json()

print(publish_to_ok(OK_APPLICATION_KEY, OK_LONG_ACCESS_TOKEN, OK_SECRET_SESSION_KEY, OK_GROUP_ID, photo_token, 'Котэ тутэ'))
