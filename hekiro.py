import csv
import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

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
    import re
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

def update_sheet(service, spreadsheet_id, sheet_name, csv_file):
    # Read CSV file
    csv_rows = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                csv_rows.append(row)

    # Fetch all student names from column B (starting at row 3, after headers)
    DATA_START_ROW = 3
    name_range = f"'{sheet_name}'!B{DATA_START_ROW}:B"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=name_range
    ).execute()
    sheet_names = [row[0] if row else '' for row in result.get('values', [])]

    # Build a map from name -> row number (1-indexed in the sheet)
    name_to_row = {}
    for i, name in enumerate(sheet_names):
        if name:
            name_to_row[name] = DATA_START_ROW + i

    # For each CSV entry, update 所持状況 and レアリティ
    updates = []
    for row in csv_rows:
        name = row[0]
        if name in name_to_row:
            row_num = name_to_row[name]
            updates.append({
                'range': f"'{sheet_name}'!A{row_num}",
                'values': [['TRUE']],
            })
            if len(row) > 1 and row[1]:
                updates.append({
                    'range': f"'{sheet_name}'!C{row_num}",
                    'values': [[row[1]]],
                })
            if len(row) > 2 and row[2]:
                updates.append({
                    'range': f"'{sheet_name}'!E{row_num}",
                    'values': [[row[2]]],
                })
            # Skill levels: CSV[3..6] -> columns G,H,I,J
            if len(row) > 6:
                updates.append({
                    'range': f"'{sheet_name}'!G{row_num}:J{row_num}",
                    'values': [[row[3], row[4], row[5], row[6]]],
                })
            # Equipment levels: CSV[7..9] -> columns L,M,N (empty -> なし)
            if len(row) > 9:
                equips = [v if v else 'なし' for v in row[7:10]]
                updates.append({
                    'range': f"'{sheet_name}'!L{row_num}:N{row_num}",
                    'values': [equips],
                })
        else:
            print(f"Warning: '{name}' not found in sheet")

    # Batch update
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

    # Verify write access by reading spreadsheet metadata
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    print(f"Successfully accessed spreadsheet: {spreadsheet['properties']['title']}")

    # Find sheet name by gid
    sheet_name = None
    for sheet in spreadsheet['sheets']:
        props = sheet['properties']
        if gid is not None and str(props['sheetId']) == gid:
            sheet_name = props['title']
            break
    if sheet_name:
        print(f"Target sheet: {sheet_name} (gid={gid})")
    else:
        print(f"Warning: Could not find sheet with gid={gid}, will use first sheet")

    update_sheet(service, spreadsheet_id, sheet_name, csv_file)

if __name__ == '__main__':
    main()
