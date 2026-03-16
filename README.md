# students-ocr

OCR screenshots of students

## Setup

```
$ pip3.10 install -r requirements.txt
```

## Run

### OCR

The size of input screenshots must be 1280x720.

```
$ python3.10 ocr.py *.png
アイリ(バンド),★★★★★☆☆,76,3,5,5,5,7,7,5,,21,,,
アイリ,★★★★★☆☆☆☆,20,1,5,5,5,1,1,1,,21,,,
アオバ,★★★★★☆,90,5,9,9,9,10,10,10,,12,,,
アカネ,★★★★★☆☆☆☆,90,5,10,7,7,10,9,9,,24,,,
アカネ(バニーガール),★★★★★☆☆☆,20,1,5,5,5,1,1,1,,22,,,
アカリ,★★★★★☆☆☆☆,57,3,5,5,5,1,1,1,,23,,,
アカリ(正月),★★★★★☆☆☆,90,5,10,7,10,10,10,9,,23,,,
アコ,★★★★★☆☆☆☆,90,5,10,10,10,10,10,10,,46,,25,25
...
```

### Google Sheets

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
