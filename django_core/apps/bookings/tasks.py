from celery import shared_task
import time
import math
import logging
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in kilometers between two GPS coordinates."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@shared_task
def dispatch_booking_to_professionals(booking_id):
    """
    Yetzo Production Pronto-Style Dispatch Algorithm:
    - Atomically locks booking and candidate records to prevent race conditions.
    - Anti-collision: Excludes pros already assigned to active jobs.
    - Anti-spam: Excludes pros who previously declined or timed out on this booking.
    - Geospatial Dark Dispatch: Sequences by GPS proximity (<= 3.0 km dark dispatch radius), then rating.
    - Records BookingAssignment with PENDING state for rapid-accept window.
    - Broadcasts live WebSocket event to tracking room.
    """
    from .models import Booking, BookingStatusHistory, BookingAssignment
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
        
        # Anti-spam: Exclude professionals who previously declined or timed out on this specific booking
        rejected_pro_ids = BookingAssignment.objects.filter(
            booking=booking,
            status__in=['REJECTED', 'TIMEOUT']
        ).values_list('professional_id', flat=True)
        
        # Query approved/active professionals who are online and not busy
        available_pros_qs = ProfessionalProfile.objects.filter(
            kyc_status__in=['ACTIVE', 'APPROVED'],
            is_online=True,
            current_status='ONLINE'
        ).exclude(id__in=busy_pro_ids).exclude(id__in=rejected_pro_ids)
        
        if not available_pros_qs.exists():
            # If no explicitly active pros, include online profiles not currently busy
            available_pros_qs = ProfessionalProfile.objects.filter(
                is_online=True
            ).exclude(id__in=busy_pro_ids).exclude(id__in=rejected_pro_ids)
        
        if not available_pros_qs.exists():
            logger.warning(f"[DISPATCH ENGINE] No available professionals found for Booking {booking_id}. Retaining in SEARCHING queue.")
            return False
            
        # Geospatial Dark-Dispatch Proximity Ranking
        candidate_list = list(available_pros_qs.select_for_update())
        
        cust_lat = None
        cust_lng = None
        if hasattr(booking.address, 'location') and booking.address.location:
            cust_lat = booking.address.location.y
            cust_lng = booking.address.location.x
            
        if cust_lat is not None and cust_lng is not None:
            # Sort with GPS distance awareness: within 3km prioritized
            def pro_distance_score(p):
                if p.current_latitude and p.current_longitude:
                    d = calculate_haversine_distance(cust_lat, cust_lng, p.current_latitude, p.current_longitude)
                    return (0 if d <= 3.0 else 1, d, -float(p.rating))
                return (2, 999.0, -float(p.rating))
            
            candidate_list.sort(key=pro_distance_score)
        else:
            candidate_list.sort(key=lambda p: -float(p.rating))
            
        if not candidate_list:
            return False
            
        selected_pro = candidate_list[0]
        
        logger.info(f"[DISPATCH ENGINE] Assigning Professional: {selected_pro.user.phone or selected_pro.user.email}...")
        
        # Assign and transition state atomically
        booking.assigned_professional = selected_pro
        booking.status = 'ASSIGNED'
        booking.save()
        
        selected_pro.current_status = 'BUSY'
        selected_pro.save(update_fields=['current_status', 'updated_at'])
        
        # Record Assignment with rapid-accept PENDING state
        BookingAssignment.objects.update_or_create(
            booking=booking,
            professional=selected_pro,
            defaults={'status': 'PENDING'}
        )
        
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
            raw_phone = selected_pro.user.phone or ''
            masked_phone = f"{raw_phone[:4]}****{raw_phone[-2:]}" if len(raw_phone) >= 6 else "Verified Partner"
            async_to_sync(channel_layer.group_send)(
                f'tracking_{booking.id}',
                {
                    'type': 'status_update',
                    'status': 'ASSIGNED',
                    'professional_name': selected_pro.user.first_name or 'Partner',
                    'professional_phone': masked_phone,
                    'rating': float(selected_pro.rating)
                }
            )
    except Exception as e:
        logger.warning(f"[DISPATCH ENGINE] WebSocket broadcast skipped: {e}")
        
    logger.info(f"[DISPATCH ENGINE] Successfully assigned Booking {booking.booking_reference} to Pro {selected_pro.id}")
    return True
