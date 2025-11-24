import schedule
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def check_expiring_products():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Checking expiring products...")

def check_payment_reminders():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Checking payment reminders...")

def read_wells_spreadsheet():
    try:
        # Setup Google Sheets authentication
        # You'll need to place your service account JSON file in the project directory
        # and update the filename below
        gc = gspread.service_account(filename='whatsap-automation-service-60ba0a9906a4.json')
        
        # Open the spreadsheet by name
        spreadsheet = gc.open('products')
        
        # Get the first worksheet (you can specify a specific sheet name if needed)
        worksheet = spreadsheet.sheet1
        
        # Get all values from the worksheet
        data = worksheet.get_all_records()
        print("DAataaaaaaaaaaaaaa", data)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Wells Spreadsheet Data:")
        print("=" * 50)
        
        if data:
            # Print headers
            headers = list(data[0].keys())
            print(f"Headers: {', '.join(headers)}")
            print("-" * 50)
            
            # Print each row
            for i, row in enumerate(data, 1):
                print(f"Row {i}: {row}")
        else:
            print("No data found in the spreadsheet")
            
        print("=" * 50)
        return data
        
    except FileNotFoundError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: service_account.json file not found")
        print("Please add your Google Service Account JSON file to the project directory")
    except gspread.SpreadsheetNotFound:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: 'wells spreadsheet' not found")
        print("Please check the spreadsheet name and ensure it's shared with your service account")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error reading spreadsheet: {str(e)}")
    
    return None

# Test mode: every 5 seconds
schedule.every(5).seconds.do(read_wells_spreadsheet)
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