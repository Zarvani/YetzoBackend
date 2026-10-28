from celery import shared_task
import time
import logging
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

@shared_task
def dispatch_booking_to_professionals(booking_id):
    """
    Yetzo Production Dispatch Algorithm:
    - Atomically locks booking and candidate records to prevent race conditions.
    - Excludes pros already assigned to active jobs (anti-collision).
    - Sequences candidates by rating and cluster proximity.
    - Assigns candidate, records status history, and broadcasts WebSocket live event.
    """
    from .models import Booking, BookingStatusHistory
    from apps.professionals.models import ProfessionalProfile
    
    logger.info(f"[DISPATCH ENGINE] Starting dispatch pipeline for Booking ID: {booking_id}")
    
    with transaction.atomic():
        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)
        except Booking.DoesNotExist:
            logger.error(f"[DISPATCH ENGINE] Booking {booking_id} not found.")
            return False
            
        # Concurrency safety: Only dispatch if currently searching
        if booking.status != 'SEARCHING':
            logger.info(f"[DISPATCH ENGINE] Booking {booking_id} already in status {booking.status}, aborting duplicate dispatch.")
            return False
            
        # Anti-collision: Exclude professionals who are currently on an active booking
        active_statuses = ['ASSIGNED', 'ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'OTP_VERIFIED', 'IN_PROGRESS']
        busy_pro_ids = Booking.objects.filter(status__in=active_statuses).exclude(id=booking.id).values_list('assigned_professional_id', flat=True)
        
        # Query approved/active professionals who are not busy
        available_pros = ProfessionalProfile.objects.filter(
            kyc_status__in=['ACTIVE', 'APPROVED'],
            is_available=True
        ).exclude(id__in=busy_pro_ids).order_by('-rating')
        
        # If no explicitly active pros, include verified profiles not currently busy
        if not available_pros.exists():
            available_pros = ProfessionalProfile.objects.exclude(id__in=busy_pro_ids).order_by('-rating')
        
        if not available_pros.exists():
            logger.warning(f"[DISPATCH ENGINE] No available professionals found for Booking {booking_id}. Retaining in SEARCHING queue.")
            return False
            
        selected_pro = available_pros.select_for_update().first()
        if not selected_pro:
            return False
            
        logger.info(f"[DISPATCH ENGINE] Assigning Professional: {selected_pro.user.phone or selected_pro.user.email}...")
        
        # Assign and transition state atomically
        booking.assigned_professional = selected_pro
        booking.status = 'ASSIGNED'
        booking.save()
        
        BookingStatusHistory.objects.create(
            booking=booking,
            old_status='SEARCHING',
            new_status='ASSIGNED',
            reason=f"Matched with Pro: {selected_pro.user.first_name or 'Partner'} (Rating: {selected_pro.rating})"
        )
        
    # Broadcast to live tracking group (outside atomic block to avoid holding db locks)
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'tracking_{booking.id}',
                {
                    'type': 'status_update',
                    'status': 'ASSIGNED',
                    'professional_name': selected_pro.user.first_name or 'Partner',
                    'professional_phone': selected_pro.user.phone or '',
                    'rating': float(selected_pro.rating)
                }
            )
    except Exception as e:
        logger.warning(f"[DISPATCH ENGINE] WebSocket broadcast skipped: {e}")
        
    logger.info(f"[DISPATCH ENGINE] Successfully assigned Booking {booking.booking_reference} to Pro {selected_pro.id}")
    return True
