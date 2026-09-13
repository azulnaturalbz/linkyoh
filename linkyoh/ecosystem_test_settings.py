"""Synthetic-only Phase A verification: never load a production env or database."""

import os

for name in (
    'LYSSL', 'LYDBUSER', 'LYDB_PASSWORD', 'LYDB_NAME', 'LYDB_HOST',
    'LYEMAIL_HOST', 'LYEMAIL_HOST_USER', 'LYEMAIL_HOST_PASSWORD',
    'LYDEFAULT_EMAIL', 'LYSEND_TO_EMAIL', 'LYFB_KEY', 'LYFB_SECRET',
    'LYMERCHANT_ID', 'LYMERCHANT_PUBLIC', 'LYMERCHANT_PRIVATE',
):
    os.environ[name] = ''
for name in ('LYAH0', 'LYAH1', 'LYAH2', 'LYAH3'):
    os.environ[name] = 'localhost'
os.environ.update({
    'LYDEBUG': 'True', 'LYDEPLOYMENT_MODE': 'dev',
    'LYAPP_SECRET': 'synthetic-ecosystem-verification-only',
    'LYDB_PORT': '5432', 'LYEMAIL_PORT': '587',
    'LYEMAIL_TLS': 'False', 'LYEMAIL_SSL': 'False',
    'LYEMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'LYUSE_S3_MEDIA': 'False', 'LYSECURE_SSL_REDIRECT': 'False',
    'LYDIRECTORY_RATE_LIMIT': 'False', 'LYIMPORT_API_KEY': '',
})

from .test_settings import *  # noqa: E402,F401,F403

LOGGING = {'version': 1, 'disable_existing_loggers': False}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
