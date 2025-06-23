# Email Setup for Linkyoh

This document provides instructions for setting up and using the email functionality in the Linkyoh application.

## Overview

The Linkyoh application now supports sending emails for:
- Welcome emails to new users
- Password reset confirmation emails
- (Additional email types can be added as needed)

Emails are sent asynchronously using Celery and RabbitMQ to ensure that the application remains responsive even when sending many emails.

## Setup Instructions

### 1. Install Required Packages

The required packages have been added to `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Make sure the following environment variables are set in your `.env` file:

```
# Email Configuration
LYEMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
LYEMAIL_HOST=your-smtp-server.com
LYEMAIL_HOST_USER=your-email@example.com
LYEMAIL_HOST_PASSWORD=your-email-password
LYEMAIL_PORT=587
LYEMAIL_TLS=True
LYEMAIL_SSL=False
LYDEFAULT_EMAIL=noreply@linkyoh.com
LYSEND_TO_EMAIL=support@linkyoh.com

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
```

For development, you can use a service like Mailtrap or a local SMTP server like MailHog.

### 3. Start RabbitMQ and Celery Workers

#### Using Docker Compose

A Docker Compose configuration file (`docker-compose.email.yml`) has been provided to run RabbitMQ and Celery workers:

```bash
docker-compose -f docker-compose.email.yml up -d
```

This will start:
- RabbitMQ server
- Celery worker for processing tasks
- Celery beat for scheduled tasks (if needed)

For detailed instructions on how to integrate the email services with the existing Docker Compose configurations (`docker-compose.app.yml` or `docker-compose.dev.yml`), please refer to the [Docker Email Integration Guide](DOCKER_EMAIL_INTEGRATION.md).

#### Manual Setup

If you prefer to run the services manually:

1. Install and start RabbitMQ:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install rabbitmq-server
   sudo service rabbitmq-server start

   # On macOS with Homebrew
   brew install rabbitmq
   brew services start rabbitmq
   ```

2. Start Celery worker:
   ```bash
   celery -A linkyoh worker -l info
   ```

3. (Optional) Start Celery beat for scheduled tasks:
   ```bash
   celery -A linkyoh beat -l info
   ```

## Email Templates

Email templates are located in:
- HTML templates: `linkyohapp/templates/emails/`
- Text templates: `linkyohapp/templates/emails/`

The following templates are available:
- Welcome email: `welcome_email.html` and `welcome_email.txt`
- Password reset confirmation: `password_reset_confirmation.html` and `password_reset_confirmation.txt`

## Sending Emails

### Using the Email Utility Functions

The application provides utility functions for sending emails:

```python
from linkyohapp.email_utils import send_welcome_email, send_password_reset_confirmation_email

# Send welcome email
send_welcome_email(user, request)

# Send password reset confirmation email
send_password_reset_confirmation_email(user, request)
```

### Creating New Email Types

To create a new email type:

1. Create HTML and text templates in `linkyohapp/templates/emails/`
2. Add a new task in `linkyohapp/tasks.py`
3. Add a new utility function in `linkyohapp/email_utils.py`

## Monitoring

### RabbitMQ Management Interface

The RabbitMQ management interface is available at http://localhost:15672/ (default credentials: guest/guest).

### Celery Flower (Optional)

For more advanced monitoring, you can install and run Celery Flower:

```bash
pip install flower
celery -A linkyoh flower
```

Flower will be available at http://localhost:5555/

## Troubleshooting

### Common Issues

1. **Emails not being sent**:
   - Check that RabbitMQ is running
   - Check that Celery workers are running
   - Check the Celery logs for errors
   - Verify SMTP settings in the environment variables

2. **Connection errors**:
   - Ensure RabbitMQ is accessible at the URL specified in `CELERY_BROKER_URL`
   - Check network connectivity between the application and RabbitMQ

3. **Authentication errors**:
   - Verify SMTP credentials
   - Check if your email provider requires additional security settings

### Logs

Check the following logs for troubleshooting:
- Celery worker logs
- RabbitMQ logs
- Django application logs

## Testing

To test the email functionality:

1. Register a new user to trigger a welcome email
2. Request a password reset and complete the process to trigger a password reset confirmation email

For development, it's recommended to use a service like Mailtrap to capture outgoing emails without actually sending them.
