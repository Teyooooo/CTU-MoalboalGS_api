import firebase_admin
from firebase_admin import db
import firebase_cred 
from send_email import get_all_users_names
from datetime import datetime

def sanitize_key(key: str) -> str:
    return (
        key.replace('.', '__DOT__')
           .replace(' ', '__SP__')
           .replace('#', '__H__')
           .replace('$', '__DOL__')
           .replace('[', '__LBK__')
           .replace(']', '__RBK__')
           .replace('/', '__SL__')
    )
    
def initialize_attendance_date():
    user_ids = get_all_users_names()

    today = datetime.today()
    date_str = today.strftime("%B %d, %Y").replace(" 0", " ")

    
    
    base_ref = db.reference(f'Attendance/{sanitize_key(date_str)}')
    
    for user_id in user_ids:
        user_ref = base_ref.child(sanitize_key(user_id))
        user_ref.set({
            "time-in": "",
            "time-out": ""
        })
    
    print(f"Initialized attendance for {date_str} with users: {', '.join(user_ids)}")
    return date_str
    
    
if __name__ == "__main__":
    initialize_attendance_date()
    