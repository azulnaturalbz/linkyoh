
import os
dbuser = os.environ['LYDBUSER']
dbpassword = os.environ['LYDB_PASSWORD']
dbname = os.environ['LYDB_NAME']
dbhome = os.environ['LYDB_HOST']
dbport = os.environ['LYDB_PORT']

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

merchant_id = os.environ['LYLYMERCHANT_ID']
public_key = os.environ['LYMERCHANT_PUBLIC']
private_key = os.environ['LYMERCHANT_PRIVATE']
