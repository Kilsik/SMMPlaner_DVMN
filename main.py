import datetime
import os
import time
import re
from asyncio import run


import pygsheets
import requests
import schedule
import telegram

from publish_on_vk import publish_to_vk, delete_vk_post
from publish_on_ok import publish_to_ok, delete_ok_post

from dotenv import load_dotenv


from spreadsheets import (get_rows_for_posts, get_file, get_parsed_file, update_post_id, get_time_to_post,
                          SMM_TG, SMM_OK, SMM_VK, SMM_DATE_POST, SMM_TIME_POST, SMM_DATE_ACTUAL_POST, SMM_GOOGLE_DOC,
                          SMM_IMAGE_LINK, SMM_TG_POST_ID, SMM_VK_POST_ID, SMM_OK_POST_ID, SMM_DELETE_POST)
from publish_on_tg import send_post, send_animation_image, delete_tg_post


def fetch_gif_image(image_url):
    url = image_url
    filename = os.path.basename(image_url)
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def format_text(text):
    formated_txt = re.sub(' +', ' ', text)
    formated_txt = formated_txt.replace(' "', ' «')
    formated_txt = formated_txt.replace('" ', '» ')
    formated_txt = formated_txt.replace(' - ', ' – ')
    return formated_txt


def get_datetime(date, time='00:00:00'):
    post_datetime = f"{date} {time}"
    return datetime.datetime.strptime(post_datetime, '%d.%m.%Y %H:%M:%S')


def main():
    load_dotenv()
    # Telegram Secret
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token=telegram_token)
    # vkontakte secret
    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    vk_ver = '5.131'
    # odnoklasniki secret
    ok_app_key = os.getenv('OK_APPLICATION_KEY')
    ok_access_token = os.getenv('OK_LONG_ACCESS_TOKEN')
    ok_sesion_key = os.getenv('OK_SECRET_SESSION_KEY')
    ok_group_id = os.getenv('OK_GROUP_ID')
    # spreadsheet secret
    service_file_spreadsheet = os.getenv('SERVICE_FILE_SPREADSHEET')
    spreadsheet_smm_key = os.getenv('SPREADSHEET_SMM_KEY')

    gc = pygsheets.authorize(service_file=service_file_spreadsheet)
    spreadsheet_smm = gc.open_by_key(spreadsheet_smm_key)
    worksheet_smm = spreadsheet_smm.sheet1
    min_row = 4
    max_row = worksheet_smm.rows
    all_table_rows = worksheet_smm.range(f'{min_row}:{max_row}', returnas='cell')
    rows_for_post, rows_for_delete = get_rows_for_posts(all_table_rows)
    date_now = datetime.datetime.now()
    today = date_now.date().strftime('%d.%m.%Y')
    time_now = date_now.strftime('%H:%M:00')

    for row in rows_for_post:
        if not row[SMM_DATE_POST].value:
            date_post = today
        else:
            date_post = row[SMM_DATE_POST].value
        if not row[SMM_TIME_POST].value:
            time_post = time_now
        else:
            time_post = row[SMM_TIME_POST].value
        datetime_post = get_datetime(date_post, time_post)
        if datetime_post > date_now:
            continue
        text = ''
        image = ''
        gif_image = ''
        if row[SMM_GOOGLE_DOC].value:
            file_link = row[SMM_GOOGLE_DOC].value
            downloaded_doc = get_file(file_link)
            text, image = get_parsed_file(downloaded_doc)
        if row[SMM_GOOGLE_DOC].value and row[SMM_IMAGE_LINK].value:
            image_link = row[SMM_IMAGE_LINK].value
            gif_image = fetch_gif_image(image_link)
        elif row[SMM_IMAGE_LINK].value:
            image_link = row[SMM_IMAGE_LINK].value
            gif_image = fetch_gif_image(image_link)
        if row[SMM_TG].value != 'FALSE' and row[SMM_TG_POST_ID].value == '':
            bot = telegram.Bot(token=telegram_token)
            if (text and gif_image) or gif_image:
                post_id = run(send_animation_image(telegram_chat_id, bot, gif_image, text))
                update_post_id(row, post_id, network='TG')
            else:
                post_id = run(send_post(telegram_chat_id, bot, text, image))
                update_post_id(row, post_id, network='TG')
        if gif_image:
            os.remove(image)
            image = gif_image
        if row[SMM_VK].value != 'FALSE' and row[SMM_VK_POST_ID].value == '':
            post_id = publish_to_vk(image, text, vk_token,
                                    vk_group_id, vk_ver)
            update_post_id(row, post_id, network='VK')
        if row[SMM_OK].value != 'FALSE' and row[SMM_OK_POST_ID].value == '':
            post_id = publish_to_ok(ok_app_key, ok_access_token, ok_sesion_key, ok_group_id, text, image)
            update_post_id(row, post_id, network='OK')
        if image:
            os.remove(image)
    for row in rows_for_delete:
        delete_date = row[SMM_DATE_ACTUAL_POST].value
        if delete_date > today:
            continue
        try:
            if row[SMM_VK_POST_ID].value:
                post_id = row[SMM_VK_POST_ID].value
                delete_vk_post(vk_token, vk_group_id, post_id, vk_ver)
            if row[SMM_TG_POST_ID].value:
                bot = telegram.Bot(token=telegram_token)
                post_id = row[SMM_TG_POST_ID].value
                run(delete_tg_post(telegram_chat_id, bot, post_id))
            if row[SMM_OK_POST_ID].value:
                post_id = row[SMM_OK_POST_ID].value
                delete_ok_post(ok_app_key, ok_access_token, ok_sesion_key, post_id)
            row[SMM_DELETE_POST].value = True
        except:
            pass


if __name__ == '__main__':
    n = os.getenv('TIME_INTERVAL')
    schedule.every(10).seconds.do(main)
    while True:
        print(schedule.next_run())
        schedule.run_pending()
        time.sleep(10)
