
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