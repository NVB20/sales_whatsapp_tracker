import os
from src.etl.extract import open_whatsapp
from src.etl.transform import load_sales_persons, parse_registration_message
from src.etl.load import append_lead

sheet_id = os.getenv("SHEET_ID")

def run_etl_pipeline():

    messages = open_whatsapp()
    messages = transform_messages(messages, sheet_id)
    append_lead(messages)


def transform_messages(messages, sheet_id):
    name_to_phone, phone_to_name = load_sales_persons(sheet_id)
    
    for msg in messages:
        parsed = parse_registration_message(msg, name_to_phone, phone_to_name)
    
    return parsed
