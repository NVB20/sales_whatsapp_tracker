#sheets:
#B!time-stamp, C!name, D!phone, E!mail, F!source
# {timestamp, name, phone, mail, source, sales_person }
# load the data into google sheets last line in main table

import re
from datetime import datetime
import gspread
from src.sheets_connection import init_sheets_connection

# Connect to sheets and load data
def load_sales_persons(sheet_id: str):
    gc = init_sheets_connection()
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet("sales_persons")
    data = ws.get_all_records()

    name_to_phone = {}
    phone_to_name = {}
    
    for row in data:
        name = row.get("name", "").strip()
        phone = re.sub(r"[^\d]", "", str(row.get("phone", "")))  # Remove ALL non-digits
        if name and phone:
            name_to_phone[name] = phone
            phone_to_name[phone] = name
    
    return name_to_phone, phone_to_name


def is_phone_number(text: str) -> bool:
    """Check if text is a phone number"""
    cleaned = re.sub(r"[^\d+]", "", text)
    # Israeli phone numbers typically have 9-10 digits (excluding country code)
    return len(cleaned) >= 9 and any(c.isdigit() for c in text)


def normalize_phone(phone: str) -> str:
    """Normalize phone number to consistent format (digits only, no + sign)"""
    cleaned = re.sub(r"[^\d]", "", phone)
    # Remove leading + if present (already removed by regex, but being explicit)
    return cleaned


def parse_registration_message(msg: dict, name_to_phone: dict, phone_to_name: dict) -> dict:
    """
    Parse registration message and identify sales person
    
    Logic:
    1. If sender is a name (not phone), use it directly as sales_person
    2. If sender is a phone number, look it up in phone_to_name mapping
    3. Fallback: try to match the 'name' field from the message content
    """
    text = msg.get("text", "")
    sender = msg.get("sender", "").strip()

    # Normalize spacing
    text = text.replace("\n", " ").replace("  ", " ")

    # Extract fields from message content
    patterns = {
        "name": r"(?:שם[:\s]*)([^\s]+)",
        "phone": r"(?:טלפון[:\s]*)([\d\-+ ]+)",
        "mail": r"(?:מייל[:\s]*)([\w\.-]+@[\w\.-]+)",
        "source": r"(?:מקור[:\s]*)([^\s]+)",
    }

    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        extracted[key] = match.group(1).strip() if match else None

    # Clean phone number
    if extracted.get("phone"):
        extracted["phone"] = normalize_phone(extracted["phone"])

    # Parse timestamp
    raw_ts = msg.get("timestamp")
    try:
        ts = datetime.strptime(raw_ts, "%H:%M, %m/%d/%Y")
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    except:
        ts_str = raw_ts

    # Determine sales person
    sales_person = None
    
    # Check if sender is a phone number or a name
    if is_phone_number(sender):
        # Sender is a phone number - look it up
        normalized_sender = normalize_phone(sender)
        print(f"DEBUG: Normalized sender phone: {normalized_sender}")
        print(f"DEBUG: Available phones in mapping: {list(phone_to_name.keys())}")
        sales_person = phone_to_name.get(normalized_sender)
        print(f"DEBUG: Found sales_person: {sales_person}")
        
        # Fallback: try matching by name from message content
        if not sales_person and extracted.get("name") in name_to_phone:
            sales_person = extracted.get("name")
            print(f"DEBUG: Used fallback - matched by name: {sales_person}")
    else:
        # Sender is a name - use it directly
        sales_person = sender
        print(f"DEBUG: Sender is a name, using directly: {sales_person}")

    return {
        "timestamp": ts_str,
        "name": extracted.get("name"),
        "phone": extracted.get("phone"),
        "mail": extracted.get("mail"),
        "source": extracted.get("source"),
        "sales_person": sales_person,
    }


def append_to_main_table(sheet_id: str, parsed_data: dict):
    """Append parsed registration data to main table"""
    gc = init_sheets_connection()
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet("main")  # Adjust worksheet name as needed
    
    # Prepare row data matching columns: B!time-stamp, C!name, D!phone, E!mail, F!source
    row = [
        parsed_data.get("timestamp", ""),
        parsed_data.get("name", ""),
        parsed_data.get("phone", ""),
        parsed_data.get("mail", ""),
        parsed_data.get("source", ""),
        parsed_data.get("sales_person", ""),
    ]
    
    ws.append_row(row)
    print(f"✓ Added registration to main table: {parsed_data.get('name')} (Sales: {parsed_data.get('sales_person')})")
