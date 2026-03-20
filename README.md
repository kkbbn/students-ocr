# students-ocr

生徒のスクリーンショットから育成状況を書き起こすツール

## 書き起こし

### セットアップ

Python 3 と依存パッケージをインストールしてください。Python 3.10 で動作を確認しています。

```
$ pip3 install -r requirements.txt
```

### 実行

解像度 1280x720 の環境で生徒の基本情報のスクリーンショットを撮り、ocr.py に読み込ませてください。
解像度を 1280x720 に設定したMuMu Playerで動作を確認しています。

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

## Google スプレッドシート

### セットアップ

1. https://console.cloud.google.com/ にアクセス
2. プロジェクトを作成または選択
3. Google Sheets API を有効にする（APIs & Services > Library）

OAuth 同意画面の設定（APIs & Services > OAuth consent screen）：

1. Get Started をクリック
2. アプリ名：任意（例：「students-ocr」）
3. ユーザーサポートメール：自分のメールアドレスを選択
4. 対象：External を選択
5. 連絡先情報：メールアドレスを入力
6. 完了 — 同意して作成
7. 左サイドバーの Audience に移動 > Test users の下で Add users をクリックし、自分の Google アカウントのメールアドレスを追加

OAuth クライアント ID の作成（APIs & Services > Credentials）：

1. Create Credentials > OAuth client ID をクリック
2. アプリケーションの種類：デスクトップアプリ
3. 名前：任意（例：「students-ocr」）
4. Create をクリック
5. Download JSON をクリックし、このプロジェクトディレクトリに credentials.json として保存

### 更新：ブルアカ育成計算機

[ブルアカ育成計算機](https://x.com/makoto_149/status/2020066203759440190) を更新できます。

スプレッドシートを開き、`ﾃﾞｰﾀｼｰﾄ` シートをクリックして URL をコピーします。以下のように `calc.py` に渡してください：

```
$ python3 ocr.py *.png > output.csv
$ python3 calc.py output.csv 'https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit?gid=[GID]'
```

### 更新：育成状況確認シート

壁炉の家・暖炉の家で使用している育成状況確認シートを更新できます。

スプレッドシートを開き、`育成状況確認` シートをクリックして URL をコピーします。以下のように `hekiro.py` に渡してください：

```
$ python3 ocr.py *.png > output.csv
$ python3 hekiro.py output.csv 'https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit?gid=[GID]'
```
