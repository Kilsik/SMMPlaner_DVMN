from asyncio import run


import telegram
import pygsheets


from spreadsheets import get_rows_for_posts, download_file, get_parse_file, get_update_row
from publish_on_tg import post_telegram
from globals import *



def main():

    gc = pygsheets.authorize(service_file=service_file_spreadsheet)
    spreadsheet_smm = gc.open_by_key(spreadsheet_smm_key)
    worksheet_smm = spreadsheet_smm.sheet1

    min_row = 4
    max_row = worksheet_smm.rows
    all_table_rows = worksheet_smm.range(f'{min_row}:{max_row}', returnas='cell')
    rows_for_post = get_rows_for_posts(all_table_rows)
    for row in rows_for_post:
        file_link = row[SMM_GOOGLE_DOC].value
        if file_link:
            downloaded_doc = download_file(file_link)
            text, image = get_parse_file(downloaded_doc)
            if row[SMM_TG].value:
                field_id = row[SMM_TG_POST_ID].label
                bot = telegram.Bot(token=telegram_token)
                post_id = run(post_telegram(telegram_chat_id, bot, text, image))
                get_update_row(worksheet_smm, post_id)


if __name__ == '__main__':
    main()