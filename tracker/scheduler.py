import threading
import time
from datetime import datetime
from .db import list_applications

def process_reminders(user_id, username):
    """
    Background worker function that runs in a separate thread.
    Queries MongoDB for applications with deadlines and checks if follow-up is due.
    """
    print(f"\n[SCHEDULER THREAD STARTED] Running background reminders for user: {username} (ID: {user_id})")
    
    # Simulate a small delay to mimic network latency or external notification API call
    time.sleep(2)
    
    try:
        # Fetch all applications for the user
        applications = list_applications(user_id)
        current_date_str = datetime.today().strftime('%Y-%m-%d')
        current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
        
        due_alerts = []
        for app in applications:
            if app.get('deadline'):
                try:
                    deadline_date = datetime.strptime(app['deadline'], '%Y-%m-%d')
                    # Check if deadline is today or in the past
                    if deadline_date <= current_date:
                        due_alerts.append(app)
                except ValueError:
                    # Date formatting issue in MongoDB document
                    print(f"[SCHEDULER WARNING] Invalid date format for application {app.get('id')}: {app.get('deadline')}")
                    
        # Log/Print the results to terminal representing an email/SMS notification system
        if due_alerts:
            print(f"=== [DEADLINE ALERTS FOUND] Sent notification emails for {len(due_alerts)} applications ===")
            for app in due_alerts:
                print(f"  --> ALERT: Follow-up is DUE for {app['company_name']} - {app['job_title']} (Deadline was: {app['deadline']}) -> Sent to {app.get('contact_email', 'User Email')}")
            print("==========================================================================")
        else:
            print("[SCHEDULER THREAD] No due/overdue deadlines found for today.")
            
    except Exception as e:
        print(f"[SCHEDULER THREAD ERROR] Failed to process reminders: {e}")
        
    print(f"[SCHEDULER THREAD FINISHED] Terminated background thread for user: {username}\n")

def start_reminder_scheduler(user_id, username):
    """
    Spawns a new background thread to execute the reminder checker.
    Prevents Django request thread blocking.
    """
    # Create thread targeting process_reminders
    thread = threading.Thread(target=process_reminders, args=(user_id, username))
    # Make thread daemon so it closes automatically when server stops
    thread.daemon = True
    thread.start()
    return thread
