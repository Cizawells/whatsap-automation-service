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

        # Open the spreadsheet by name
        spreadsheet = gc.open("wells spreadsheet")

        # Get the first worksheet (you can specify a specific sheet name if needed)
        worksheet = spreadsheet.sheet1

        # Get all values from the worksheet
        data = worksheet.get_all_records()
        # print("DAataaaaaaaaaaaaaa", data)
        urgentList = []
        warningList = []
        infoList = []

        if data:
            # Print headers
            headers = list(data[0].keys())
            print(f"Headers: {', '.join(headers)}")
            print("-" * 50)

            # Print each row
            for i, row in enumerate(data, 1):
                required_keys = ["Name", "Quantity", "Expiry_date", "Remaining_Days"]
                if not all(
                    k in row and row[k] not in (None, "", " ") for k in required_keys
                ):
                    continue

                remaining_days = row["Remaining_Days"]
                # print(f"Row {i} remaining days: {row["Remaining_Days"]}")
                if remaining_days < 10 and remaining_days > 7:
                    infoList.append(row)
                elif remaining_days <= 7 and remaining_days > 2:
                    warningList.append(row)
                elif remaining_days <= 2:
                    urgentList.append(row)

                # try:
                #     print(
                #         f"startinggg sending message + {API_VERSION}, {WHATSAPP_BUSINESS_PHONE_NUMBER_ID}, {ACCESS_TOKEN}"
                #     )

                #     url = f"https://graph.facebook.com/{API_VERSION}/{WHATSAPP_BUSINESS_PHONE_NUMBER_ID}/messages"
                #     headers = {
                #         "Authorization": f"Bearer {ACCESS_TOKEN}",
                #         "Content-Type": "application/json",
                #     }
                #     data = {
                #         "messaging_product": "whatsapp",
                #         "to": f"{WHATSAPP_USER_PHONE_NUMBER}",
                #         "type": "template",
                #         "template": {
                #             "name": "payment_template",
                #             "language": {"code": "en_US"},
                #             "components": [  # ✅ Inside template
                #                 {
                #                     "type": "body",
                #                     "parameters": [
                #                         {"type": "text", "text": "Wells"},
                #                         {"type": "text", "text": "$50"},
                #                         {"type": "text", "text": "invoice"},
                #                     ],
                #                 }
                #             ],
                #         },
                #     }
                #     wRespone = requests.post(url, headers=headers, json=data)
                #     print("wRespone", wRespone.json())

                # except Exception as e:
                #     print(
                #         f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error processing row {i}: {str(e)}"
                #     )
                # else:
                #     print(
                #         "Yooooooooooooooo sent message",
                #     )
            print("infoList", infoList)
            print("warningList", warningList)
            print("urgentList", urgentList)
        else:
            print("No data found in the spreadsheet")

        print("=" * 50)
        return data

    except FileNotFoundError:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: service_account.json file not found"
        )
        print(
            "Please add your Google Service Account JSON file to the project directory"
        )
    except gspread.SpreadsheetNotFound:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: 'wells spreadsheet' not found"
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
schedule.every(10).seconds.do(read_wells_spreadsheet)

# Read wells spreadsheet on startup
print("📋 Reading wells spreadsheet...")
read_wells_spreadsheet()

print("🚀 Scheduler started! Press Ctrl+C to stop\n")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n⛔ Scheduler stopped")
