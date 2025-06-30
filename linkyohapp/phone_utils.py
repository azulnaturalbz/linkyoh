"""
phone_utils.py – Twilio Verify–based phone verification helpers
---------------------------------------------------------------

This module replaces the custom SMS/WhatsApp code‑sending logic
with Twilio’s Verify service.  Twilio hosts the OTP code, handles
expiry, rate‑limiting, and templating (including WhatsApp), so
the application only needs to start a verification and later
check the code.
"""

import logging
from datetime import timedelta

from django.utils import timezone
from twilio.rest import Client
import credentials

logger = logging.getLogger(__name__)

# Lazily‑initialised Twilio client & Verify service
_client = Client(credentials.TWILIO_ACCOUNT_SID, credentials.TWILIO_AUTH_TOKEN)
_verify_service = _client.verify.v2.services(credentials.TWILIO_VERIFY_SERVICE_SID)


# ---------------------------------------------------------------------------
# Twilio Verify helpers
# ---------------------------------------------------------------------------

def start_twilio_verification(phone_number: str, channel: str = "sms") -> bool:
    """
    Kick off a Twilio Verify flow for *phone_number*.
    `channel` must be either ``"sms"`` or ``"whatsapp"``.
    Returns ``True`` on success, ``False`` on error.
    """
    if not credentials.PHONE_VERIFICATION_ENABLED:
        logger.info(
            "Phone verification disabled. Would have started %s verification for %s",
            channel,
            phone_number,
        )
        return True

    try:
        _verify_service.verifications.create(to=str(phone_number), channel=channel)
        logger.info("Started %s verification for %s", channel, phone_number)
        return True
    except Exception as exc:  # noqa: BLE001 – propagate all Twilio errors uniformly
        logger.error("Verify start failed for %s: %s", phone_number, exc)
        return False


def check_twilio_verification(phone_number: str, code: str) -> bool:
    """
    Ask Twilio to validate *code* for *phone_number*.
    Returns ``True`` if Twilio marks it ``approved``.
    """
    if not credentials.PHONE_VERIFICATION_ENABLED:
        # Development shortcut: accept “000000” when Verify is disabled
        return code == "000000"

    try:
        check = _verify_service.verification_checks.create(
            to=str(phone_number), code=code
        )
        approved = check.status == "approved"
        logger.info("Verification check for %s: %s", phone_number, check.status)
        return approved
    except Exception as exc:  # noqa: BLE001
        logger.error("Verify check failed for %s: %s", phone_number, exc)
        return False


# ---------------------------------------------------------------------------
# Public API expected by the views
# ---------------------------------------------------------------------------

def create_verification(phone_number, method="sms", expiry_minutes: int = 10):
    """
    Wrapper used by the registration flow.

    Starts a Verify request via Twilio and stores a *stub* row in
    ``PhoneVerification`` for local bookkeeping (rate‑limiting,
    analytics).  The actual OTP code is **not** stored locally.

    Returns ``(None, None, success)`` to preserve the original
    triple‑return signature used in the views.
    """
    from .models import PhoneVerification  # local import to avoid Django setup issues

    success = start_twilio_verification(phone_number, method)

    # Up‑sert a stub record (no code stored)
    PhoneVerification.objects.update_or_create(
        phone_number=phone_number,
        defaults={
            "verification_code": "",
            "is_verified": False,
            "verification_method": method,
            "expires_at": timezone.now() + timedelta(minutes=expiry_minutes),
            "attempts": 0,
        },
    )

    return None, None, success


def verify_code(phone_number, code):
    """
    Validate *code* via Twilio Verify and update local attempt / status counters.
    Returns ``True`` when the code is correct.
    """
    from .models import PhoneVerification

    approved = check_twilio_verification(phone_number, code)

    obj, _ = PhoneVerification.objects.get_or_create(phone_number=phone_number)
    obj.attempts += 1
    obj.is_verified = approved
    if approved:
        obj.verification_code = code  # Store the code only on success
        obj.expires_at = timezone.now() + timedelta(days=365)  # Extend expiry on success
    else:
        obj.expires_at = timezone.now() + timedelta(minutes=10)  # Reset expiry on failure
    obj.save(update_fields=["attempts", "is_verified", "verification_code", "expires_at"])

    return approved