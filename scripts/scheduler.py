import schedule
import time
from run import run

def job():
    print("Running daily brief...")
    run()

# Schedule every morning at 7:00 AM
schedule.every().day.at("07:00").do(job)

print("Scheduler running. Brief will generate every morning at 7:00 AM.")
print("Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(60)