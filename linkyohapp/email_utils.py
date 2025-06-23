import logging
from django.conf import settings
from .tasks import send_email_task

logger = logging.getLogger(__name__)

def send_email(subject, template_html, template_txt, context, recipient_list, from_email=None, async_send=True):
    """
    Send an email with both HTML and text versions.

    Args:
        subject (str): Email subject
        template_html (str): Path to HTML template
        template_txt (str): Path to text template
        context (dict): Context for rendering templates
        recipient_list (list): List of recipient email addresses
        from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.
        async_send (bool, optional): Whether to send the email asynchronously using Celery. Defaults to True.

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    try:
        if async_send:
            # Send email asynchronously using Celery
            send_email_task.delay(
                subject=subject,
                template_html=template_html,
                template_txt=template_txt,
                context=context,
                recipient_list=recipient_list,
                from_email=from_email
            )
            logger.info(f"Email task queued for {', '.join(recipient_list)}: {subject}")
            return True
        else:
            # Send email synchronously
            return send_email_task(
                subject=subject,
                template_html=template_html,
                template_txt=template_txt,
                context=context,
                recipient_list=recipient_list,
                from_email=from_email
            )
    except Exception as e:
        logger.error(f"Failed to queue email task for {', '.join(recipient_list)}: {str(e)}")
        return False

def send_welcome_email(user, request=None):
    """
    Send a welcome email to a new user.

    Args:
        user: User object
        request: HTTP request object (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Welcome to Linkyoh!"
    template_html = "emails/welcome_email.html"
    template_txt = "emails/welcome_email.txt"

    # Prepare context
    context = {
        'user': user,
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }

    # Add domain and protocol if request is provided
    if request:
        context['domain'] = request.get_host()
        context['protocol'] = 'https' if request.is_secure() else 'http'
    else:
        # Default values if request is not provided
        context['domain'] = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
        context['protocol'] = 'https'

    return send_email(
        subject=subject,
        template_html=template_html,
        template_txt=template_txt,
        context=context,
        recipient_list=[user.email]
    )

def send_password_reset_confirmation_email(user, request=None):
    """
    Send a confirmation email after a user resets their password.

    Args:
        user: User object
        request: HTTP request object (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Your Password Has Been Reset"
    template_html = "emails/password_reset_confirmation.html"
    template_txt = "emails/password_reset_confirmation.txt"

    # Prepare context
    context = {
        'user': user,
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }

    # Add domain and protocol if request is provided
    if request:
        context['domain'] = request.get_host()
        context['protocol'] = 'https' if request.is_secure() else 'http'
    else:
        # Default values if request is not provided
        context['domain'] = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
        context['protocol'] = 'https'

    return send_email(
        subject=subject,
        template_html=template_html,
        template_txt=template_txt,
        context=context,
        recipient_list=[user.email]
    )
