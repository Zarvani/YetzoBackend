import os
import sys
import django
import uuid

sys.path.append(r'c:\Yetzo\YetzoBackend\django_core')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, Role
from apps.professionals.models import ProfessionalProfile
from apps.bookings.models import Booking, BookingItem
from apps.payments.models import Payment, Refund, Wallet, WalletTransaction, EscrowLedger
from apps.services.models import Service, Category
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.professionals.views import AdminProfessionalKYCUpdateView, AdminProfessionalDetailView
from apps.bookings.views import BookingStatusUpdateView
from apps.payments.views import RefundListView, RefundProcessView

def run_ops_verification():
    print("=== STARTING OPERATIONS & ADMIN VERIFICATION SUITE ===")
    factory = APIRequestFactory()
    
    # 1. Setup Admin User
    admin_role, _ = Role.objects.get_or_create(name='OPERATIONS_MANAGER')
    admin_user, _ = User.objects.get_or_create(
        email='ops.head@yetzo.com',
        defaults={'phone': '+919999000001', 'first_name': 'Ops', 'last_name': 'Commander', 'role': admin_role}
    )
    admin_user.role = admin_role
    admin_user.is_staff = True
    admin_user.save()
    
    # 2. Setup Candidate Professional
    pro_role, _ = Role.objects.get_or_create(name='PROFESSIONAL')
    pro_user, _ = User.objects.get_or_create(
        email='ramesh.ops@yetzo.com',
        defaults={'phone': '+919999000002', 'first_name': 'Ramesh', 'last_name': 'Sharma', 'role': pro_role}
    )
    pro_profile, _ = ProfessionalProfile.objects.get_or_create(
        user=pro_user,
        defaults={'kyc_status': 'APPLIED', 'current_status': 'OFFLINE'}
    )
    
    # --- TEST 1: KYC Approval Endpoint ---
    print("\n[Test 1] Testing KYC Approval via AdminProfessionalKYCUpdateView...")
    view_kyc = AdminProfessionalKYCUpdateView.as_view()
    request_kyc = factory.patch(
        f'/api/v1/professionals/{pro_profile.id}/kyc/',
        {'kyc_status': 'ACTIVE'},
        format='json'
    )
    force_authenticate(request_kyc, user=admin_user)
    response_kyc = view_kyc(request_kyc, id=pro_profile.id)
    assert response_kyc.status_code == 200, f"KYC Approval failed with {response_kyc.status_code}: {response_kyc.data}"
    
    pro_profile.refresh_from_db()
    assert pro_profile.kyc_status == 'ACTIVE', f"Expected ACTIVE, got {pro_profile.kyc_status}"
    assert pro_profile.is_online == True, "Expected is_online to be True"
    assert pro_profile.current_status == 'ONLINE', f"Expected ONLINE, got {pro_profile.current_status}"
    print("PASS: Professional KYC transitioned to ACTIVE, status set to ONLINE.")
    
    # --- TEST 2: Professional Detail View ---
    print("\n[Test 2] Testing AdminProfessionalDetailView...")
    view_pro_detail = AdminProfessionalDetailView.as_view()
    request_detail = factory.get(f'/api/v1/professionals/{pro_profile.id}/')
    force_authenticate(request_detail, user=admin_user)
    response_detail = view_pro_detail(request_detail, id=pro_profile.id)
    assert response_detail.status_code == 200, f"Pro Detail failed: {response_detail.status_code}"
    print("PASS: Pro detail retrieved successfully.")
    
    # --- TEST 3: Manual Operations Dispatch Override ---
    print("\n[Test 3] Testing Manual Operations Dispatch Override...")
    cust_role, _ = Role.objects.get_or_create(name='CUSTOMER')
    cust_user, _ = User.objects.get_or_create(
        email='neha.ops@yetzo.com',
        defaults={'phone': '+919999000003', 'first_name': 'Neha', 'last_name': 'Verma', 'role': cust_role}
    )
    service = Service.objects.first()
    if not service:
        category, _ = Category.objects.get_or_create(name='Home Chores', slug='home-chores-ops')
        service = Service.objects.create(
            category=category,
            name='Kitchen Clean Test',
            slug='kitchen-clean-ops'
        )
    from apps.locations.models import Address
    address = Address.objects.first()
    if not address:
        address = Address.objects.create(
            user=cust_user,
            house_flat='Flat 402',
            street='Green Glen Layout',
            city='Bengaluru',
            state='Karnataka',
            pincode='560103'
        )
    booking = Booking.objects.create(
        booking_reference=f"YZ-OPS-{uuid.uuid4().hex[:6].upper()}",
        customer=cust_user,
        service=service,
        address=address,
        status='SEARCHING',
        total_amount=299,
        base_price=299,
        start_otp="1234",
        end_otp="5678"
    )
    
    view_dispatch = BookingStatusUpdateView.as_view()
    request_dispatch = factory.patch(
        f'/api/v1/bookings/{booking.id}/status/',
        {
            'new_status': 'ASSIGNED',
            'professional_id': str(pro_profile.id),
            'reason': 'Manual Operations Dispatcher Override'
        },
        format='json'
    )
    force_authenticate(request_dispatch, user=admin_user)
    response_dispatch = view_dispatch(request_dispatch, id=booking.id)
    assert response_dispatch.status_code == 200, f"Manual dispatch failed: {response_dispatch.data}"
    
    booking.refresh_from_db()
    pro_profile.refresh_from_db()
    assert booking.status == 'ASSIGNED', f"Expected ASSIGNED, got {booking.status}"
    assert booking.assigned_professional == pro_profile, "Assigned professional does not match!"
    assert pro_profile.current_status == 'BUSY', f"Expected BUSY, got {pro_profile.current_status}"
    print(f"PASS: Booking {booking.booking_reference} manually assigned to {pro_profile.user.first_name}. Pro marked BUSY.")
    
    # --- TEST 4: Escrow Refund Disbursement ---
    print("\n[Test 4] Testing Escrow Refund & Reversal Desk...")
    payment = Payment.objects.create(
        booking=booking,
        user=cust_user,
        amount=299,
        status='CAPTURED'
    )
    escrow = EscrowLedger.objects.create(
        booking=booking,
        payment=payment,
        amount_held=299,
        status='HELD'
    )
    refund = Refund.objects.create(
        payment=payment,
        amount=299,
        status='PENDING',
        reason='Customer requested cancellation prior to arrival'
    )
    
    # 4a: List refunds
    view_refund_list = RefundListView.as_view()
    request_rlist = factory.get('/api/v1/payments/refunds/')
    force_authenticate(request_rlist, user=admin_user)
    response_rlist = view_refund_list(request_rlist)
    assert response_rlist.status_code == 200, f"Refund list failed: {response_rlist.status_code}"
    assert len(response_rlist.data) > 0, "Expected at least 1 refund record in ledger"
    
    # 4b: Process refund
    view_refund_proc = RefundProcessView.as_view()
    request_proc = factory.post(f'/api/v1/payments/refunds/{refund.id}/process/')
    force_authenticate(request_proc, user=admin_user)
    response_proc = view_refund_proc(request_proc, id=refund.id)
    assert response_proc.status_code == 200, f"Refund process failed: {response_proc.data}"
    
    refund.refresh_from_db()
    payment.refresh_from_db()
    escrow.refresh_from_db()
    cust_wallet = Wallet.objects.get(user=cust_user)
    
    assert refund.status == 'PROCESSED', f"Expected PROCESSED, got {refund.status}"
    assert refund.provider_refund_id.startswith('rfnd_'), f"Invalid provider_refund_id: {refund.provider_refund_id}"
    assert payment.status == 'REFUNDED', f"Expected REFUNDED, got {payment.status}"
    assert escrow.status == 'REFUNDED', f"Expected escrow REFUNDED, got {escrow.status}"
    assert cust_wallet.balance >= 299, f"Customer wallet not credited! Balance: {cust_wallet.balance}"
    print(f"PASS: Refund #{refund.provider_refund_id} disbursed. Escrow released. Customer wallet credited ₹{cust_wallet.balance}.")
    
    print("\n=== ALL OPERATIONS & ESCROW TESTS PASSED CLEANLY (4/4) ===")

if __name__ == '__main__':
    run_ops_verification()
