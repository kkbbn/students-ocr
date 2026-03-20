# students-ocr

OCR screenshots of students

## OCR

### Setup

Install Python 3 and dependencies. The scripts are tested with Python 3.10.

```
$ pip3 install -r requirements.txt
```

### Run

The size of input screenshots must be 1280x720.

```
$ python3 ocr.py *.png
アイリ(バンド),★★★★★☆☆,1,76,3,5,5,5,7,7,5,,21,,,
アイリ,★★★★★☆☆☆☆,1,20,1,5,5,5,1,1,1,,21,,,
アオバ,★★★★★☆,30,90,5,9,9,9,10,10,10,,12,,,
アカネ,★★★★★☆☆☆☆,50,90,5,10,7,7,10,9,9,,24,,,
アカネ(バニーガール),★★★★★☆☆☆,1,20,1,5,5,5,1,1,1,,22,,,
アカリ,★★★★★☆☆☆☆,1,57,3,5,5,5,1,1,1,,23,,,
アカリ(正月),★★★★★☆☆☆,40,90,5,10,7,10,10,10,9,,23,,,
アコ,★★★★★☆☆☆☆,60,90,5,10,10,10,10,10,10,,46,,25,25
...
```

## Google Sheets

### Setup

1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable the Google Sheets API (APIs & Services > Library)

Configure OAuth Consent Screen (APIs & Services > OAuth consent screen):

1. Click Get Started
2. App name: anything (e.g. "students-ocr")
3. User support email: select your email
4. Audience: select External
5. Contact Information: enter your email
6. Finish — agree and create
7. Go to Audience (left sidebar) > under Test users, click Add users and add your own Google account email

Create OAuth Client ID (APIs & Services > Credentials):

1. Click Create Credentials > OAuth client ID
2. Application type: Desktop app
3. Name: anything (e.g. "students-ocr")
4. Click Create
5. Click Download JSON and save it as credentials.json in this project directory

### Update: ブルアカ育成計算機

You can update [ブルアカ育成計算機](https://x.com/makoto_149/status/2020066203759440190).

Open a spreadsheet, click the `ﾃﾞｰﾀｼｰﾄ`  sheet, and copy the URL. Give it to `calc.py` as follows:

```
$ python3 ocr.py *.png > output.csv
$ python3 calc.py output.csv 'https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit?gid=[GID]'
```

### Update: 育成状況確認シート

You can update 育成状況確認シート used by 壁炉の家・暖炉の家.

Open a spreadsheet, click the `育成状況確認` sheet, and copy the URL. Give it to `hekiro.py` as follows:

```
$ python3 ocr.py *.png > output.csv
$ python3 hekiro.py output.csv 'https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit?gid=[GID]'
```
