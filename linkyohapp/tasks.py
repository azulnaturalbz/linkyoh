import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from .models import Notification, User

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(subject, template_html, template_txt, context, recipient_list, from_email=None):
    """
    Celery task to send an email with both HTML and text versions.
    
    Args:
        subject (str): Email subject
        template_html (str): Path to HTML template
        template_txt (str): Path to text template
        context (dict): Context for rendering templates
        recipient_list (list): List of recipient email addresses
        from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        # Render HTML and text content
        html_content = render_to_string(template_html, context)
        text_content = render_to_string(template_txt, context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        logger.info(f"Email sent to {', '.join(recipient_list)}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {', '.join(recipient_list)}: {str(e)}")
        return False

@shared_task
def send_welcome_email_task(user_data, domain, protocol, support_email):
    """
    Celery task to send a welcome email to a new user.
    
    Args:
        user_data (dict): User data including id, username, first_name, email
        domain (str): Domain name
        protocol (str): Protocol (http or https)
        support_email (str): Support email address
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Welcome to Linkyoh!"
    template_html = "emails/welcome_email.html"
    template_txt = "emails/welcome_email.txt"
    
    # Prepare context
    context = {
        'user': user_data,
        'domain': domain,
        'protocol': protocol,
        'support_email': support_email,
    }
    
    return send_email_task(
        subject=subject,
        template_html=template_html,
        template_txt=template_txt,
        context=context,
        recipient_list=[user_data['email']]
    )

@shared_task
def send_password_reset_confirmation_task(user_data, domain, protocol, support_email):
    """
    Celery task to send a confirmation email after a user resets their password.
    
    Args:
        user_data (dict): User data including id, username, first_name, email
        domain (str): Domain name
        protocol (str): Protocol (http or https)
        support_email (str): Support email address
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Your Password Has Been Reset"
    template_html = "emails/password_reset_confirmation.html"
    template_txt = "emails/password_reset_confirmation.txt"
    
    # Prepare context
    context = {
        'user': user_data,
        'domain': domain,
        'protocol': protocol,
        'support_email': support_email,
    }
    
    return send_email_task(
        subject=subject,
        template_html=template_html,
        template_txt=template_txt,
        context=context,
        recipient_list=[user_data['email']]
    )
@shared_task
def send_notification_emails():
    """
    Task to send email notifications for unread notifications.
    This task bundles notifications to avoid spamming users.
    """
    # Get users with unread notifications that haven't been emailed
    users_with_notifications = User.objects.filter(
        notifications__is_read=False,
        notifications__email_sent=False
    ).distinct()
    
    for user in users_with_notifications:
        # Skip users without email
        if not user.email:
            continue
            
        # Get all unread notifications for this user that haven't been emailed
        notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            email_sent=False
        ).order_by('-created_at')
        
        if not notifications.exists():
            continue
            
        # Count notifications by type
        notification_count = notifications.count()
        message_count = notifications.filter(notification_type='message').count()
        claim_request_count = notifications.filter(notification_type='claim_request').count()
        claim_approved_count = notifications.filter(notification_type='claim_approved').count()
        claim_rejected_count = notifications.filter(notification_type='claim_rejected').count()
        mention_count = notifications.filter(notification_type='mention').count()
        system_count = notifications.filter(notification_type='system').count()
        
        # Create email subject
        subject = f"Linkyoh: You have {notification_count} new notifications"
        
        # Prepare context
        context = {
            'user': user,
            'notification_count': notification_count,
            'message_count': message_count,
            'claim_request_count': claim_request_count,
            'claim_approved_count': claim_approved_count,
            'claim_rejected_count': claim_rejected_count,
            'mention_count': mention_count,
            'system_count': system_count,
            'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000',
            'protocol': 'https' if not settings.DEBUG else 'http',
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        # Send the email
        success = send_email_task(
            subject=subject,
            template_html='emails/notification_email.html',
            template_txt='emails/notification_email.txt',
            context=context,
            recipient_list=[user.email]
        )
        
        if success:
            # Mark notifications as emailed
            notifications.update(email_sent=True)
            logger.info(f"Sent notification email to {user.email} with {notification_count} notifications")


@shared_task
def cleanup_old_notifications():
    """
    Task to clean up old read notifications to prevent database bloat.
    """
    # Delete read notifications older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    old_notifications = Notification.objects.filter(
        is_read=True,
        updated_at__lt=cutoff_date
    )
    
    count = old_notifications.count()
    old_notifications.delete()
    
    logger.info(f"Deleted {count} old read notifications")