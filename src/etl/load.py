import os
from dotenv import load_dotenv
from src.sheets_connection import init_sheets_connection

# Load environment variables
load_dotenv()

#connect to google sheets
client = init_sheets_connection()

SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME =os.getenv("SHEET_NAME")

sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)


def append_lead(sheet, data):

    # Build the row according to your sheet structure
    row = [
        False,                      # A: checkbox
        data.get("timestamp", ""),  # B: timestamp
        data.get("name", ""),       # C: name
        data.get("phone", ""),      # D: phone
        data.get("mail", ""),       # E: mail
        data.get("source", ""),     # F: source
        data.get("sales_person",""),# G: sales_person
        "", "", "", "",             # H–K merged comments fields
        "",                         # L: additional comments
        ""                          # M: yes/no
    ]

    #Find last row based ONLY on timestamp column (B)
    col_b = sheet.col_values(2)  # column index 2 = B
    last_row = len(col_b)        # last row with timestamp
    insert_row = last_row + 1

    #Insert the row in the correct location
    sheet.update(
        f"A{insert_row}",
        [row],
        value_input_option="USER_ENTERED"
    )

    print(f"Lead added successfully at row {insert_row}!")



append_lead(sheet, message_data)
