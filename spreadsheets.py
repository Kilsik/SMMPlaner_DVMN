import base64
import pygsheets
import requests
import datetime
import os

import publish_on_vk


from docx_parser import DocumentParser
from globals import *


def get_time_to_post(date, time, n):
    '''
    Чтобы выбрать посты, которые надо публиковать сейчас или в ближайшие n минут
    '''

    time_interval = datetime.timedelta(minutes=int(n))
    if not date:
        return True
    if time:
        post_time = get_datetime(date, time)
    else:
        post_time = datetime.datetime.combine(datetime.date.today(),
            datetime.datetime.now().time()) + datetime.timedelta(minuts=1)
    current_time = datetime.datetime.now()
    delta = current_time-post_time
    zero_time = datetime.timedelta(microseconds=0)
    if zero_time <= (post_time - current_time) <= time_interval:
        return True
    else:
        return False


def get_rows_for_posts(all_table_rows):
    '''
    Отбираем то, что нужно опубликовать в ближайшие n минут. n лежит в
    globals.py
    '''
    rows_for_post = []
    for row in all_table_rows:
        tg = True if row[SMM_TG].value == 'TRUE' and row[SMM_TG].color == (None,
            None, None, None) and (not row[SMM_TG_POST_ID].value) else False
        vk = True if row[SMM_VK].value == 'TRUE' and row[SMM_VK].color == (None,
            None, None, None) and (not row[SMM_VK_POST_ID].value) else False
        ok = True if row[SMM_OK].value == 'TRUE' and row[SMM_OK].color == (None,
            None, None, None) and (not row[SMM_OK_POST_ID].value) else False
        deleted = False
        if row[SMM_DATE_ACTUAL_POST].color == (None, None, None,
                None) and row[SMM_DATE_ACTUAL_POST].value:
            delete_date = datetime.datetime.strptime(
                row[SMM_DATE_ACTUAL_POST].value, '%d.%m.%Y').date()
            deleted = (delete_date == datetime.date.today())
        need_time = True if deleted else get_time_to_post(row[SMM_DATE_POST].value,
            row[SMM_TIME_POST].value, n)
        if not row[SMM_GOOGLE_DOC].value and not row[SMM_GIF_LINK].value:
            continue
        elif row[SMM_GOOGLE_DOC].value or row[SMM_GIF_LINK].value:
            if (tg or vk or ok or deleted) and need_time:
                rows_for_post.append(row)
    return rows_for_post


def get_post_link(rows_for_post):
    for row in rows_for_post:
        post_link = row[SMM_GOOGLE_DOC].value
        return post_link


def download_file(link):
    file_id = link.split('/')[-2]
    url = f"https://docs.google.com/document/d/{file_id}/export?format=docx&id={file_id}"
    response = requests.get(url)
    file_name = 'post.docx'
    with open(file_name, 'wb') as f:
        f.write(response.content)
    return file_name


def get_parse_file(path):
    doc = DocumentParser(path)
    text = []
    filename = None
    for _type, item in doc.parse():
        if _type == 'paragraph':
            text.append(item['text'])
        elif _type == 'multipart':
            img_data = item[1]['image'].split(',')[1]
            filename = item[1]['filename']
            recovered = base64.b64decode(img_data)
            with open(filename, 'wb') as file:
                file.write(recovered)
    return ' '.join(text), filename


def get_datetime(date, time='00:00:00'):
    post_datetime = f"{date} {time}"
    return datetime.datetime.strptime(post_datetime, '%d.%m.%Y %H:%M:%S')


def update_post_id(row, post_id, network):
    row[globals()[f"SMM_{network}"]].color = (0, 1, 0, 0)
    row[globals()[f"SMM_{network}_POST_ID"]].value = post_id
    row[globals()[f"SMM_{network}"]].value = True


def fetch_gif_image(image_url):
    url = image_url
    filename = os.path.basename(image_url)
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def main():
    ''' А не собрать ли нам все тут? '''

    gc = pygsheets.authorize(service_file=service_file_spreadsheet)
    spreadsheet_smm = gc.open_by_key(spreadsheet_smm_key)
    worksheet_smm = spreadsheet_smm.sheet1

    min_row = 4
    max_row = worksheet_smm.rows

    all_table_rows = worksheet_smm.range(f'{min_row}:{max_row}', returnas='cell')
    rows_for_post = get_rows_for_posts(all_table_rows)
    print(rows_for_post)
    for row in rows_for_post:
        print(row)
        vk_flag = True if row[SMM_VK].value == 'TRUE' else False
        tg_flag = True if row[SMM_TG].value == 'TRUE' else False
        ok_flag = True if row[SMM_OK].value == 'TRUE' else False
        if vk_flag:
            if row[SMM_DATE_ACTUAL_POST].value:
                delete_date = datetime.datetime.strptime(
                    row[SMM_DATE_ACTUAL_POST].value, '%d.%m.%Y').date()
            else:
                delete_date = None
            if datetime.date.today() == delete_date:
                post_id = row[SMM_VK_POST_ID].value
                publish_on_vk.delete_vk_post(vk_token, vk_group_id, post_id,
                    vk_ver)
                row[SMM_DATE_ACTUAL_POST].color = (0, 1, 0, 0)
                row[SMM_VK_POST_ID].value = ''
                continue
            file_link = ''
            image_link = ''
            if row[SMM_GOOGLE_DOC].value:
                file_link = row[SMM_GOOGLE_DOC].value
            else:
                image_link = row[SMM_GIF_LINK].value
                print(image_link)
            if file_link:
                downloaded_doc = download_file(file_link)
                text, img_filename = get_parse_file(downloaded_doc)
                if row[SMM_VK].value == 'TRUE':
                    post_id = publish_on_vk.publish_to_vk(img_filename, text,
                        vk_token, vk_group_id, vk_ver)
            elif image_link:
                img_filename = fetch_gif_image(image_link)
                print(img_filename)
                if row[SMM_VK].value == 'TRUE':
                    post_id = publish_on_vk.publish_to_vk(img_filename, '',
                        vk_token, vk_group_id, vk_ver)
            update_post_id(row, post_id, 'VK')
        elif tg_flag:
            # Публикация в телеграмме
            pass
        elif ok_flag:
            # Публикация в одноклассниках
            pass
        if img_filename:
            os.remove(img_filename)
        if downloaded_doc:
            os.remove(downloaded_doc)





if __name__ == '__main__':
    main()