
import os
dbuser = os.environ['DBUSER']
dbpassword = os.environ['DB_PASSWORD']
dbname = os.environ['DB_NAME']
dbhome = os.environ['DB_HOST']
dbport = os.environ['DB_PORT']

EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_USE_TLS = os.environ['EMAIL_TLS']
EMAIL_USE_SSL =os.environ['EMAIL_SSL']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_EMAIL']
SEND_TO_EMAIL = os.environ['SEND_TO_EMAIL']

SOCIAL_AUTH_FACEBOOK_KEY = os.environ['FB_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ['FB_SECRET']

SECRET_KEY = os.environ['APP_SECRET']

ALLOWED_HOST = os.environ['AH0']
ALLOWED_HOST1 = os.environ['AH1']
ALLOWED_HOST2 = os.environ['AH2']
ALLOWED_HOST3 = os.environ['AH3']

merchant_id = os.environ['MERCHANT_ID']
public_key = os.environ['MERCHANT_PUBLIC']
private_key = os.environ['MERCHANT_PRIVATE']
