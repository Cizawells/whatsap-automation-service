import schedule
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests
import os
from dotenv import load_dotenv

load_dotenv()


API_VERSION = os.getenv("API_VERSION")
WHATSAPP_BUSINESS_PHONE_NUMBER_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_NUMBER_ID")
WHATSAPP_USER_PHONE_NUMBER = os.getenv("WHATSAPP_USER_PHONE_NUMBER")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")


def check_expiring_products():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Checking expiring products...")


def check_payment_reminders():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Checking payment reminders...")


def read_wells_spreadsheet():
    try:
        # Setup Google Sheets authentication
        # You'll need to place your service account JSON file in the project directory
        # and update the filename below
        gc = gspread.service_account(
            filename="whatsap-automation-service-60ba0a9906a4.json"
        )

        # Open the clients spreadsheet and read its first sheet
        clients_spreadsheet = gc.open("whatsap_automation_clients")
        clients_worksheet = clients_spreadsheet.sheet1
        clients_data = clients_worksheet.get_all_records()

        last_sheet_data = None

        for client_index, client_row in enumerate(clients_data, 1):
            sheet_name = client_row.get("Sheet_Name")
            sheet_phoneNumber = client_row.get("Phone_Number")
            name = client_row.get("Name")
            if not sheet_name:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Skipping client row {client_index}: missing 'Sheet_Name'"
                )
                continue
            elif not sheet_phoneNumber:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Skipping client row {client_index}: missing 'Phone_Number'"
                )
                continue
            elif not name:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Skipping client row {client_index}: missing 'Name'"
                )
                continue

            try:
                # For each client, open the spreadsheet specified in Sheet_Name
                spreadsheet = gc.open(sheet_name)

                # Get the first worksheet (you can specify a specific sheet name if needed)
                worksheet = spreadsheet.sheet1

                # Get all values from the worksheet
                data = worksheet.get_all_records()
                last_sheet_data = data

                urgentList = []
                warningList = []
                infoList = []

                if data:
                    # Print headers
                    headers = list(data[0].keys())
                    print(f"[{sheet_name}] Headers: {', '.join(headers)}")
                    print("-" * 50)

                    # Print each row
                    for i, row in enumerate(data, 1):
                        required_keys = [
                            "Name",
                            "Quantity",
                            "Expiry_date",
                            "Remaining_Days",
                        ]
                        if not all(
                            k in row and row[k] not in (None, "", " ")
                            for k in required_keys
                        ):
                            continue

                        remaining_days = row["Remaining_Days"]
                        if remaining_days < 10 and remaining_days > 7:
                            infoList.append(row)
                        elif remaining_days <= 7 and remaining_days > 2:
                            warningList.append(row)
                        elif remaining_days <= 2:
                            urgentList.append(row)

                    print(f"[{sheet_name}] infoList", infoList)
                    print(f"[{sheet_name}] warningList", warningList)
                    print(f"[{sheet_name}] urgentList", urgentList)

                    urgentItemsText = "".join(
                        f"{item['Name']} - {item['Quantity']}u (expire {item['Expiry_date']}) | "
                        for item in urgentList
                    )

                    try:
                        print(
                            f"startinggg sending message + {API_VERSION}, {WHATSAPP_BUSINESS_PHONE_NUMBER_ID}, {ACCESS_TOKEN}"
                        )

                        url = f"https://graph.facebook.com/{API_VERSION}/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages"
                        headers = {
                            "Authorization": f"Bearer {ACCESS_TOKEN}",
                            "Content-Type": "application/json",
                        }
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": f"{sheet_phoneNumber}",
                            "type": "template",
                            "template": {
                                "name": "daily_inventory_alert",
                                "language": {"code": "fr"},
                                "components": [
                                    {
                                        "type": "body",
                                        "parameters": [
                                            {"type": "text", "text": f"{name}"},
                                            {"type": "text", "text": "11/12/2025"},
                                            {
                                                "type": "text",
                                                # "text": f"🔴 URGENT (0-2 jours): {len(urgentList)} produit(s): {urgentItemsText}",
                                                "text": f"🔴 URGENT (0-2 jours): {len(urgentList)} produit(s): {urgentItemsText}",
                                            },
                                            {"type": "text", "text": "5"},
                                        ],
                                    }
                                ],
                            },
                        }
                        wRespone = requests.post(url, headers=headers, json=payload)
                        print("wRespone", wRespone.json())

                    except Exception as e:
                        print(
                            f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error sending message for sheet '{sheet_name}': {str(e)}"
                        )
                    else:
                        print(
                            f"Yooooooooooooooo sent message for sheet '{sheet_name}'",
                        )
                else:
                    print(f"No data found in spreadsheet '{sheet_name}'")

                print("=" * 50)

            except gspread.SpreadsheetNotFound:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: spreadsheet '{sheet_name}' not found"
                )
                print(
                    "Please check the spreadsheet name in 'whatsap_automation_clients' and ensure it's shared with your service account"
                )

        return last_sheet_data

    except FileNotFoundError:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: service_account.json file not found"
        )
        print(
            "Please add your Google Service Account JSON file to the project directory"
        )
    except gspread.SpreadsheetNotFound:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: spreadsheet not found"
        )
        print(
            "Please check the spreadsheet name and ensure it's shared with your service account"
        )
    except Exception as e:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error reading spreadsheet: {str(e)}"
        )

    return None


# Test mode: every 5 seconds
# schedule.every(5).seconds.do(read_wells_spreadsheet)
# schedule.every(10).seconds.do(read_wells_spreadsheet)

# Read wells spreadsheet on startup
print("📋 Reading wells spreadsheet...")
read_wells_spreadsheet()

print("🚀 Scheduler started! Press Ctrl+C to stop\n")

# try:
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("\n⛔ Scheduler stopped")
