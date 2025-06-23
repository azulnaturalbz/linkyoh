import random
import string
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import credentials

logger = logging.getLogger(__name__)

def generate_verification_code(length=6):
    """Generate a random verification code of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_sms(phone_number, verification_code):
    """Send verification code via SMS using Twilio"""
    if not credentials.PHONE_VERIFICATION_ENABLED:
        logger.info(f"Phone verification disabled. Would have sent code {verification_code} to {phone_number}")
        return True
    
    try:
        client = Client(credentials.TWILIO_ACCOUNT_SID, credentials.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your Linkyoh verification code is: {verification_code}",
            from_=credentials.TWILIO_PHONE_NUMBER,
            to=str(phone_number)
        )
        logger.info(f"SMS sent to {phone_number}: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False

def send_verification_whatsapp(phone_number, verification_code):
    """Send verification code via WhatsApp using Twilio"""
    if not credentials.PHONE_VERIFICATION_ENABLED:
        logger.info(f"Phone verification disabled. Would have sent code {verification_code} to {phone_number} via WhatsApp")
        return True
    
    try:
        client = Client(credentials.TWILIO_ACCOUNT_SID, credentials.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your Linkyoh verification code is: {verification_code}",
            from_=f"whatsapp:{credentials.TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{str(phone_number)}"
        )
        logger.info(f"WhatsApp message sent to {phone_number}: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Failed to send WhatsApp message to {phone_number}: {str(e)}")
        return False

def create_verification(phone_number, method='sms', expiry_minutes=10):
    """
    Create a new verification code for the given phone number
    
    Args:
        phone_number: The phone number to verify
        method: The verification method ('sms' or 'whatsapp')
        expiry_minutes: Number of minutes until the code expires
        
    Returns:
        tuple: (verification_object, verification_code)
    """
    from .models import PhoneVerification
    
    # Generate a new verification code
    verification_code = generate_verification_code()
    
    # Calculate expiration time
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    
    # Create or update verification record
    verification, created = PhoneVerification.objects.update_or_create(
        phone_number=phone_number,
        defaults={
            'verification_code': verification_code,
            'is_verified': False,
            'verification_method': method,
            'expires_at': expires_at,
            'attempts': 0
        }
    )
    
    # Send the verification code
    if method == 'whatsapp':
        success = send_verification_whatsapp(phone_number, verification_code)
    else:  # Default to SMS
        success = send_verification_sms(phone_number, verification_code)
    
    return verification, verification_code, success

def verify_code(phone_number, code):
    """
    Verify a code for a given phone number
    
    Args:
        phone_number: The phone number to verify
        code: The verification code to check
        
    Returns:
        bool: True if verification successful, False otherwise
    """
    from .models import PhoneVerification
    
    try:
        verification = PhoneVerification.objects.get(phone_number=phone_number)
        
        # Check if the verification has expired
        if verification.is_expired():
            logger.warning(f"Verification code for {phone_number} has expired")
            return False
        
        # Increment the number of attempts
        verification.attempts += 1
        verification.save()
        
        # Check if the code matches
        if verification.verification_code == code:
            verification.is_verified = True
            verification.save()
            logger.info(f"Phone number {phone_number} successfully verified")
            return True
        else:
            logger.warning(f"Invalid verification code for {phone_number}")
            return False
    except PhoneVerification.DoesNotExist:
        logger.warning(f"No verification found for {phone_number}")
        return False