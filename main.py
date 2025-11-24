import schedule
import time
from datetime import datetime

def check_expiring_products():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Checking expiring products...")

def check_payment_reminders():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Checking payment reminders...")

# Test mode: every 5 seconds
schedule.every(5).seconds.do(check_expiring_products)
schedule.every(10).seconds.do(check_payment_reminders)

print("🚀 Scheduler started! Press Ctrl+C to stop\n")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n⛔ Scheduler stopped")