import datetime
import os
import time
from asyncio import run


import pygsheets
import requests
import schedule
import telegram
from dotenv import load_dotenv


from spreadsheets import (get_rows_for_posts, get_file, get_parsed_file, update_post_id, get_time_to_post, get_datetime,
                          SMM_TG, SMM_OK, SMM_VK, SMM_DATE_POST, SMM_TIME_POST, SMM_DATE_ACTUAL_POST, SMM_GOOGLE_DOC,
                          SMM_IMAGE_LINK, SMM_TG_POST_ID, SMM_VK_POST_ID, SMM_OK_POST_ID, SMM_DELETE_POST)
from publish_on_tg import send_post, send_animation_image


def fetch_gif_image(image_url):
    url = image_url
    filename = os.path.basename(image_url)
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def main():
    load_dotenv()
    # Telegram Secret
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = telegram.Bot(token=telegram_token)
    # vkontakte secret
    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    vk_ver = '5.131'
    # odnoklasniki secret

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
    for row in rows_for_post:
        if not row[SMM_DATE_POST].value and not row[SMM_TIME_POST].value:
            date = datetime.datetime.now()
            today = date.date().strftime('%d.%m.%Y')
            hour = date.strftime('%H:%M:00')
            date_post = row[SMM_DATE_POST].value
            time_post = row[SMM_TIME_POST].value
            if date_post != today or time_post > hour:
                continue
        file_link = ''
        image_link = ''
        if row[SMM_GOOGLE_DOC].value:
            file_link = row[SMM_GOOGLE_DOC].value
        else:
            image_link = row[SMM_IMAGE_LINK].value
        if file_link:
            downloaded_doc = get_file(file_link)
            text, image = get_parsed_file(downloaded_doc)
            if row[SMM_TG].value == 'TRUE' and row[SMM_TG_POST_ID].value == '':
                post_id = run(send_post(telegram_chat_id, bot, text, image))
                update_post_id(row, post_id, network='TG')
            if row[SMM_VK].value == 'TRUE' and row[SMM_VK_POST_ID].value == '':
                pass
            if row[SMM_OK].value == 'TRUE' and row[SMM_OK_POST_ID].value == '':
                pass
        elif image_link:
            image = fetch_gif_image(image_link)
            bot = telegram.Bot(token=telegram_token)
            if row[SMM_TG].value  == 'TRUE' and row[SMM_TG_POST_ID].value == '':
                post_id = run(send_animation_image(telegram_chat_id, bot, image))
                update_post_id(row, post_id, network='TG')
            if row[SMM_VK].value == 'TRUE' and row[SMM_VK_POST_ID].value == '':
                pass
            if row[SMM_OK].value == 'TRUE' and row[SMM_OK_POST_ID].value == '':
                pass



if __name__ == '__main__':
    n = os.getenv('TIME_INTERVAL')
    schedule.every(n).minutes.do(main)
    while True:
        print(schedule.next_run())
        schedule.run_pending()
        time.sleep(60)
