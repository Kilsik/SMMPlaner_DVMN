from environs import Env


env = Env()
env.read_env()
service_file_spreadsheet = env('SERVICE_FILE_SPREADSHEET')
spreadsheet_smm_key = env('SPREADSHEET_SMM_KEY')
vk_token = env('VK_ACCESS_TOKEN')
vk_group_id = env('VK_GROUP_ID')
vk_ver = '5.131'




# cell groups
SMM_TG = 0
SMM_OK = 1
SMM_VK = 2
SMM_DATE_POST = 3
SMM_TIME_POST = 4
SMM_DATE_ACTUAL_POST = 5
SMM_GOOGLE_DOC = 6
SMM_GIF_LINK = 7
SMM_TG_POST_ID = 8
SMM_VK_POST_ID = 9
SMM_OK_POST_ID = 10
