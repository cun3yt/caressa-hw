from os import getenv

ENV = getenv('ENV')

possible_envs = ['test', 'dev', 'stage', 'prod', ]

if ENV not in possible_envs:
    raise Exception("ENV environment variable must be set. "
                    "Possible values: {}".format(', '.join(possible_envs)))

twilio_account_sid = getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = getenv('TWILIO_AUTH_TOKEN')

PUSHER_KEY_ID = getenv('PUSHER_KEY_ID')
PUSHER_SECRET = getenv('PUSHER_SECRET')
PUSHER_CLUSTER = getenv('PUSHER_CLUSTER')

SUBDOMAIN = getenv('WEB_SUBDOMAIN')

USER_ACTIVITY_LOG = "{server}/api/user-activity-log/".format(server=SUBDOMAIN)

DATETIME_TZ_FORMAT = '%Y-%m-%d %H:%M:%S%z'
# todo: Decide on asserting being non-null existence or full operation of some of the services here.
# todo Should we unify all time related variables to epoch!
