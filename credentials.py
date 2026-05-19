import os

# Get deployment mode with a default of 'standalone'
DEPLOYMENT_MODE = os.environ.get('LYDEPLOYMENT_MODE', 'standalone')

DEBUG = os.environ['LYDEBUG'] == 'True'
SSL = os.environ['LYSSL']
DBUSER = os.environ['LYDBUSER']
DBPASSWORD = os.environ['LYDB_PASSWORD']
DBNAME = os.environ['LYDB_NAME']
DBHOME = os.environ['LYDB_HOST']
DBPORT = os.environ['LYDB_PORT']
EMAIL_BACKEND = os.environ['LYEMAIL_BACKEND']
EMAIL_HOST = os.environ['LYEMAIL_HOST']
EMAIL_HOST_USER = os.environ['LYEMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['LYEMAIL_HOST_PASSWORD']
EMAIL_PORT = os.environ['LYEMAIL_PORT']
EMAIL_USE_TLS = os.environ['LYEMAIL_TLS']
EMAIL_USE_SSL =os.environ['LYEMAIL_SSL']
DEFAULT_FROM_EMAIL = os.environ['LYDEFAULT_EMAIL']
SEND_TO_EMAIL = os.environ['LYSEND_TO_EMAIL']
SOCIAL_AUTH_FACEBOOK_KEY = os.environ['LYFB_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ['LYFB_SECRET']
SECRET_KEY = os.environ['LYAPP_SECRET']
ALLOWED_HOST = os.environ['LYAH0']
ALLOWED_HOST1 = os.environ['LYAH1']
ALLOWED_HOST2 = os.environ['LYAH2']
ALLOWED_HOST3 = os.environ['LYAH3']
MERCHANT_ID = os.environ['LYMERCHANT_ID']
PUBLIC_KEY = os.environ['LYMERCHANT_PUBLIC']
PRIVATE_KEY = os.environ['LYMERCHANT_PRIVATE']

# Phone verification settings
PHONE_VERIFICATION_ENABLED = os.environ.get('PHONE_VERIFICATION_ENABLED', 'False') == 'True'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID', '')

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')

# Optional AWS/S3 media storage settings. These are optional so existing VM and
# local deployments can continue using filesystem media.
USE_S3_MEDIA = os.environ.get('LYUSE_S3_MEDIA', 'False') == 'True'
AWS_STORAGE_BUCKET_NAME = os.environ.get('LYAWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = os.environ.get('LYAWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_MEDIA_PREFIX = os.environ.get('LYAWS_S3_MEDIA_PREFIX', 'media')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('LYAWS_S3_CUSTOM_DOMAIN', '')
AWS_QUERYSTRING_AUTH = os.environ.get('LYAWS_QUERYSTRING_AUTH', 'False') == 'True'
CSRF_TRUSTED_ORIGINS = os.environ.get('LYCSRF_TRUSTED_ORIGINS', '')
SECURE_SSL_REDIRECT = os.environ.get('LYSECURE_SSL_REDIRECT', 'False') == 'True'
STATIC_ROOT = os.environ.get('LYSTATIC_ROOT', '')

# Optional API access for trusted import agents. Leave blank to disable API-key
# imports and allow staff-authenticated imports only.
IMPORT_API_KEY = os.environ.get('LYIMPORT_API_KEY', '')
IMPORT_USER_USERNAME = os.environ.get('LYIMPORT_USER_USERNAME', 'linkyoh-ai-admin')
