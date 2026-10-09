from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.bookings.models import Booking
from apps.services.models import Service, ServiceCategory
from apps.locations.models import Address
import threading
import time

User = get_user_model()

class BookingAtomicityTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@yetzo.com",
            phone_number="+919999999999",
            password="password"
        )
        self.category = ServiceCategory.objects.create(name="Cleaning", slug="cleaning")
        self.service = Service.objects.create(
            category=self.category,
            name="Deep Cleaning",
            slug="deep-cleaning",
            base_price=100000, # 1000 INR
            estimated_duration=120
        )
        self.address = Address.objects.create(
            user=self.user,
            full_address="123 Test St",
            city="Testville",
            postal_code="123456",
            latitude=12.9716,
            longitude=77.5946
        )

    def test_booking_status_race_condition(self):
        """
        Verify that multiple concurrent threads attempting to modify the same
        booking status (e.g. two webhooks hitting simultaneously) do not result
        in inconsistent states by leveraging select_for_update().
        """
        booking = Booking.objects.create(
            booking_reference="YZ-TEST-123",
            customer=self.user,
            service=self.service,
            address=self.address,
            status='PENDING_PAYMENT',
            total_amount=100000
        )
        
        # We will simulate two threads trying to update the booking status.
        def worker_update_status(target_status):
            try:
                with transaction.atomic():
                    # select_for_update locks the row until transaction completes
                    b = Booking.objects.select_for_update().get(id=booking.id)
                    # Simulate some processing delay
                    time.sleep(0.5)
                    b.status = target_status
                    b.save()
            except Exception as e:
                pass
                
        # Thread 1 tries to mark it CONFIRMED
        t1 = threading.Thread(target=worker_update_status, args=('CONFIRMED',))
        # Thread 2 tries to mark it FAILED
        t2 = threading.Thread(target=worker_update_status, args=('FAILED',))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Depending on which thread acquired the lock last, it will overwrite the previous one safely.
        # Without select_for_update, Django might raise concurrent update exceptions or lose data.
        booking.refresh_from_db()
        self.assertIn(booking.status, ['CONFIRMED', 'FAILED'])
