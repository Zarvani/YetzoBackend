import time
from celery import shared_task
from .models import Notification

@shared_task
def send_push_notification(user_id, title, body, data_payload=None):
    """
    Mock task to simulate sending an FCM push notification in the background.
    """
    print(f"[CELERY] Sending Push to User ID {user_id}...")
    print(f"Title: {title}\nBody: {body}")
    
    # Simulate network latency
    time.sleep(1)
    
    # Here we would normally interface with firebase_admin
    # firebase_admin.messaging.send(message)
    
    print(f"[CELERY] Push sent successfully.")
    return True

@shared_task
def process_booking_dispatch(booking_id):
    """
    Background task triggered when a booking enters 'SEARCHING' state.
    It identifies nearby professionals and fires notifications to them.
    """
    print(f"[CELERY] Initiating dispatch algorithm for Booking {booking_id}")
    time.sleep(2)
    print(f"[CELERY] Dispatch algorithm completed for Booking {booking_id}")
    return True
