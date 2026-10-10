from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def dispatch_booking_to_professionals(booking_id):
    """
    Simulates the Yetzo dispatch algorithm.
    This runs asynchronously in the background.
    """
    from .models import Booking, BookingAssignment
    from apps.professionals.models import ProfessionalProfile
    
    logger.info(f"[DISPATCH ENGINE] Starting dispatch for Booking ID: {booking_id}")
    
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        logger.error(f"[DISPATCH ENGINE] Booking {booking_id} not found.")
        return False
        
    # In a real PostGIS implementation, we would use:
    # professionals = ProfessionalProfile.objects.filter(
    #     location__distance_lte=(booking.address.location, D(km=10))
    # )
    
    # For now, we simulate fetching 5 available professionals in the same city
    professionals = ProfessionalProfile.objects.filter(is_verified=True)[:5]
    
    if not professionals.exists():
        logger.warning(f"[DISPATCH ENGINE] No professionals found for Booking {booking_id}")
        booking.status = 'FAILED_NO_PARTNERS'
        booking.save()
        return False
        
    logger.info(f"[DISPATCH ENGINE] Found {professionals.count()} professionals. Initiating ping sequence...")
    
    for pro in professionals:
        logger.info(f"[DISPATCH ENGINE] Pinging Professional: {pro.user.phone_number}...")
        
        # Simulate network delay/push notification wait time
        time.sleep(2) 
        
        # Simulate Professional Accepting the job (1 in 3 chance)
        import random
        accepted = random.choice([True, False, False])
        
        if accepted:
            logger.info(f"[DISPATCH ENGINE] Professional {pro.user.phone_number} ACCEPTED the booking!")
            BookingAssignment.objects.create(
                booking=booking,
                professional=pro,
                status='ACCEPTED'
            )
            booking.status = 'CONFIRMED'
            booking.save()
            
            # Here we would trigger a WebSocket message back to the customer
            # channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(...)
            
            return True
            
        logger.info(f"[DISPATCH ENGINE] Professional {pro.user.phone_number} declined/timed out.")
        
    logger.warning(f"[DISPATCH ENGINE] All professionals declined Booking {booking_id}.")
    booking.status = 'FAILED_NO_PARTNERS'
    booking.save()
    return False
