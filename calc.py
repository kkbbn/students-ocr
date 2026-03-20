import csv
import os
import re
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

EXPECTED_SHEET_NAME = 'ﾃﾞｰﾀｼｰﾄ'

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: {CREDENTIALS_FILE} not found.")
                print("Download OAuth 2.0 Client ID credentials from Google Cloud Console")
                print("and save them as credentials.json in this directory.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"Credentials saved to {TOKEN_FILE}")
    return creds

def parse_spreadsheet_url(url):
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        print(f"Error: Could not parse spreadsheet ID from URL: {url}")
        sys.exit(1)
    spreadsheet_id = match.group(1)
    gid = None
    gid_match = re.search(r'gid=(\d+)', url)
    if gid_match:
        gid = gid_match.group(1)
    return spreadsheet_id, gid

def normalize_name(name):
    """Convert half-width parens to full-width for matching."""
    return name.replace('(', '\uff08').replace(')', '\uff09')

def parse_stars(star_str):
    """Count ★ and ☆ in the star string."""
    return star_str.count('\u2605'), star_str.count('\u2606')

def update_sheet(service, spreadsheet_id, sheet_name, csv_file):
    csv_rows = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                csv_rows.append(row)

    # Fetch student names from column B
    DATA_START_ROW = 7
    name_range = f"'{sheet_name}'!B{DATA_START_ROW}:B"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=name_range
    ).execute()
    sheet_names = [row[0] if row else '' for row in result.get('values', [])]

    name_to_row = {}
    for i, name in enumerate(sheet_names):
        if name:
            name_to_row[name] = DATA_START_ROW + i

    # CSV columns:
    # [0] name, [1] stars (★☆), [2] 固有Lv, [3] level, [4] EX skill,
    # [5-7] skills (NS/PS/SS), [8-10] equipment, [11] 愛用品,
    # [12] 絆ランク, [13-15] WB (HP/攻撃/治癒)
    #
    # 現在 columns (J,L,N,P,R,T,V,X,Z,AB,AD,AF,AH,AJ,AL,AN):
    # J=Lv, L=★, N=固有(☆), P=固有Lv, R=EX, T=NS, V=PS, X=SS,
    # Z=装備1, AB=装備2, AD=装備3, AF=絆ランク, AH=愛用品,
    # AJ=HP開放, AL=攻撃開放, AN=治癒開放

    updates = []
    for row in csv_rows:
        csv_name = row[0]
        normalized_name = normalize_name(csv_name)

        if csv_name in name_to_row:
            row_num = name_to_row[csv_name]
        elif normalized_name in name_to_row:
            row_num = name_to_row[normalized_name]
        else:
            print(f"Warning: '{csv_name}' not found in sheet")
            continue

        # J: Level (CSV[3])
        if len(row) > 3 and row[3]:
            updates.append({
                'range': f"'{sheet_name}'!J{row_num}",
                'values': [[row[3]]],
            })

        # L: ★ count, N: ☆ count (from CSV[1])
        if len(row) > 1 and row[1]:
            star_count, unique_count = parse_stars(row[1])
            updates.append({
                'range': f"'{sheet_name}'!L{row_num}",
                'values': [[star_count]],
            })
            updates.append({
                'range': f"'{sheet_name}'!N{row_num}",
                'values': [[unique_count]],
            })

        # P: CSV[2]
        if len(row) > 2 and row[2]:
            updates.append({
                'range': f"'{sheet_name}'!P{row_num}",
                'values': [[row[2]]],
            })

        # R: EX skill (CSV[4])
        if len(row) > 4 and row[4]:
            updates.append({
                'range': f"'{sheet_name}'!R{row_num}",
                'values': [[row[4]]],
            })

        # T, V, X: Skills (CSV[5-7])
        for col, idx in [('T', 5), ('V', 6), ('X', 7)]:
            if len(row) > idx and row[idx]:
                updates.append({
                    'range': f"'{sheet_name}'!{col}{row_num}",
                    'values': [[row[idx]]],
                })

        # Z, AB, AD: Equipment (CSV[8-10])
        for col, idx in [('Z', 8), ('AB', 9), ('AD', 10)]:
            if len(row) > idx and row[idx]:
                updates.append({
                    'range': f"'{sheet_name}'!{col}{row_num}",
                    'values': [[row[idx]]],
                })

        # AF: 絆ランク (CSV[12])
        if len(row) > 12 and row[12]:
            updates.append({
                'range': f"'{sheet_name}'!AF{row_num}",
                'values': [[row[12]]],
            })

        # AH: 愛用品 (CSV[11])
        if len(row) > 11 and row[11]:
            updates.append({
                'range': f"'{sheet_name}'!AH{row_num}",
                'values': [[row[11]]],
            })

        # AJ, AL, AN: WB (CSV[13-15])
        for col, idx in [('AJ', 13), ('AL', 14), ('AN', 15)]:
            if len(row) > idx and row[idx]:
                updates.append({
                    'range': f"'{sheet_name}'!{col}{row_num}",
                    'values': [[row[idx]]],
                })

    if updates:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': updates}
        ).execute()
        print(f"Updated {len(updates)} cells.")
    else:
        print("No updates to make.")

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <csv_file> <spreadsheet_url>")
        sys.exit(1)

    csv_file = sys.argv[1]
    spreadsheet_url = sys.argv[2]
    spreadsheet_id, gid = parse_spreadsheet_url(spreadsheet_url)

    creds = authenticate()
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    print(f"Successfully accessed spreadsheet: {spreadsheet['properties']['title']}")

    sheet_name = None
    for sheet in spreadsheet['sheets']:
        props = sheet['properties']
        if gid is not None and str(props['sheetId']) == gid:
            sheet_name = props['title']
            break
    if sheet_name:
        print(f"Target sheet: {sheet_name} (gid={gid})")
    else:
        print(f"Error: Could not find sheet with gid={gid}")
        sys.exit(1)

    if sheet_name != EXPECTED_SHEET_NAME:
        print(f"Error: Expected sheet name '{EXPECTED_SHEET_NAME}', but got '{sheet_name}'")
        sys.exit(1)

    update_sheet(service, spreadsheet_id, sheet_name, csv_file)

if __name__ == '__main__':
    main()
