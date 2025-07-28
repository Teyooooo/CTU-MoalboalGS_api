from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import os
from firebase_admin import firestore
import firebase_cred 
from dotenv import load_dotenv

load_dotenv()

db = firestore.client()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def send_email(to_email, subject, body, html_body=None):
    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, APP_PASSWORD)
        smtp.send_message(msg)

    print(f"✅ Email sent to {to_email}")

def get_account_by_name(name):
    try:
        users = db.collection("accounts").where("name", "==", name).limit(1).stream()
        user = next(users, None)
        if user:
            return user.to_dict()  # Return entire user data
        else:
            print(f"⚠️ No user found with name: {name}")
            return None
    except Exception as e:
        print("Error getting account by name:", e)
        return None

def get_tasks_due_soon():
    today = datetime.now().date()
    print("📅 Today is:", today)

    tasks_due = {}

    trimesters = db.collection("trimesters").stream()

    for tri_doc in trimesters:
        tasks = db.collection("trimesters").document(tri_doc.id).collection("tasks").stream()

        for task_doc in tasks:
            task_data = task_doc.to_dict()
            deadline = task_data.get("deadline")
            reminder_sent = task_data.get("reminder_sent", False)

            print(f"\n🔍 Task: {task_data.get('name')}")
            print("Raw deadline:", deadline)
            print("Reminder sent:", reminder_sent)

            if not deadline or reminder_sent:
                print("⏭️ Skipping: No deadline or already reminded.")
                continue

            # Handle Firestore Timestamp or string deadline
            if hasattr(deadline, "date"):
                deadline_date = deadline.date()
            elif isinstance(deadline, str):
                try:
                    deadline_date = datetime.strptime(deadline, "%m/%d/%Y").date()
                except ValueError:
                    print("⚠️ Invalid date format for deadline.")
                    continue
            else:
                print("⚠️ Unsupported deadline format:", type(deadline))
                continue

            print("Parsed deadline date:", deadline_date)

            if (deadline_date - today).days != 3:
                print("⏭️ Not 3 days away.")
                continue

            # Process users
            users_ref = task_doc.reference.collection("users")
            users = users_ref.stream()

            for user_doc in users:
                username = user_doc.id
                user_account = get_account_by_name(username)

                if user_account is None:
                    print(f"⚠️ No account for user: {username}")
                    continue

                email = user_account["email"]
                name = user_account["name"]


                if email not in tasks_due:
                    tasks_due[email] = {
                        "name": name,
                        "deadline": deadline_date.strftime("%B %d, %Y"),
                        "tasks": []
                    }

                tasks_due[email]["tasks"].append(task_data["name"])
                print(f"✅ Added task '{task_data['name']}' for {email}")

    return tasks_due

def get_all_users_names():
    try:
        users_ref = db.collection("accounts").stream()
        names = []
        for user_doc in users_ref:
            user_data = user_doc.to_dict()
            name = user_data.get("name")
            if name:
                names.append(name)
        return names
    except Exception as e:
        print("Error fetching user names:", e)
        return []

def send_upcoming_deadline_emails_grouped():
    user_tasks = get_tasks_due_soon()

    for email, info in user_tasks.items():
        task_list = "\n".join([f"- {task}" for task in info["tasks"]])
        message = f"""Hi {info['name']},

This is a reminder that the following task(s) are due on {info['deadline']}:

{task_list}

Please make sure to complete them before the deadline.

Thank you!
"""

        html = f"""
        <html>
          <body>
            <p>Hi {info['name']},</p>
            <p>This is a reminder that the following tasks are due on <strong>{info['deadline']}</strong>:</p>
            <ul>
              {''.join(f'<li>{task}</li>' for task in info['tasks'])}
            </ul>
            <p>Please make sure to complete them before the deadline.</p>
            <p>Thank you!</p>
          </body>
        </html>
        """

        send_email(
            to_email=email,
            subject=f"Reminder: {len(info['tasks'])} task(s) due on {info['deadline']}",
            body=message,
            html_body=html
        )


if __name__ == "__main__":
    # send_upcoming_deadline_emails_grouped()
    
    # print(get_all_users_names())
    print(get_tasks_due_soon())
    
    # print(GMAIL_ADDRESS)