# settings_nester.py
DEBUG = False
ALLOWED_HOSTS = ['*']  # Or specific IP of the nester VM

# API configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Alert configuration
ALERT_EMAIL = 'support@nfl-it.com'
ALERT_THRESHOLD = 300  # 5 minutes without heartbeat before alerting