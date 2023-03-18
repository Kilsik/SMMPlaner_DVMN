
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
