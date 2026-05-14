# your_app/utils.py
from webpush import send_user_notification
from .models import Notification # Import your Notification model

def create_and_send_notification(user, title, message, notif_type="system"):
    # 1. Save to database (so it shows in your React screen)
    notif = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notif_type
    )

    # 2. Send the PWA Push Notification
    payload = {
        "head": title,
        "body": message,
        "icon": "/vite.svg", # Path to your PWA icon in React public folder
        "url": "/notifications" 
    }
    
    try:
        # This talks to the browser's push service
        send_user_notification(user=user, payload=payload, ttl=1000)
    except Exception as e:
        print(f"Failed to send push: {e}")
        
    return notif