# SMM Planer

`SMM planer` – this code will help you to organize and make post by the date and time in such social 
networks and messengers as: `Vkontakte`, `Odnoklassniki`, `Telegram`. 
Create and fill in Google Sheets as in an  
<a href='https://docs.google.com/spreadsheets/d/1Fc8GpOupbms651ikJo6y0esBFSqlVWCxeTmP-YgO5qs/'>example</a>.


## Setup

Python3 have to be already installed. Then use pip (or pip3, there is a contravention with Python2) to install dependencies:

### 1. Install requirements
```bash
pip install -r requirements.txt
```

### 2. Create `.env` and place your secrets accordingly

```bash
TELEGRAM_TOKEN=place_your_token_here
TELEGRAM_CHAT_ID=place_your_chat_id_here
VK_ACCESS_TOKEN=place_your_token_here
VK_GROUP_ID=place_your_group_id_here
OK_APPLICATION_KEY=place_your_application_key_here
OK_LONG_ACCESS_TOKEN=place_your_token_here
OK_SECRET_SESSION_KEY=place_your_session_key_here
OK_GROUP_ID=place_your_group_id_here
SERVICE_FILE_SPREADSHEET='place_your_authorize_file.json'
SPREADSHEET_SMM_KEY='place_your_spreadsheet_key'
TIME_INTERVAL=60
```

#### Receiving keys from `Google Sheets API`
<ol>
  <li>Follow this <a href='https://developers.google.com/sheets/api/quickstart/python'>link</a>.</li>
  <li>Push the button `Enable the Google Sheets API` to download the keys to your account in `Google`.</li>
  <li>Put in data in the folder of the project.</li> 
</ol>

#### Receiving keys from `OK API`
<ol>
  <li>Follow this <a href='https://apiok.ru/dev/'>link</a>.</li>
</ol>

#### Receiving keys from `VK API`
<ol>
  <li>Follow this <a href='https://dev.vk.com/reference'>link</a>.</li>
</ol>

#### Receiving keys from `Telegram API`
<ol>
  <li>Follow this <a href='https://core.telegram.org/api'>link</a>.</li>
</ol>

#### How to connect `Google Sheets `
<ol>
  <li>Open the website, `Google Sheets`.</li>
  <li>In the address bar, there will be a link of this type: `https://docs.google.com/spreadsheets/d/1Fc8GpOupbms651ikJo6y0esBFSqlVWCxeTmP-YgO5qs`.</li>
  <li>`1Fc8GpOupbms651ikJo6y0esBFSqlVWCxeTmP-YgO5qs` - this is your `SPREADSHEET_SMM_KEY`</li>
</ol>

#### Receiving keys from `Authorizing pygsheets`
<ol>
  <li>Follow this <a href='https://pygsheets.readthedocs.io/en/stable/authorization.html'>link</a>.</li>
</ol>


### 3. Run

```bash
python main.py
```
