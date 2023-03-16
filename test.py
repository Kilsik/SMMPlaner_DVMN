import base64
import pygsheets
import requests


from docx_parser import DocumentParser
from globals import *


gc = pygsheets.authorize(service_file=service_file_spreadsheet)
spreadsheet_smm = gc.open_by_key(spreadsheet_smm_key)
worksheet_smm = spreadsheet_smm.sheet1

min_row = 4
max_row = worksheet_smm.rows

all_table_rows = worksheet_smm.range(f'{min_row}:{max_row}', returnas='cell')


def get_parse_docx(path):
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


def download_docx(link):
    file_id = link.split('/')[-2]
    url = f"https://docs.google.com/document/d/{file_id}/export?format=docx&id={file_id}"
    response = requests.get(url)
    with open('post.docx', 'wb') as f:
        f.write(response.content)


def get_rows_for_posts(all_table_rows):
    rows_for_post = []
    for row in all_table_rows:
        if not row[SMM_GOOGLE_DOC].value and not row[SMM_GIF_LINK].value:
            break
        elif row[SMM_GOOGLE_DOC].value:
            rows_for_post.append(row)
    return rows_for_post


def get_post_link(rows_for_post):
    for row in rows_for_post:
        post_link = row[SMM_GOOGLE_DOC].value
        return post_link


def get_update_row(row, post_id, network='TG'):
    row[globals()[f"SMM_{network}"]].color = (0, 1, 0, 0)
    row[globals()[f"SMM_{network}"]].value = False
    row[globals()[f"SMM_{network}_POST_ID"]].value = post_id





# if __name__ == '__main__':
