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
    for _type, item in doc.parse():
        try:
            text.append(item['text'])
        except TypeError:
            img_data = item[1]['image']
            filename = item[1]['filename']
            text_img = img_data.split(',')[1]
            recovered = base64.b64decode(text_img)
            with open(filename, 'wb') as file:
                file.write(recovered)
    return ' '.join(text)

print(get_parse_docx('post.docx'))
def upload_docx(link):
    file_id = link.split('/')[-2]
    url = f"https://docs.google.com/document/d/{file_id}/export?format=docx&id={file_id}"
    response = requests.get(url)
    with open('post.docx', 'wb') as f:
        f.write(response.content)


def get_rows_for_posts(all_table_rows):
    rows_for_post = []
    for rows in all_table_rows:
        if rows[SMM_GOOGLE_DOC].value:
            rows_for_post.append(rows)
    return rows_for_post


def get_post_link(rows_for_post):
    for row in rows_for_post:
        post_link = row[SMM_GOOGLE_DOC].value
        return post_link


    # rows[SMM_TG].color = (1, 0, 0, 0)     # красим ячейки
    # rows[SMM_TG].value = False            # присваеваем значение

# if __name__ == '__main__':
